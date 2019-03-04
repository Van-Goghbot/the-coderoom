#!/usr/bin/env python
import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import tf
import geometry_msgs.msg
from math import pi
from std_msgs.msg import String, Float64
from moveit_commander.conversions import pose_to_list
from de_msgs.srv import QueryBrickLoc, QueryBrickLocResponse
from samrowan import SamRowan
# from keith_code import *

# Provides the goal location queries.

rospy.init_node('brick_manager_server')


#Create Classes to Manager Goal and Brick Stack Location

GoalManager = SamRowan(5,4)

def brick_manager_server(req):
    #num = req.num #change req to req.num to do placed iteration thing
    resp = QueryBrickLocResponse()
    p = [0.5, 0.5, 0.18, 3.14, 0, 3.14/4] # z+0.2?
    resp.x = p[0]
    resp.y = p[1]
    resp.z = p[2]
    resp.wx = p[3]
    resp.wy = p[4]
    resp.wz = p[5]
    return p


def goal_manager_server(req):

    num = req.num

    """
    p = GoalManager.get_next_goal_loc()    #SAM DO CODE AND LOGIC IN HERE
    print("GoalManager P: ", p)

    which_brick = QueryBrickLocRequest()
    print("placed:", which_brick)
    """

inb = input()
i = int(inb)


def test(i):
    if i == 0:
        pos = [0.5, 0.1, 0, 1.5708, 0, 0]
        return pos
    elif i == 1:
        pos = [0.5, 0, 0, 1.5708, 0, 0]
        return pos
    elif i == 2:
        pos = [0.5, -0.1, 0, 1.5708, 0, 0]
        return pos
    else:
        pos = [0.5, 0, 0, 3.1415, 0, 0]
        return pos

#print (test(i))

#########################################################################
###BELOW CODE IS THE ORIGINAL####################
############################################################################
    """if num == 0:
        p = [0.5, 0, 0.05, 3.14, 0, 0]
    elif num == 1:
        p = [0.5, -0.2, 0.05, 3.14, 0, 0]
    elif num == 2:
        p = [0.5, -0.4, 0.05, 3.14, 0, 0]
    elif num == 3:
        p = [0.5, -0.6, 0.05, 3.14, 0, 0]

    elif num == 4:
        p = [0.5, 0, 0.2, 3.14, 0, 0]
    elif num == 5:
        p = [0.5, -0.2, 0.2, 3.14, 0, 0]
    elif num == 6:
        p = [0.5, -0.4, 0.2, 3.14, 0, 0]
    elif num == 7:
        p = [0.5, -0.8, 0.2, 3.14, 0, 0]
    else:
        p = [0.8, 0, 0.2, 3.14, 0, 0]"""

    resp = QueryBrickLocResponse()
    resp.x = p[0]
    resp.y = p[1]
    resp.z = p[2] + 0.15
    resp.wx = p[3]
    resp.wy = p[4]
    resp.wz = p[5] +  3.14/4
    return resp

brick_manager_s = rospy.Service('get_pick_loc', QueryBrickLoc, brick_manager_server)
goal_manager_s = rospy.Service('get_place_loc', QueryBrickLoc, goal_manager_server)

rospy.spin()