import numpy as np

n_r = 12
r_c = 7.63
p = 2.77
h_r = 0.37


def get_rib(points, pitches):
    # Create x, y and z arrays for the ribs
    t = np.arange(0, 1, (pitches + 0.0)/(0.0 + 2*points))
    alpha = np.multiply(t, 2*np.pi*pitches/n_r)
    x = np.multiply(t, pitches)
    y = np.multiply(np.cos(alpha), r_c + h_r)
    z = np.multiply(np.sin(alpha), r_c + h_r)
    # Filter for positive z
    z_pos = np.where(z >= 0)
    # Return the coordinates
    return x[z_pos], y[z_pos], z[z_pos]