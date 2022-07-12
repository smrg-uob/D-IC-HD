from overlay import overlay
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d


x_r1, y_r1, z_r1 = overlay.get_rib_1()
x_r2, y_r2, z_r2 = overlay.get_rib_2()
x_d1, y_d1, z_d1 = overlay.get_drill_1()
x_d2, y_d2, z_d2 = overlay.get_drill_2()

fig = plt.figure()
ax = fig.gca(projection='3d', adjustable='box')
ax.plot3D(x_r1, y_r1, z_r1, color="blue")
ax.plot3D(x_r2, y_r2, z_r2, color="blue")
ax.plot3D(x_d1, y_d1, z_d1, color="red")
ax.plot3D(x_d2, y_d2, z_d2, color="red")
plt.show()

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.plot(x_r1, y_r1, color="blue")
ax2.plot(x_r2, y_r2, color="blue")
ax2.plot(x_d1, y_d1, color="red")
ax2.plot(x_d2, y_d2, color="red")

plt.show()
