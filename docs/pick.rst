Picking
=======================
Overview
-----------------------
Initially, for the picking motion, we wanted to pick the bricks up from a free-standing position and iterate through. But through testing on the physical robot, we encountered too many issues with redundancies and instead decided to focus on the motion planning for the placement of the bricks. As such, we decided to feed the robot bricks manually which had two benefits: firstly, the user has more of an interaction with the robot rather than just watching it until it finishes, and secondly, feeding the bricks allows for some uncertainty and error to enter the process, allowing for a better test of our project's error detection.

Dual arms
-----------------------
The first thing we want to do when we've selected a path is to send the coordinates to both arms so that we can run both arms simultaneously, improving the speed and efficiency of the task.

.. figure::  imgs/deniro_simulated.png
   :align:   center
   
We achieve this by using the subprocess module in Python to run two scripts simultaneously. To give ``left_placement.py`` the working coordinates, we integrate them as command line arguments:

.. literalinclude:: dominoes_code/right_placement.py
   :language: python
   :dedent: 3
   :lines: 182
   :linenos:
   :lineno-start: 182
   
A new node is created and the coordinates can then be interpreted.

.. literalinclude:: dominoes_code/left_placement.py
   :language: python
   :dedent: 1
   :lines: 30-36
   :linenos:
   :lineno-start: 30
   
Then we can just give the same command to the left and right arms; pick and place the bricks in the specified coordinates.

.. literalinclude:: dominoes_code/left_placement.py
   :language: python
   :dedent: 1
   :lines: 57-62
   :linenos:
   :lineno-start: 57
   
Because we have ordered the coordinates, the only place where the arms may collide is at the start of the task when they are both placing bricks at the centre of the table. To avoid this, we simply use the ``rospy.sleep`` command to stall the right arm so that the left arm can place and move out of the way beforehand.

Picking
---------------------
The picking function can be found at ``line 102 of domino.py``
We first want to move the arms to a 'safe point' using joint angles to get to a midpoint, which will prevent the arms from getting twisted and thus mitigating redundancies.

.. literalinclude:: dominoes_code/domino.py
   :language: python
   :dedent: 2
   :lines: 118-119
   :linenos:
   :lineno-start: 118
   
The gripper then opens and moves forward slightly, ready to receive a brick. To improve the error detection of the robot, we use the IR sensor on the end effector to determine whether it has been handed a brick.
`A video of handing DE-NIRO a brick can be seen here <https://drive.google.com/open?id=1X7xDFg5td2QZFyYkaZnfSWQ3x5a8MqJ3>`_

IR Sensor
---------------------
We achieve this by creating a listener and subscribing to the IR sensor topic for both arms

.. literalinclude:: dominoes_code/domino.py
   :language: python
   :lines: 26-34
   :linenos:
   :lineno-start: 26
   
.. literalinclude:: dominoes_code/domino.py
   :language: python
   :dedent: 1
   :lines: 105-113
   :linenos:
   :lineno-start: 105
   
The readings from this topic can then be used within the ``pick`` function to determine whether a brick is in the grippers. 

.. literalinclude:: dominoes_code/domino.py
   :language: python
   :dedent: 2
   :lines: 124-127
   :linenos:
   :lineno-start: 124

Once the grippers close and the brick is secured, the arm returns back to the 'safe point'. ready to place the brick.
