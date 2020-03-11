.. toctree::
   :maxdepth: 2

Bezier Curve
============
In developing the placing sequence, the group implemented an SVG code to dynamically place each brick after the pick sequence. The SVG uses a bezier curve with two handles; the curvature of the SVG is determined by the length of the handles.

.. literalinclude:: dominoes_code/bezier_conversion.py
   :language: python
   :start-after: self.y = y
   :end-before: def conversion
   :linenos:
   

T - Space vs Cartesean Space
----------------------------
Beziers work by converting a value from 0 and 1 into x and y coordinates. They're defined by 4 control points.
[insert image of control points]

These control points are used in the following equation:


Representing a Bezier in Code
-----------------------------

The Bezier Class
^^^^^^^^^^^^^^^^



Creating a Bezier from the Start and End Bricks
-----------------------------------------------

Evenly Spacing the Bricks
-------------------------

Approximating the Length of a Bezier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Utilizing Memoisation to Improve Efficiency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Converting Distance Along Path to Catesean Coordinates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Rotating the Bricks to be Normal to the Path
---------------------------------------------
Calculating Tangent Line
^^^^^^^^^^^^^^^^^^^^^^^^

Converting to Rotation
^^^^^^^^^^^^^^^^^^^^^^

