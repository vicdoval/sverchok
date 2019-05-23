Line Intersection
=================

Functionality
-------------

The node is designed to get the intersection between two endless lines in space, also provides the distance between the two lines and the point in each line that is closet to the other line.


Inputs / Parameters
-------------------


+------------------+-------------+----------------------------------------------------------------------+
| Param            | Type        | Description                                                          |  
+==================+=============+======================================================================+
| **Verts_Line A** | Vertices    |  It will get the first and last vertices's to define the line segment| 
+------------------+-------------+----------------------------------------------------------------------+
| **Verts_Line B** | Vertices    | It will get the first and last vertices's to define the line segment |
+------------------+-------------+----------------------------------------------------------------------+

Advanced Parameters
-------------------

In the N-Panel you can use the toggle:
 
**Tolerance**: Minimal distance to accept is intersecting.

Outputs
-------

**Distance**: Distance between the lines.

**Intersect**: Returns true if the lines intersect. (Distance < Tolerance)

**Closest Point A**: Returns the closest point to the line B in the line A

**Closest Point B**: Returns the closest point to the line A in the line B


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

