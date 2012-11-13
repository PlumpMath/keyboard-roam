keyboard-roam
=============

A Panda3D based program for young children to get feedback from smashing the keyboard

TODO
====

* Make the bunnies follow the terrain
* Use other things besides bunnies
* Jump
* Use Panda 3D physics and gravity to make bunnies move more naturally
* More hidden fun stuff

BIG CHANGES
===========

2012-11-06 Jeff		Run backward when the down arrow key is pressed.

2012-11-06 Jeff		Make the bunnies line up behind Ralph. This almost
	   		works but math may be off.

2012-11-06 Jeff		Make the bunnies look at Ralph.

2012-11-06 Jeff		Capture all of the non-printable keys.

2012-11-06 Jeff		Get sounds from http://www.freesound.org
	   		Implement "running" sound.
			Implement "bump" sound.
			Implement "spawn" sound."

2012-11-10 Jeff		Divided the keyboard into sections, and bound each
	   		section to an action:

			- Camera left
			- Camera right
			- Move forward
			- Move backward
			- Spawn a new bunny
			- Move or rotate (arrow keys)