from onrobot_sg import SG

gripper_obj = SG('192.168.8.179', 502)
step = 50  # step for moving the gripper
target_width = gripper_obj.get_gp_wd() + (5 * step)
gripper_obj.set_target(target_width)
