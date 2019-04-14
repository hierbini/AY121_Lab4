import numpy as np
import tool_box as tb
import math

cos = np.cos
sin = np.sin
radians = np.radians

def direction(lat, lon):
    return np.matrix([[cos(lat) * cos(lon), cos(lat) * sin(lon), sin(lat)]])


def GAL_to_EQ_rotation():
    rotation = np.matrix([[-0.054876, -0.873437, -0.483835],
                          [ 0.494109, -0.444830,  0.746982],
                          [-0.867666, -0.198076,  0.455984]])
    return np.linalg.inv(rotation)


def EQ_to_HA_rotation(LST):
    return np.matrix([[cos(LST),  sin(LST), 0],
                      [sin(LST), -cos(LST), 0],
                      [       0,         0, 1]])


def HA_to_CEL_rotation(lat=37.873199):
    return np.matrix([[-sin(lat),  0, cos(lat)],
                      [        0, -1,        0],
                      [ cos(lat),  0, sin(lat)]])


def GAL_to_CEL_rotation(LST, lat):
    rot3, rot2, rot1 = GAL_to_EQ_rotation(), EQ_to_HA_rotation(LST), HA_to_CEL_rotation(lat)
    total_rotation = np.dot(rot1, np.dot(rot2, rot3))
    return total_rotation


def rotate(galactic_coordinates, rotation_matrix):
    """
    Rotates galactic coordinates to the sources coordinates in a different coordinate system.

    Parameters:
    galactic coordinates (tuple): source's galactic coordinates (longitude, latitude)
    rotation matrix (3 by 3 numpy matrix): matrix which rotates coordinates from galactic
    coordinate system to new coordinate system

    Returns:
    new coordinates (tuple): source's coordinates in (latitude, longtiude)
    """
    lon, lat = np.radians(galactic_coordinates[0]), np.radians(galactic_coordinates[1])
    vector = direction(lat, lon)
    coords = np.matmul(rotation_matrix, np.transpose(vector))
    x0, x1, x2 = coords[0], coords[1], coords[2]
    new_lat, new_lon = math.atan(x1 / x0), math.asin(x2)
    return (new_lat, new_lon)