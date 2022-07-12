import numpy as np

n_r = 12
r_c = 7.63
p = 2.77
h_r = 0.37
w_d = 0.5
h_d = 5


def get_rib_1():
    x, y, z = get_rib(1000)
    return x - p/2.0, y, z


def get_rib_2():
    x, y, z = get_rib(1000)
    return x + p/2.0, y, z


def get_drill_1():
    x = (p*n_r - w_d)/2.0
    y1 = r_c + h_r
    y2 = r_c + h_r + h_d
    return np.asarray((x, x)), np.asarray((y1, y2)), np.asarray((0, 0))


def get_drill_2():
    x = (p*n_r + w_d)/2.0
    y1 = r_c + h_r
    y2 = r_c + h_r + h_d
    return np.asarray((x, x)), np.asarray((y1, y2)), np.asarray((0, 0))


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
