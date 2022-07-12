import numpy as np

n_r = 12
r_c = 7.63
p = 2.77
h_r = 0.37


def get_overlay():
    x, y, z = get_rib(1000)
    x1 = x - p/2.0
    x2 = x + p/2.0
    return np.concatenate((x1, x2)), np.concatenate((y, y)), np.concatenate((z, z))


def get_rib_1():
    x, y, z = get_rib(1000)
    return x - p/2.0, y, z


def get_rib_2():
    x, y, z = get_rib(1000)
    return x + p/2.0, y, z


def get_rib(points):
    # Create x, y and z arrays for the ribs
    t = np.arange(-0.5, 0.5, 1.0/points)
    alpha = np.multiply(t, np.pi)
    x = np.multiply(t, p*n_r)
    y = np.multiply(np.sin(alpha), r_c + h_r)
    z = np.multiply(np.cos(alpha), r_c + h_r)
    # Filter for positive z
    z_pos = np.where(z >= 0)
    # Return the coordinates
    return x[z_pos], y[z_pos], z[z_pos]
