import bisect

### VECTOR FUNCTIONS ######################################################################################################

def make_vector(x, y):
    return np.array([x, y])


def get_magnitude(coords):
    x = get_x(coords)
    y = get_y(coords)
    return np.sqrt(x**2 + y**2)


def get_x(coords):
    return coords[0]


def get_y(coords):
    return coords[1]

### VALUES ################################################################################################################

def kpc_to_km(kpc):
    return kpc * 3.086e16

def km_to_kpc(km):
    return km / 3.086e16

GALACTIC_VELOCITY = 220
DEGREE_SPACING = 2
LONGITUDE_RANGE = np.linspace(-10, 250, (250 + 10) / DEGREE_SPACING)
GRID_EDGE = kpc_to_km(10) # 10 kpc

SUN_COORDS = make_vector(0, kpc_to_km(8.5)) # kpc
SUN_VELOCITY = make_vector(GALACTIC_VELOCITY, 0)

### MAP FUCNTIONS #########################################################################################################


def create_xy_coordinates(length):
    x_axis = np.linspace(-GRID_EDGE, GRID_EDGE, length) # kpc
    y_axis = np.linspace(-GRID_EDGE, GRID_EDGE, length) # kpc
    coords = []
    for x in range(length):
        for y in range(length):
            coords.append(make_vector(x_axis[x], y_axis[y]))
    return x_axis, y_axis, coords


def find_l_file(dr):
    """
    Finds the file with galactic longitude closest to l calculated from theta
    """
    l_file = list(LONGITUDE_RANGE)
    l_theta = 180 - 90 - np.arctan(get_x(dr) / get_y(dr))
    i = bisect.bisect_left(l_file, l_theta)
    if (l_file[i] - l_theta) < (l_file[i-1] - l_theta):
        #print("Galactic Longitude: " + str(l_file[i]))
        return pyfits.open("Data/first_try" + str(l_file[i]) + ".fits")
    else:
        #print("Galactic Longitude: " + str(l_file[i-1]))
        return pyfits.open("Data/first_try" + str(l_file[i-1]) + ".fits")
    

def get_dr(coords):
    dr = coords - SUN_COORDS
    return dr


def get_velocity(coords):
    rx, ry = get_x(coords), get_y(coords)
    Vx = GALACTIC_VELOCITY * ry / get_magnitude(coords)
    Vy = GALACTIC_VELOCITY * -1 * rx / get_magnitude(coords)
    return (Vx, Vy)


def get_dv(velocity):
    dv = velocity - SUN_VELOCITY
    return dv


def calculate_doppler_velocity(coords):
    velocity = get_velocity(coords)
    dv = get_dv(velocity)
    dr = get_dr(coords)
    doppler_velocity = np.dot(dv, dr) / get_magnitude(dr)
    return doppler_velocity


def match_doppler_velocity(doppler_velocity, doppler_velocity_value):
    i = bisect.bisect_left(doppler_velocity, doppler_velocity_value)
    if (doppler_velocity[i] - doppler_velocity_value) < (doppler_velocity[i-1] - doppler_velocity_value):
         return i
    else:
        return i-1


def create_map(length):
    grid = np.zeros(shape=(length, length))
    x_axis, y_axis, xy_coords = create_xy_coordinates(length)
    for x in range(length):
        for y in range(length):
            coords = xy_coords[x * length + y]
            dr = get_dr(coords)
            temperature_brightness, doppler_velocity = cal.calibrate_spectra(find_l_file(coords), 20)
            v_dop_value = calculate_doppler_velocity(coords)
            index = match_doppler_velocity(doppler_velocity, v_dop_value)
            grid[x][y] = temperature_brightness[index]
    return grid


def plot_map(grid, length):
    fs = 14 #fontsize for plots
    fig = plt.figure(figsize=[15, 15])
    plt.imshow(grid)
    parallels = np.arange(-GRID_EDGE, GRID_EDGE, 10)
    meridians = np.arange(-GRID_EDGE, GRID_EDGE, 10)
    for loc in parallels:
        axhline(loc, color = 'k', linestyle = ':')
    for loc in meridians:
        axvline(loc, color = 'k', linestyle = ':')

    #plot lines intersecting
    plt.set_ylim(-GRID_EDGE, GRID_EDGE)
    plt.set_xlim(-GRID_EDGE, GRID_EDGE)
    plt.set_title("Map of the Milky Way", fontsize = fs + 2)
    plt.tick_params(which = 'both', labelsize = fs - 2)

    #plot the colorbar
    divider = make_axes_locatable(fig)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    cbar = fig.colorbar(cim, cax = cax, orientation = 'vertical')
    cbar.set_label(cbarlabel, fontsize = fs)
    cax.tick_params(which = 'both', labelsize = fs - 2)
    plt.show()