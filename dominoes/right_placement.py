import argparse
import struct
import sys
import copy

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
import domino
import subprocess
import simulation
import math

class arm(object):
    #This class was adapted from pick_and_place.py from the 'Controlling DE-NIRO via Python code' tutorial
    def __init__(self, limb, verbose=True):
        self._limb_name = limb # string
        self._verbose = verbose # bool
        self._limb = baxter_interface.Limb(limb)
        self._gripper = baxter_interface.Gripper(limb)
        ns = "ExternalTools/" + limb + "/PositionKinematicsNode/IKService"
        self._iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
        rospy.wait_for_service(ns, 5.0)
        # verify robot is enabled
        print("Getting robot state... ")
        self._rs = baxter_interface.RobotEnable(baxter_interface.CHECK_VERSION)
        self._init_state = self._rs.state().enabled
        print("Enabling robot... ")
        self._rs.enable()

    def move_to_start(self, start_angles=None):
        print("Moving the {0} arm to pose...".format(self._limb_name))
        if not start_angles:
            start_angles = dict(zip(self._joint_names, [0]*7))
        self._guarded_move_to_joint_position(start_angles)
        rospy.sleep(1.0)

    def ik_request(self, pose):
        hdr = Header(stamp=rospy.Time.now(), frame_id='base')
        ikreq = SolvePositionIKRequest()
        ikreq.pose_stamp.append(PoseStamped(header=hdr, pose=pose))
        try:
            resp = self._iksvc(ikreq)
        except (rospy.ServiceException, rospy.ROSException), e:
            rospy.logerr("Service call failed: %s" % (e,))
            return False
        # Check if result valid, and type of seed ultimately used to get solution
        # convert rospy's string representation of uint8[]'s to int's
        resp_seeds = struct.unpack('<%dB' % len(resp.result_type), resp.result_type)
        limb_joints = {}
        if (resp_seeds[0] != resp.RESULT_INVALID):
            seed_str = {
                        ikreq.SEED_USER: 'User Provided Seed',
                        ikreq.SEED_CURRENT: 'Current Joint Angles',
                        ikreq.SEED_NS_MAP: 'Nullspace Setpoints',
                       }.get(resp_seeds[0], 'None')
            # Format solution into Limb API-compatible dictionary
            limb_joints = dict(zip(resp.joints[0].name, resp.joints[0].position))
        else:
            rospy.logerr("INVALID POSE - No Valid Joint Solution Found.")
            return False
        return limb_joints

    def _guarded_move_to_joint_position(self, joint_angles):
        if joint_angles:
            self._limb.move_to_joint_positions(joint_angles)
        else:
            rospy.logerr("No Joint Angles provided for move_to_joint_positions. Staying put.")

    def gripper_open(self):
        self._gripper.open()

    def gripper_close(self):
        self._gripper.close()

    def _servo_to_pose(self, pose):
        # servo down to release
        joint_angles = self.ik_request(pose)
        #print (joint_angles)
        self._guarded_move_to_joint_position(joint_angles)

def main():
    rospy.init_node("right_arm") #Initiate a node to control computation for the right arm

    mode_sim = True #Change depending on whether running simulation or not

     #Initialise an instance of the arm class for both arms
    right_pnp = arm('right')
    left_test = arm('left')

    #Move both arms to a midpoint using joint angles
    domino.safe_point_r(right_pnp)
    domino.safe_point_l(left_test)

    #Get coordinates from the user by creating
    translations, angles = listener.get_coordinates()
    start_x = translations[0][0] * 100 + 60
    start_y = (translations[0][1] + 0.1) * -100 + 120
    start_angle = angles[0][2] - math.pi/2
    end_x = translations[1][0] * 100 + 60
    end_y = (translations[1][1] + 0.1) * -100 + 120
    end_angle = angles[1][2] + math.pi/2
    print start_x, start_y, ((math.pi) - start_angle)
    print end_x, end_y, ((math.pi) + end_angle)

    #Get Bezier coordinates for a path
    if mode_sim == True:
        coords = bezier_interpolation.create_path(10, 35, -math.pi/8, 110, 40, math.pi/8, 110)
    else:
        coords = bezier_interpolation.create_path(start_x, start_y, start_angle, end_x, end_y, end_angle, 110)

    def run_pnp(coords):

        check_list = [] #For checking whether a path succeeds
        right = [] #Coordinates for right arm
        left = [] #Coordinates for left arm

        #Setup variables
        table_height = 0.24
        hover = 0.1

        #Setup variables for height adjustment
        table_length = 160 #160cm
        table_reach = table_length/2 #Each arm only uses half the table
        relaive_table_length = 0.6 #Maximum y-distance travelled in gazebo by arm
        scale_factor = table_reach/relaive_table_length #Scaling factor
        scale_difference = 317.4 #Conversion between gazebo and millimetres

        raised_height = 79 #Table height in mm (raised side)
        lowered_height = 72
        height_difference = raised_height - lowered_height
        incline_angle = float(math.tan(height_difference/table_length))

        #For each brick check inverse kinematics of placement
        for brick in coords:
            print("brick")
            print float(brick.y), float(brick.x), float(brick.rot)
            if brick.x <= 0: #Split coordinates based on whether they are on the right or left side
                right.append((float(brick.x), float(brick.y), float(brick.rot)))
            else:
                left.append((float(brick.x), float(brick.y), float(brick.rot)))

            #Adjust coordinates to account for slant of table
            adjusted_z = table_height + ((float(brick.y)+relaive_table_length)*scale_factor*incline_angle)/scale_difference

            #Check whether inverse kinematics for each point on a path
            error_check = domino.ik_test(round(brick.y, 3),round(brick.x, 3),adjusted_z,incline_angle,math.pi,brick.rot,hover,right_pnp,left_test)

            #Flag if any of the coordinates on the path fail
            if error_check[0] == False:
                check_list.append(error_check[0])
            if error_check[1] == False:
                check_list.append(error_check[1])

        if len(check_list) > 0:
            print ("Failed Path")
        else:
            print("Succesful Path")

            #Order the coordinates
            right.sort()
            right = right[::-1]
            left.sort()

            #Load table model
            if mode_sim == True:
                simulation.load_table()

            #Call function to run the left arm simultaneously, feed the succesful coordinates to the subprocess by inputting them as command line arguments
            rc = subprocess.Popen("python left_placement.py '" + str(left) + "'", shell=True)
            rospy.sleep(10) #Pause to avoid coliision with the left arm

            movement_count = 0 #Count how many moves have been made (To load bricks in simulation)

            for coord in right:
                movement_count += 2

                #Call function to pick and place bricks at a specific coordinate
                adjusted_z = table_height + ((float(brick.y)+0.6)*scale_factor*incline_angle)/scale_difference
                domino.pickandplace('r',right_pnp,coord[1],coord[0],adjusted_z,incline_angle,math.pi,coord[2]+math.pi/2,hover,movement_count,mode_sim)
        return check_list

    check_list = run_pnp(coords) #Check the first path

    run_number = 0 #How many paths have been checked

    influence = 110 #Handle influence (affects curvature of path)

    #If the first run failed, rerun
    while len(check_list) > 0:
        influence -= 10 #Decrease to straighten path
        run_number += 1
        print("")
        print("Run number {0} failed".format(str(run_number)))

        #Create a new path
        if mode_sim == True:
            coords = bezier_interpolation.create_path(10, 35, -3.14/8, 110, 40, 3.14/8, influence)
        else:
            coords = bezier_interpolation.create_path(start_x, start_y, start_angle, end_x, end_y, end_angle, influence)

        #Rerun with the new, straighter path
        check_list = run_pnp(coords)

        #After 10 iterations the path is straight, break if it still doesn't work
        if run_number >= 10:
            break

    if mode_sim == True:
        simulation.delete_gazebo_models()

if __name__ == '__main__':
    sys.exit(main())
