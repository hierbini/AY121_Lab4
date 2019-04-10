import numpy as np
import ugradio
import tool_box as tb
import time
import leusch

def seconds_from_hours(number_of_hours):
    return number_of_hours * 3600

DT = 5  # timestep for tracking
max_time = tb.time["Julian"]() + seconds_from_hours(1)  # when to stop pointing

def difference(a, b):
    return np.abs(a - b)


def get_altaz(ra, dec):
    return ugradio.coord.get_altaz(ra, dec, lat=leo.lat, lon=leo.lon, alt=leo.alt)


def track_object(altitude, azimuth, position_calculator):
    LT = ugradio.leusch.LeuschTelescope()
    print('pointing dishes')
    LT.point(altitude, azimuth)
    print('first pointing done')
    try:
        while True:
            if tb.time["Julian"]() > max_time:
                print('observing successful')
                break
            altitude, azimuth = position_calculator()  # recompute position
            LT.point(altitude, azimuth)
            print('Target:' + str(altitude) + ',' + str(azimuth))
            alt_point, az_point = LT.get_pointing()
            print('Telescope pointed: ' + str(alt_point) + ', ' + str(az_point))
            time.sleep(DT)
    except Exception as e:
        print("Error")
    finally:
        LT.stow()