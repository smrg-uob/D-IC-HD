from overlay import overlay
from matplotlib import pyplot as plt


x, y, z = overlay.get_rib(1000, 2)

fig = plt.figure()
ax = fig.gca(projection='3d', adjustable='box')
ax.scatter3D(x, y, z)

plt.show()
