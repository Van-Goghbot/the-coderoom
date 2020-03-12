import argparse
import struct
import sys
import copy
import time

import rospy
import rospkg

import tf

from gazebo_msgs.srv import (SpawnModel, DeleteModel)
from geometry_msgs.msg import (PoseStamped, Pose, Point, Quaternion)
from std_msgs.msg import (Header, Empty)

from baxter_core_msgs.srv import (SolvePositionIK, SolvePositionIKRequest)

import baxter_interface
import csv
import listener
import bezier_interpolation
import simulation

from sensor_msgs.msg import Range

def callback_left(msg):
    #Setup listener to feed back IR range of left arm
    global left_arm_range
    left_arm_range = msg.range

def callback_right(msg):
    #Setup listener to feed back IR range of right arm
    global right_arm_range
    right_arm_range = msg.range

def move(arm,x,y,z,r,p,ya,pnp):
    #Move to a given point using cartesian coordinates and euler angles
    quat = tf.transformations.quaternion_from_euler(r,p,ya)

    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.x = quat[0]
    pose.orientation.y = quat[1]
    pose.orientation.z = quat[2]
    pose.orientation.w = quat[3]

    #Use the provided servo_to_pose function to move the corresponding arm
    if arm == 'l':
        pnp._servo_to_pose(pose)
    elif arm == 'r':
        pnp._servo_to_pose(pose)
    return x,y,z,r,p,ya

def safe_point_r(pnp):
    #Function to return arms to a safe tucked position
    right_joint_angles = {'right_s0': -0.2823,
                  'right_s1': -1.13965,
                  'right_e0': 1.0771,
                  'right_e1': 1.08657,
                  'right_w0': -0.387,
                  'right_w1': 1.8194,
                  'right_w2': -1.7079
                  }
    pnp._guarded_move_to_joint_position(right_joint_angles)
    print ("Moved to safe point")

def safe_point_l(pnp):
    #Function to return arms to tucked position    
    left_joint_angles = {'left_s0': -0.5929,
                 'left_s1': -1.3422,
                 'left_e0': 0.3146,
                 'left_e1': 1.3544,
                 'left_w0': 3.059-3.14,
                 'left_w1': 1.5702,
                 'left_w2': -1.072
                 }
    pnp._guarded_move_to_joint_position(left_joint_angles)
    print ("Moved to safe point")

def place(x,y,z,r,p,ya,height,arm,pnp):
    #Place bricks at the specified coordinate
    print ("Placing with {0} arm".format(str(arm)))
    move(arm,x,y,z+height,r,p,ya,pnp) #Move to a hover point
    move(arm,x,y,z,r,p,ya,pnp) #Lower to place point
    if arm == 'l':
        pnp.gripper_open() #Release brick
        rospy.sleep(0.1) #Pause to let brick settle
    if arm == 'r':
        pnp.gripper_open()
        rospy.sleep(0.1)
    move(arm,x,y,z+height,r,p,ya,pnp) #Move back to hover point

    #Move back to a safe point
    if arm == 'l':
        brick_place('l',-0.5929,-1.3422,0.3146,1.3544,3.059-3.14,1.5702,-1.072,pnp)
    if arm == 'r':
        brick_place('r',-0.2823,-1.13965,1.0771,1.08657,-0.387,1.8194,-1.7079,pnp)
    return x,y,z+height,r,p,ya

def pick(arm,pnp,movement_count,sim):
    #Function to pick up a brick with a given arm from a set position

    #Take IR ranges from callback functions
    global left_arm_range
    global right_arm_range

    #Setup subscribers to update left and right arm ranges
    rospy.Subscriber("/robot/range/left_hand_range/state",Range,callback_left,queue_size = 1)
    time.sleep(0.5) #Pause to make sure the subscriber has time to retrieve latest values
    rospy.Subscriber("/robot/range/right_hand_range/state",Range,callback_right,queue_size = 1)
    time.sleep(0.5)

    if arm == 'l':
        print ("Picking with left arm")

        #Move to picking point
        brick_place('l',1.045,-1.2174,-0.5546,1.8941,1.5558,-1.2412,-0.9172,pnp)
        pnp.gripper_open()
        #Recieve brick
        coord = move('l',0.6,0.8,0.5,0,3.14/2,0,pnp)

        #Wait until there is a brick in the gripper
        if sim != True:
            while left_arm_range > 0.6:
                rospy.sleep(0.1)

        #Load brick in the simulation
        if sim == True:
            spawn_brick(movement_count)

        pnp.gripper_close()

        #Move back to safe point
        brick_place('l',1.045,-1.2174,-0.5546,1.8941,1.5558,-1.2412,-0.9172,pnp)
        brick_place('l',-0.5929,-1.3422,0.3146,1.3544,3.059-3.14,1.5702,-1.072,pnp)

    elif arm == 'r':
        print ("Picking with right arm")

        #Move to picking point
        brick_place('r',-1.032,-1.222,0.5439,1.897,-1.5479,-1.239,0.9162,pnp)
        pnp.gripper_open()
        #Recieve brick
        coord = move('r',0.6,-0.8,0.5,0,3.14/2,0,pnp)

        #Wait until there is a brick in the gripper
        if sim != True:
            while right_arm_range > 0.6:
                rospy.sleep(0.1)

        #Load brick in the simulation
        if sim == True:
            spawn_brick(movement_count)

        pnp.gripper_close()

        #Move back to safe point
        brick_place('r',-1.032,-1.222,0.5439,1.897,-1.5479,-1.239,0.9162,pnp)
        brick_place('r',-0.1652,-1.2395,0.81048,1.1156,-0.2439,1.7843,-0.222,pnp)
        brick_place('r',-0.2823,-1.13965,1.0771,1.08657,-0.387,1.8194,-1.7079,pnp)

def pickandplace(arm,pnp,x,y,z,r,p,ya,height,movement_count,sim):
    #Combined pick and place functions
    pick(arm,pnp,movement_count,sim)
    place(x,y,z,r,p,ya,height,arm,pnp)


def brick_place(arm,s0,s1,e0,e1,w0,w1,w2,pnp):
    #Function to use joint angles to move to point
    if arm == 'l':
        joint_angles = {'left_s0': s0,
                         'left_s1': s1,
                         'left_e0': e0,
                         'left_e1': e1,
                         'left_w0': w0,
                         'left_w1': w1,
                         'left_w2': w2
                         }
        pnp._guarded_move_to_joint_position(joint_angles)
    elif arm == 'r':
        joint_angles = {'right_s0': s0,
                         'right_s1': s1,
                         'right_e0': e0,
                         'right_e1': e1,
                         'right_w0': w0,
                         'right_w1': w1,
                         'right_w2': w2
                         }
        pnp._guarded_move_to_joint_position(joint_angles)

def ik_test(x,y,z,r,p,ya,hover,pnp1,pnp2):
    #Function to test whether a range of coordinates are within workspace
    quat = tf.transformations.quaternion_from_euler(r,p,ya)
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.x = quat[0]
    pose.orientation.y = quat[1]
    pose.orientation.z = quat[2]
    pose.orientation.w = quat[3]

    #Specify second pose to test hover point
    pose2 = Pose()
    pose2.position.x = x
    pose2.position.y = y
    pose2.position.z = z + hover
    pose2.orientation.x = quat[0]
    pose2.orientation.y = quat[1]
    pose2.orientation.z = quat[2]
    pose2.orientation.w = quat[3]

    if y <= 0:#Test coordinates on the right side
        #Test with right arm
        limb_joints = pnp1.ik_request(pose)
        limb_joints_up = pnp1.ik_request(pose2)
        if limb_joints == False or limb_joints_up == False:
            #If right arm fails, try with left
            print ("Right arm failed")
            limb_joints = pnp2.ik_request(pose)
            limb_joints_up = pnp2.ik_request(pose2)
            if limb_joints_up == False or limb_joints_up == False:
                print ("FAILED COORDINATE")
            else:
                print ("SUCCESSFUL COORDINATE")
                pass
        else:
            print ("SUCCESSFUL COORDINATE")
            pass

    elif y >= 0: #Test coordinates on the left side
        #Test with left arm
        limb_joints = pnp2.ik_request(pose)
        limb_joints_up = pnp2.ik_request(pose2)
        if limb_joints == False or limb_joints_up == False:
            #If left arm fails, try with right
            print ("Left arm failed")
            limb_joints = pnp1.ik_request(pose)
            limb_joints_up = pnp1.ik_request(pose2)
            if limb_joints == False or limb_joints_up == False:
                print ("FAILED COORDINATE")
            else:
                print ("SUCCESSFUL COORDINATE")
                pass
        else:
            print ("SUCCESSFUL COORDINATE")
            pass

    return limb_joints,limb_joints_up

def spawn_brick(movement_count):
    #Load the relevant brick depending on what stage we are at
    if movement_count == 1:
        simulation.load_brick1()
    elif movement_count == 2:
        simulation.load_brick2()
    elif movement_count == 3:
        simulation.load_brick3()
    elif movement_count == 4:
        simulation.load_brick4()
    elif movement_count == 5:
        simulation.load_brick5()
    elif movement_count == 6:
        simulation.load_brick6()
    elif movement_count == 7:
        simulation.load_brick7()
    elif movement_count == 8:
        simulation.load_brick8()
