Improvements
======================
Increased workspace
----------------------
DE-NIRO has a very large reachable workspace, which was one of the reasons we chose to use it. In our demonstrations, we only used a fraction of that potential workspace. A simple future improvement would be adding more tables to allow for longer, more exciting paths.

.. figure::  imgs/workspace.png
   :align:   center
   
This would be achieved through adding extra waypoints for the bezier to intersect with; allowing for even more interesting paths.

Multi-threading
----------------------
Whilst our use of the subprocess module was successful in practice, much of the debugging is clunky and overly complicated. The use of multi-threading may be beneficial to the improvement of our implementation.
