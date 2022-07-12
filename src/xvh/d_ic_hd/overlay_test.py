from overlay import overlay
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d


x, y, z = overlay.get_overlay()

fig = plt.figure()
ax = fig.gca(projection='3d', adjustable='box')
ax.scatter3D(x, y, z)

plt.show()

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
x1, y1, z1 = overlay.get_rib_1()
ax2.plot(x1, y1, color="blue")
x2, y2, z2 = overlay.get_rib_2()
ax2.plot(x2, y2, color="blue")

plt.show()
