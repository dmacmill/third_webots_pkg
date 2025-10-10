# third_webots_pkg

Attempt at adding lidar this time

1. open webots without ros2. open the world for editing and add a Lidar node to the 
children in my_robot. save by clicking the icon on the screen or ctrl-shift-s

2. add a child shape to the lidar node. set that shapes geometry to cylinder, 
appearance to whatever. 

3. see the lidar vis by setting View > optional rendering > show lidar rays
there are by default 4 lidar ray layers, for 2D lidar we only need 1 so make sure 
to set that.

