import numpy as np 

def mean_spec(spectra):
	return np.mean(spectra, axis = 0)

def son_soff(upperspec, lowerspec):
    """
    Creates online spectrum and offline spectrum from the upper spectra and lower spectra
    
    Parameters:
    upperspec (list): upper spectrum
    lowersepec (list): lower spectrum
    
    Returns:
    s_on (array): online spectrum
    s_off (array): offline spectrum
    """
    left_upper, right_upper = np.split(upperspec, 2)
    left_lower, right_lower = np.split(lowerspec, 2)
    s_off = list(right_upper) + list(left_lower)
    s_on = list(left_upper) + list(right_lower)
    return np.asarray(s_on), np.asarray(s_off)

s_on, s_off = son_soff(mean_upperspec, mean_lowerspec)
s_line = s_on/s_off