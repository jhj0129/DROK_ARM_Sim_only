#!/usr/bin/env python3
import os, threading, time
from pathlib import Path
import numpy as np
import yaml
import mujoco
import mujoco.viewer
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool
from control_msgs.action import FollowJointTrajectory, GripperCommand
from ament_index_python.packages import get_package_share_directory

ARM_JOINTS = [f"JOINT{i}" for i in range(1, 7)]
ALL_FEEDBACK_JOINTS = ARM_JOINTS + ["JOINT7"]

class DrokMujocoNode(Node):
    def __init__(self, model, data, cfg):
        super().__init__('drok_arm_mujoco')
        self.model, self.data, self.cfg = model, data, cfg
        self.lock = threading.RLock()
        self.arm_act = {n: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in ARM_JOINTS}
        self.joint_ids = {n: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, n) for n in ALL_FEEDBACK_JOINTS}
        self.qpos_adr = {n: model.jnt_qposadr[jid] for n,jid in self.joint_ids.items()}
        self.dof_adr = {n: model.jnt_dofadr[jid] for n,jid in self.joint_ids.items()}
        self.grip_act_l = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, 'JOINT7')
        self.grip_act_r = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, 'GRIPPER_RIGHT_JOINT')
        self.right_joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, 'GRIPPER_RIGHT_JOINT')
        self.right_qpos_adr = model.jnt_qposadr[self.right_joint_id]
        self.command_open = float(cfg['gripper_interface']['command_open'])
        self.command_close = float(cfg['gripper_interface']['command_close'])
        self.j7_open = float(cfg['gripper_interface']['joint7_open_m'])
        self.j7_close = float(cfg['gripper_interface']['joint7_close_m'])
        self.pub = self.create_publisher(JointState, '/joint_states', 20)
        self.ready_pub = self.create_publisher(Bool, '/drok_arm/sim_ready', 1)
        self.direct_sub = self.create_subscription(JointState, '/drok_arm/joint_command', self.direct_cb, 10)
        self.arm_server = ActionServer(self, FollowJointTrajectory, '/arm_controller/follow_joint_trajectory', execute_callback=self.arm_execute, goal_callback=self.goal_cb, cancel_callback=self.cancel_cb)
        self.gripper_server = ActionServer(self, GripperCommand, '/gripper_controller/gripper_cmd', execute_callback=self.gripper_execute, goal_callback=self.goal_cb, cancel_callback=self.cancel_cb)
        self.publish_period = 1.0 / float(cfg['sim']['publish_rate_hz'])
        self.last_pub = 0.0
        self._apply_home()
        self.get_logger().info('SIM backend ready')
        self.get_logger().info('Action: /arm_controller/follow_joint_trajectory')
        self.get_logger().info('Action: /gripper_controller/gripper_cmd')
        self.get_logger().info('Direct: /drok_arm/joint_command')
        self.get_logger().info('Feedback: /joint_states')

    def _apply_home(self):
        with self.lock:
            for n in ARM_JOINTS:
                q=float(self.cfg['home_q'][n]); self.data.qpos[self.qpos_adr[n]]=q; self.data.ctrl[self.arm_act[n]]=q
            self.data.qpos[self.qpos_adr['JOINT7']] = self.j7_open
            self.data.qpos[self.right_qpos_adr] = -self.j7_open
            self.data.ctrl[self.grip_act_l]=self.j7_open; self.data.ctrl[self.grip_act_r]=-self.j7_open
            mujoco.mj_forward(self.model,self.data)

    def goal_cb(self,_): return GoalResponse.ACCEPT
    def cancel_cb(self,_): return CancelResponse.ACCEPT

    def direct_cb(self,msg):
        pos={n:p for n,p in zip(msg.name,msg.position)}
        with self.lock:
            for n in ARM_JOINTS:
                if n in pos: self.data.ctrl[self.arm_act[n]]=float(pos[n])
            if 'JOINT7' in pos:
                q=max(self.j7_open,min(self.j7_close,float(pos['JOINT7'])))
                self.data.ctrl[self.grip_act_l]=q; self.data.ctrl[self.grip_act_r]=-q

    @staticmethod
    def _t(point): return point.time_from_start.sec + point.time_from_start.nanosec*1e-9

    def arm_execute(self,gh):
        traj=gh.request.trajectory
        result=FollowJointTrajectory.Result()
        missing=[n for n in ARM_JOINTS if n not in traj.joint_names]
        if not traj.points or missing:
            gh.abort(); result.error_code=result.INVALID_GOAL; result.error_string=f'missing joints: {missing}'; return result
        idx={n:traj.joint_names.index(n) for n in ARM_JOINTS}
        t0=time.monotonic()
        for pt in traj.points:
            if gh.is_cancel_requested:
                gh.canceled(); result.error_code=result.SUCCESSFUL; result.error_string='cancelled'; return result
            wait=t0+self._t(pt)-time.monotonic()
            if wait>0: time.sleep(wait)
            with self.lock:
                for n in ARM_JOINTS: self.data.ctrl[self.arm_act[n]]=float(pt.positions[idx[n]])
        gh.succeed(); result.error_code=result.SUCCESSFUL; result.error_string='success'; return result

    def gripper_execute(self,gh):
        result=GripperCommand.Result(); qcmd=float(gh.request.command.position)
        lo=min(self.command_open,self.command_close); hi=max(self.command_open,self.command_close); qcmd=max(lo,min(hi,qcmd))
        ratio=(qcmd-self.command_open)/(self.command_close-self.command_open)
        j7=self.j7_open+ratio*(self.j7_close-self.j7_open)
        with self.lock:
            self.data.ctrl[self.grip_act_l]=j7; self.data.ctrl[self.grip_act_r]=-j7
        time.sleep(0.25)
        gh.succeed(); result.position=qcmd; result.effort=0.0; result.stalled=False; result.reached_goal=True; return result

    def publish_feedback_if_due(self):
        now=time.monotonic()
        if now-self.last_pub < self.publish_period: return
        self.last_pub=now
        m=JointState(); m.header.stamp=self.get_clock().now().to_msg(); m.name=list(ALL_FEEDBACK_JOINTS)
        with self.lock:
            m.position=[float(self.data.qpos[self.qpos_adr[n]]) for n in ALL_FEEDBACK_JOINTS]
            m.velocity=[float(self.data.qvel[self.dof_adr[n]]) for n in ALL_FEEDBACK_JOINTS]
        self.pub.publish(m); b=Bool(); b.data=True; self.ready_pub.publish(b)

def main():
    rclpy.init()
    share=Path(get_package_share_directory('drok_arm_mujoco'))
    cfg=yaml.safe_load((share/'config'/'sim.yaml').read_text())
    model=mujoco.MjModel.from_xml_path(str(share/'model'/'drok_arm.xml')); data=mujoco.MjData(model)
    node=DrokMujocoNode(model,data,cfg)
    ex=MultiThreadedExecutor(num_threads=3); ex.add_node(node)
    th=threading.Thread(target=ex.spin,daemon=True); th.start()
    dt=float(cfg['sim']['timestep']); realtime=bool(cfg['sim'].get('realtime',True))
    try:
        with mujoco.viewer.launch_passive(model,data) as viewer:
            while rclpy.ok() and viewer.is_running():
                tick=time.monotonic()
                with node.lock: mujoco.mj_step(model,data)
                node.publish_feedback_if_due(); viewer.sync()
                if realtime:
                    remain=dt-(time.monotonic()-tick)
                    if remain>0: time.sleep(remain)
    finally:
        ex.shutdown(); node.destroy_node(); rclpy.shutdown()
if __name__=='__main__': main()
