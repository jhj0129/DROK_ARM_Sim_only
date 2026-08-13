from setuptools import setup
from glob import glob
import os
package_name='drok_arm_mujoco'
setup(name=package_name,version='0.1.0',packages=[package_name],data_files=[
 ('share/ament_index/resource_index/packages',['resource/'+package_name]),
 ('share/'+package_name,['package.xml']),
 ('share/'+package_name+'/config',glob('config/*.yaml')),
 ('share/'+package_name+'/model',glob('model/*.xml')),
] + [(os.path.join('share',package_name,os.path.dirname(p)),[p]) for p in glob('model/assets/**/*',recursive=True) if os.path.isfile(p)],
install_requires=['setuptools'],zip_safe=True,maintainer='jhj0129',maintainer_email='jhj0129@example.com',description='DROK ARM MuJoCo simulation hardware backend.',license='Apache-2.0',entry_points={'console_scripts':['mujoco_node = drok_arm_mujoco.mujoco_node:main']})
