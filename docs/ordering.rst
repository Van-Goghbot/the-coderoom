Ordering
====================
Overview
--------------------
(EDIT)

Code Overview
--------------------
The code for ordering code is relatively simple, we first need to divide the coordinate list into coordinates covered by the left arm and those covered by the right.
::
    for brick in coords:
        if brick.x <= 0:
            right.append((float(brick.x), float(brick.y), float(brick.rot)))
        else:
            left.append((float(brick.x), float(brick.y), float(brick.rot)))
::

Both lists need to be sorted into ascending order, the right list is then reversed, arranging the both sets of coordinates around 0.
::
    right.sort()
    right = right[::-1]
    left.sort()
::
.. figure::  imgs/ordering.png
   :align:   center
