Distance Point Plane
====================

Functionality
-------------

The node is designed to find the distance between a point and one plane.

The plane is defined by three points.

As extra results you can get from the node:

- If the point is in the triangle.

- If point is in the plane. 

- Closest point in the plane. 

- If the closest point is inside the triangle.

 


Inputs / Parameters
-------------------


+---------------------+-------------+---------------------------------------------------------------------------------------------+
| Param               | Type        | Description                                                                                 |  
+=====================+=============+=============================================================================================+
| **Vertices**        | Vertices    | Points to calculate                                                                         | 
+---------------------+-------------+---------------------------------------------------------------------------------------------+
| **Plane Vertices**  | Vertices    | It will get the first three vertices of the input list to define the triangle and the plane |
+---------------------+-------------+---------------------------------------------------------------------------------------------+

Advanced Parameters
-------------------

In the N-Panel you can use the toggle:

**Tolerance**: Minimal distance to accept is intersecting.
 
**Implementation**: Choose between MathUtils and NumPy (Usually faster)

**Output NumPy**: Get NumPy arrays in stead of regular lists (makes the node faster). Only in the NumPy implementation.

**Match List**: Define how list with different lengths should be matched.

Outputs
-------

**Distance**: Distance to the line.

**In Triangle**: Returns True if the point  coplanar and inside the triangle formed by the input vertices

**In Plane**: Returns True if point is in the same plane as with input vertices.

**Closest Point**: Returns the closest point in the plane

**Closest in Triangle**": Returns true if the closest point is is in the same plane as with input vertices.


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

