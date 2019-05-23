Plane Intersection
==================

Functionality
-------------

The node is designed to get the intersection line between two theoretical planes.

Each plane is defined by one point in the plane and plane's normal.


Inputs / Parameters
-------------------


+------------------+-------------+----------------------------------------------------------------------+
| Param            | Type        | Description                                                          |  
+==================+=============+======================================================================+
| **Location A**   | Vertices    | One point of the plane A                                             | 
+------------------+-------------+----------------------------------------------------------------------+
| **Normal A**     | Vertices    | Normal of the plane A                                                |
+------------------+-------------+----------------------------------------------------------------------+
| **Location B**   | Vertices    | One point of the plane B                                             | 
+------------------+-------------+----------------------------------------------------------------------+
| **Normal B**     | Vertices    | Normal of the plane B                                                |
+------------------+-------------+----------------------------------------------------------------------+


Outputs
-------

**Intersect**: Distance to the line.

**Origin**: Returns True if the point is between the input vertices

**Direction**: Returns True if point is in the same plane as with input vertices.

Example of usage
----------------

.. image:: https://user-images.githubusercontent.com/10011941/57584308-0067b580-74da-11e9-966e-fe32cae35d29.png
  :alt: Distance_point_line_procedural.PNG

It can be used to create perpendicular lines from input points

.. image:: https://user-images.githubusercontent.com/10011941/57584321-3147ea80-74da-11e9-8da4-18fc028bcfdd.png
  :alt: Sverchok_Distance_point_line.PNG

Or to select the points in a distance range 

.. image:: https://user-images.githubusercontent.com/10011941/57584309-03fb3c80-74da-11e9-9f90-811731330189.png
  :alt: Blender_distance_point_line.PNG

