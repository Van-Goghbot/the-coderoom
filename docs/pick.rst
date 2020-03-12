Picking
=======================
Dual arms
-----------------------
The first thing we want to do when we've selected a path is to send the coordinates to both arms so that we can run both arms simultaneously, improving the speed and efficiency of the task.

.. figure::  imgs/deniro_simulated.png
   :align:   center
   
We achieve this by using the subprocess module in Python to run two scripts simultaneously. To give ``left_placement.py`` the working coordinates, we integrate them in the name when it is instantiated:
::
  rc = subprocess.Popen("python left_placement.py '" + str(left) + "'", shell=True)
::
A new node is created and the coordinates can then be interpreted.
::
  def main():
      rospy.init_node("left_arm")
      left_pnp = right_placement.PickAndPlace('left')
      left = [tuple([float(x) for x in y.split(',')]) for y in str(sys.argv[1])[2:-2].split('), (')]
::
Then we can just give the same command to the left and right arms; pick and place the bricks in the specified coordinates.
::
    for coord in right:
        domino.pickandplace('r',right_pnp,coord[1],coord[0],adjusted_z,incline_angle,math.pi,coord[2]+math.pi/2,hover,movement_count)
::
Because we have ordered the coordinates, the only place where the arms may collide is when they are both placing bricks in the centre of the table, at the start of the task. To avoid this, we simply use the ``rospy.sleep`` command to stall the right arm so that the left arm can place and move out of the way beforehand.

Picking
---------------------
  The picking function can be found at ``line 122 in domino.py``
We first want to move the arms to a 'safe point' using joint angles to get to a midpoint which will prevent the arms from getting twisted and thus mitigating redundancies.
::
  brick_place('l',1.045,-1.2174,-0.5546,1.8941,1.5558,-1.2412,-0.9172,pnp)
::
The gripper then opens, and moves forward slightly, ready to recieve a brick. To improve the error detection of the robot, we use the IR sensor on the end effector to determine whether it has been handed a brick.
`Handing DENIRO a brick`_

IR Sensor
---------------------
We achieve this by creating a listener and subscribing to the IR sensor topic for both arms

.. _Handing DENIRO a brick: https://drive.google.com/open?id=1X7xDFg5td2QZFyYkaZnfSWQ3x5a8MqJ3

::
  ..literalinclude:: IR_listener.py
   :lines: 8-20
   
The readings from this topic can then be used within the ``pick`` function to determine whether a brick is in the grippers. 

ADD CODE HERE
--------------------------

Once the grippers close and the brick is secured, the arm returns back to the 'safe point'. ready to place the brick.
