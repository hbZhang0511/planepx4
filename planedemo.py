#!/usr/bin/env python3

import rospy
from mavros_msgs.srv import SetMode
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import AttitudeTarget
import matplotlib.pyplot as plt
from mavros_msgs.srv import CommandBool, CommandBoolRequest, SetMode, SetModeRequest

position_data = {'x': [], 'y': [], 'z': []}
#"/mavros/setpoint_raw/attitude"
def arm():
    rospy.wait_for_service("/mavros/cmd/arming")
    arming_client = rospy.ServiceProxy("mavros/cmd/arming", CommandBool)
    arm_cmd = CommandBoolRequest()
    arm_cmd.value = True
    if(arming_client.call(arm_cmd).success == True):
        rospy.loginfo("Vehicle armed")

#pos_pub = None

def state_callback(data):
    global position_data
    position_data['x'].append(data.pose.position.x)
    position_data['y'].append(data.pose.position.y)
    position_data['z'].append(data.pose.position.z)
    #pos_pub.publish(data)
    rospy.loginfo("Current Position: x: %s, y: %s, z: %s", data.pose.position.x, data.pose.position.y, data.pose.position.z)
    
def set_offboard_mode():
    offb_set_mode = SetModeRequest()
    offb_set_mode.custom_mode = 'OFFBOARD'
    rospy.wait_for_service('/mavros/set_mode')
    set_mode = rospy.ServiceProxy('/mavros/set_mode', SetMode)
    if(set_mode.call(offb_set_mode).mode_sent == True):
        rospy.loginfo("OFFBOARD enabled")

def control_loop():
    rospy.init_node('fixedwing_control', anonymous=True)
    pos_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
    vel_pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=10)
    rospy.Subscriber('/mavros/local_position/pose', PoseStamped, state_callback)

    for i in range(100):
        command = PoseStamped()
        # rate_cmd = AttitudeTarget()
        # rate_cmd.type_mask=128
        # rate_cmd.thrust = 0.68
        # rate_cmd.body_rate.x = 0
        command.pose.position.x = 5.0
        command.pose.position.y = 5.0
        command.pose.position.z = 8.0
        pos_pub.publish(command)
        rospy.sleep(0.01) 
        
    set_offboard_mode()
    arm()
    print("end arm")
    rate = rospy.Rate(10)  # 10 Hz

    while not rospy.is_shutdown():
        # 构造一个控制命令
        command = TwistStamped()
        command.twist.linear.x = 5.0  # 设置前进速度
        command.twist.linear.y = 0.0
        command.twist.linear.z = 1.0  # 设置爬升速度
        command.twist.angular.x = 0.0
        command.twist.angular.y = 0.0
        command.twist.angular.z = 0.1  # 设置偏航速度

        vel_pub.publish(command)
        rate.sleep()

if __name__ == '__main__':
    try:
        control_loop()
    except rospy.ROSInterruptException:
        pass
    finally:
        # 在程序结束后绘制曲线
        #if position_data['x']: 
        plt.plot(position_data['x'], label='x')
        plt.plot(position_data['y'], label='y')
        plt.plot(position_data['z'], label='z')
        plt.legend()
        plt.show()
