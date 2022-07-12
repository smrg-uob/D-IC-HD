from overlay import overlay
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d


x, y, z = overlay.get_rib(1000)

fig = plt.figure()
ax = fig.gca(projection='3d', adjustable='box')
ax.scatter3D(x, y, z)

plt.show()

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
ax2.plot(x, y)

plt.show()
