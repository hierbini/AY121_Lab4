import numpy as np
import ugradio
import scipy.signal 
import astropy.io.fits as pyfits
import tool_box as tb


def get_spectra(observation, spectra_number, polarization="first"):
	"""
	Function retrieves a specified spectra from an observation file. 

	Parameters:
	observation (file): file where spectra data is saved
	spectra_number (int): index of specific spectra
	polarization (string): polarization of telescope ('first' or 'second')

	Returns:
	spectra (numpy array)
	"""
	if polarization == "first":
		pol = 'auto0_real'
	elif polarization == "second":
		pol = 'auto1_real'
	return observation[spectra_number].data[pol]


def get_average_spectra(observation, n_spectra):
	"""
	Gets the average spectra of all spectra taken during an observation

	Parameters:
	observation (file): file where spectra data is saved
	n_spectra (int): the number of spectra taken during the observation

	Returns:
	average_spectra (numpy array)
	"""
	average_spectra = []
	for i in np.arange(1, n_spectra):
		average_spectra.append(get_spectra(observation, i))
	return np.mean(np.array(average_spectra), axis = 0)


def frequency(header, average_spectra):
	"""
	Gets the frequency axis of the spectra in an observation

	Parameters:
	observation (file): file where spectra data is saved

	Returns:
	frequency (numpy array): a frequency array
	"""
	vsamp = header["SAMPRATE"]
	return (tb.shift(tb.freq(len(average_spectra), d = 1/vsamp)) / 1e6) + 1270 + 150


def baseline_fit(average_spectra, freq):
	"""
	Finds a fit to the baseline. Uses linear interpolation.

	Parameters:
	average_spectra (numpy array): the average spectra of all the spectra in an observation
	freq (numpy array): the frequency array which corresponds to the spectra

	Returns:
	baseline (numpy array): the baseline fit
	"""
	filtered_spectra = scipy.signal.medfilt(average_spectra, kernel_size=5) # take out outliers
	max_index = np.argmax(filtered_spectra)
	cushion = 180
	mask = np.ones(len(filtered_spectra), dtype=bool)
	for i in range(len(mask)):
		if i < max_index + cushion and i > max_index - cushion:
			mask[i] = False
	baseline = scipy.interpolate.interp1d(freq[mask], filtered_spectra[mask], kind='linear')
	return baseline(freq)


def get_gain(noise_on, noise_off):
	"""
	Calculates the gain which, when multiplied with our power spectra, converts our spectra 
	to units of temperature brightness (Kelvin).

	Parameters:
	noise_on (numpy array): spectra with telescope noise turned on
	noise_off (numpy array): specftra with telescope noise turned off

	Returns:
	gain (float): a multiplying constant
	"""
	noise_on_spectra = average_spectra(noise_on, len(noise_on))
	noise_off_spectra = average_spectra(noise_off, len(noise_off))
	T_noise = 30
	T_sky = 2.73
	gain = (T_noise - T_sky) / np.sum(noise_on_spectra - noise_off_spectra) * np.sum(noise_off_spectra)
	return gain

noise_on = pyfits.open("Data/noise_on.fits")
noise_off = pyfits.open("Data/noise_off.fits")
gain = get_gain(noise_on, noise_off)


def doppler_correction(header):
	"""
	Determines the correction needed to shift the doppler velocity to the LSR frame

	Parameters:
	observation (file): file where spectra data is saved

	Returns:
	correction (float): a number that is subtracted from the doppler velocity
	"""
	ra, dec, jd = header["RA"], header["DEC"], header["JD"]
	correction = ugradio.doppler.get_projected_velocity(ra, dec, jd) / 1e3
	return correction


def doppler_velocity(header, freq):
	nu = 1420.4
	delta_nu = freq - nu
	c = 2.99e5
	doppler_velocity = delta_nu / nu * c
	return doppler_velocity - doppler_correction(header) - 30


def calibrate_spectra(observation, n_spectra):
	"""
	Calibrates observation spectra such that we go from power spectra as a function
	of frequency to temperature spectra as a function of doppler velocity (in the 
	LSR frame)

	Parameters:
	observation (file): file where spectra data is saved

	Returns:
	n_spectra (int): the number of spectra taken during the observation
	"""
	header = observation[0].header
	average_spectra = get_average_spectra(observation, n_spectra)
	freq = frequency(header, average_spectra)
	temperature_brightness = (average_spectra - baseline_fit(baseline_fit(average_spectra, freq), freq)) * gain
	v_doppler = doppler_velocity(header, freq)
	return temperature_brightness, v_doppler

