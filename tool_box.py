import numpy as np
import ugradio


units = {"time": "($\mu$s)",
         "frequency": "(MHz)",
         "temperature": "(K)",
         "velocity": "($km \cdot s^{-1}$)",
         "voltage": "($\mu$V)",
         "voltage spectra": "($\mu V \cdot \mu s$)",
         "power spectra": "($\mu V^{2} \cdot \mu s^{2}$)"
        }


time = {"Local": ugradio.timing.local_time,
        "UTC": ugradio.timing.utc, # current UTC as a string
        "UTC seconds": ugradio.timing.unix_time,
        "Julian": ugradio.timing.julian_date, # current Julian day and time,
        "LST": ugradio.timing.lst # current LST at NCH
       }


fft = np.fft.fft
shift = np.fft.fftshift
freq = np.fft.fftfreq


def LST_from_unixtimes(unixtimes):
    """
    Returns local sidereal times from array of unixtimes
    
    Parameters:
    unixtimes (int array): unixtimes from interferometer data

    Returns:
    lst (float array): Returns local sidereal time in radians
    """
    julian_dates = time["Julian"](unixtimes)
    lst = time["LST"](julian_dates)
    return lst


def hour_angle(lst, ra):
    """
    Calculates the hour angle given local sidereal time and right ascension

    Parameters:
    lst (float array): local sidereal time in radians
    ra (float array): right ascension in radians

    Returns:
    hour angles (float array): equal to (lst - ra)
    """
    return lst - ra + 2*np.pi