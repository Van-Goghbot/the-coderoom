Inverse Kinematics
=====================
Overview
---------------------
If the coordinates are run before checking the inverse, the path may fail halfway through. To avoid this, we check the inverse kinematics for each placing point and the hover point above.

.. figure::  imgs/hover.png
   :align:   center
   
Inverse kinematics check
---------------------
To achieve this, we input the necessary pose and hover distance to check whether there is a feasible set of joint angles.

.. literalinclude:: dominoes_code/right_placement.py
   :language: python
   :dedent: 3
   :lines: 159
   :linenos:
   :lineno-start: 159

Table slant
---------------------
During testing, we found that the bricks wouldn't knock over reliably on a flat surface due to the width of the brick. To counteract this, we instead place the path on a slanted table, allowing the dominoes to be knocked over more easily. We use an adjusted value for z and an incline angle and for the roll so that we can account for the slant of the table. The necessary parameters are set up in ``lines 126-144 of right_placement.py``

.. figure::  imgs/table_height.png
   :align:   center
   
.. literalinclude:: dominoes_code/right_placement.py
   :language: python
   :dedent: 2
   :lines: 130-144
   :linenos:
   :lineno-start: 130
   
IK Test
---------------------
We must first input the coordinates and orientation as a pose:

.. literalinclude:: dominoes_code/domino.py
   :language: python
   :dedent: 1
   :lines: 196-213
   :linenos:
   :lineno-start: 196
   
If the coordinate is on the left side, we want to test that with the left side and visa versa with the right arm. If both arms fail for either the hover or place coordinate, the coordinate fails, and so does the current path. 

.. literalinclude:: dominoes_code/right_placement.py
   :language: python
   :dedent: 3
   :lines: 162-165
   :linenos:
   :lineno-start: 162
   
If the initial path has failed we have to rerun the path with a straighter path. We do this by adjusting the handles from the bezier code to produce a different path in ``right_placement.py lines 202-215:

.. literalinclude:: dominoes_code/right_placement.py
   :language: python
   :dedent: 1
   :lines: 202-215
   :linenos:
   :lineno-start: 202

If this still doesn't work after 10 tries it means even a straight line won't work. We have to break out of the loop and retry with new start and end positions, but this eventuality rarely happens.

.. literalinclude:: dominoes_code/right_placement.py
   :language: python
   :dedent: 2
   :lines: 218-219
   :linenos:
   :lineno-start: 218

If a path does succeed, we can then go on to pick and place the bricks.
