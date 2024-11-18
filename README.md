# Semi-auto-mower

This repository has all files used to build a simple lawn mower prototype.
The mower is built mainly on 3D-printing, DC motors and a Raspberry Pi.

# Directory structure

`cad` contains Solidworks (.SLDPRT) and Fusion (.f3d) files used to design parts.
Parts are also provided as .STL files.

`control` contains (currently) very simple python code for controlling the mower.
Note: the directory `control/RPi` must be removed when running the code on an RPi,
as this is just a placeholder package for running the control code on a normal
computer.
