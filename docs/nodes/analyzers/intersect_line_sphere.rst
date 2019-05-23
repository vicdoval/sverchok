Compas 3D
=========

Functionality
-------------

The node is designed to get the intersection between one sphere and one line segment in space, it also provides the the number of intersections.


Inputs / Parameters
-------------------


+------------------+-----------+----------------------------------------------------------------------+
| Param            | Type      | Description                                                          |  
+==================+===========+======================================================================+
| **Verts_Line A** | Vector    |  It will get the first and last vertices's to define the line segment| 
+------------------+-----------+----------------------------------------------------------------------+
| **Center**       | Vector    | Position of the center of the sphere                                 |
+------------------+-----------+----------------------------------------------------------------------+
| **Radius**       | Float     | Radius of the sphere                                                 |
+------------------+-----------+----------------------------------------------------------------------+


Outputs
-------

**Intersection Num**: Number of intersections (0, 1 or 2).

**Closest Point A**: Returns the intersection point. In case of two intersections it will return the one nearer to the end of the segment, in case of no intersection will return the the point of the sphere witch points is perpendicular to the line.

**Closest Point B**: Returns the intersection point. In case of two intersections it will return the one nearer to the origin of the segment, in case of no intersection will return the the point of the line witch points perpendicular to the origin of the sphere and parallel to the surface of the sphere.


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

