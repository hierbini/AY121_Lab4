import numpy as np
import matplotlib.pyplot as plt
import tool_box as tb
import leuschner
import ugradio.leusch
from astropy.coordinates import SkyCoord,AltAz,EarthLocation
from astropy import units as u
from astropy.time import Time
import ugradio.timing
import ugradio.leo as leo
import time
import astropy.io.fits as pyfits

ALT_MIN, ALT_MAX = 15, 85
AZ_MIN, AZ_MAX = 5, 350
coords = EarthLocation(lat=leo.lat*u.deg, lon=leo.lon*u.deg, height=leo.alt*u.m) #leuschner 

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


degree_spacing = 2
longitude_range = np.linspace(-10, 250, (250 + 10) / degree_spacing)

def find_missing_longitudes():
    missing_longitudes = []
    for l in longitude_range:
        try:
            pyfits.open("Data/final" + str(l) + ".fits")
        except:
            missing_longitudes.append(l)
    np.save("missing_longitudes_final", missing_longitudes)
    return missing_longitudes


def take_observation(filename, wait):
    time.sleep(wait)
    degree_spacing = 2
    longitude_range = np.round(np.linspace(-10, 250, (250 + 10) / degree_spacing),2)
    b = 0
    number_of_spectra = 20

    synth = ugradio.agilent.SynthDirect()
    synth.set_frequency(635, "MHz")

    LT = ugradio.leusch.LeuschTelescope()
    spectrometer = leuschner.Spectrometer('10.0.1.2')
    missing_longitudes = np.load("missing_longitudes_final.npy")

    for l in longitude_range:
        if (l in missing_longitudes):
            alt, az = get_altaz(l, b)
            if (ALT_MIN < alt < ALT_MAX) and (AZ_MIN < az < AZ_MAX): 
                l = np.round(l, 2)
                LT.point(alt, az)
                spectrometer.read_spec("Data/" + filename + str(l) + ".fits", number_of_spectra, (l, b))
    noise = ugradio.leusch.LeuschNoise()
    noise.on()
    spectrometer.read_spec("Data/" + filename + str(l) + "_noise_on.fits", number_of_spectra, (l, b))
    noise.off()
    spectrometer.read_spec("Data/" + filename + str(l) + "_noise_off.fits", number_of_spectra, (l, b))
    LT.stow()
    find_missing_longitudes()
