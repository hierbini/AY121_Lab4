import numpy as np
import matplotlib.pyplot as plt
import tool_box as tb
import tracking
import leuschner
import ugradio.leusch

ALT_MIN, ALT_MAX = 15, 85
AZ_MIN, AZ_MAX = 5, 350

def take_observation(filename):
    degree_spacing = 2
    longitude_range = np.linspace(-10, 250, (250 + 10) / degree_spacing)
    b = 0
    number_of_spectra = 20

    LT = ugradio.leusch.LeuschTelescope()
    spectrometer = leuschner.Spectrometer('10.0.1.2')
    missing_longitudes = np.load("missinglongitudes.npy")

    for l in longitude_range:
        if (l in missing_longitudes):
            alt, az = tracking.get_altaz(l, b)
            if (ALT_MIN < alt < ALT_MAX) and (AZ_MIN < az < AZ_MAX): 
                LT.point(alt, az)
                spectrometer.read_spec(filename + str(l) + ".fits", number_of_spectra, (l, b))


def get_spectra(observation, spectra_number, polarization="first"):
    if polarization == "first":
        pol = 'auto0_real'
    elif polarization == "second":
        pol = 'auto1_real'
    spectra = observation[spectra_number].data[pol]
    return spectra


def plot_spectra(observation, n_spectra, title="Insert Title"):
    power, freqs = average_spectra(observation, n_spectra)
    self.power_plot = plt.figure(figsize = [15, 6])
    plt.title(title)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power ($V^{2}$)")
    plt.plot_power(power, freqs)
    plt.grid()
    plt.show()


def average_spectra(observation, n_spectra):
    average_spectra = []
    for i in np.arange(1, n_spectra):
        average_spectra.append(get_spectra(observation, i))
    v_samp = observation[0].header["SAMPRATE"]
    freqs = tb.shift(tb.freq(len(spectra), d = 1 / v_samp)) / 1e6
    return np.mean(np.array(average_spectra), axis = 0), freqs