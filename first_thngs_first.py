import tracking
import leuschner


 def take_observation(altitude, azimuth):
    LT = ugradio.leusch.LeuschTelescope()
    LT.point(altitude, azimuth)

def save_observation(number_of_spectra, galactic_coordinates):
    spectrometer = leuscher.Spectrometer('10.0.1.2')
    spectrometer.read_spec("Data/" + filename, number_of_spectra, galactic_coordinates)

l, b = 120, 0
alt, az = tracking.get_altaz(l, b)
take_observation(alt, az)
save_observation(100, (l, b))