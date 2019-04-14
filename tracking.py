import numpy as np
import ugradio
import tool_box as tb
import time
import leusch
from astropy.coordinates import SkyCoord,AltAz,EarthLocation
from astropy import units as u
from astropy.time import Time
import ugradio.timing
import leo

def seconds_from_hours(number_of_hours):
    return number_of_hours * 3600


DT = 5 # timestep for tracking
max_time = tb.time["Julian"]() + seconds_from_hours(1)  # when to stop pointing
coords = EarthLocation(lat=leo.lat*u.deg, lon=leo.lon*u.deg, height=leo.alt*u.m)


def difference(a, b):
    return np.abs(a - b)


def print_altaz(alt, az):
    print("Altitude: " + str(alt), "Azimuth: " + str(az))


def get_altaz(l, b, julian_date=None):
    if julian_date == None:
        julian_date = ugradio.timing.julian_date()
    position = SkyCoord(frame='galactic', l=l, b=b, unit=(u.degree,u.degree))
    altaz=position.transform_to(AltAz(obstime=Time(julian_date,format='jd'),location=coords))
    alt, az = altaz.alt.deg, altaz.az.deg
    print_altaz(alt, az)
    return alt, az


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