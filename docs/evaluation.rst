Evaluation
=======================
Overall the project was a huge success for us: we were able to take user inputs and produce a domino path that is always different, avoiding the pre-programmed steps that we thought we would have to use.

There were some slight issues; we wanted to create even more interesting paths, but were somewhat limited by the task space we settled on. The workspace exists for this future change, something we talk about in ``improvements``. There are still some minor glitches when running the task in real-life with bricks slightly misaligning when they are dropped and some issues with redundancy collisions when more extreme angles are used, but our implementation works for the majority of cases. 

The completion speed of the task was satisfactory; the dual-arm usage massively increased the efficiency but there is still space for some minor improvements by eradicating superfluous movement commands. However, for the purposes of the demonstration, these movements avoided redundancies or singularities, so they were deemed necessary for the time being.

Our use of the subprocess module to use both arms was successful, but is somewhat difficult to use. In future, the implementation of multi-threading could be a more optimal solution.

Overall, attempting this ambitious project paid off, with much learnt about ROS, motion planning and kinematics along the way. The outcomes far exceeded our expectations for this project.
