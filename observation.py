import numpy as np
import matplotlib.pyplot as plt
import tool_box as tb
import plot
import os
import rotation as rot
import tracking
import leuschner


class Observation:

    def load_observation_from_file(filename, create_info_method):
    try:
        pyfits.open("Data/" + filename)
    except FileNotFoundError:
        answer = raw_input("Are you about to take data? (yes/no): ")
        if answer == "yes":
            return create_info_method(filename)

    def __init__(self, filename):
        self.data = load_observation_from_file(filename, take_observation)
        self.load_info(filename)


    def take_observation(self, galactic_coordinates):
        equatorial_coordinates = rot.rotate(galactic_coordinates, rot.GAL_to_EQ_rotation)
        ra, dec = equatorial_coordinates[0], equatorial_coordinates[1]
        initial_alt, initial_az = tracking.get_altaz(ra, dec)
        tracking.tracking_object(initial_alt, initial_az, tracking.get_altaz)


    def save_observation(self, number_of_spectra, galactic_coordinates):
        spectrometer = leuscher.Spectrometer('10.0.1.2')
        spectrometer.read_spec("Data/" + filename, number_of_spectra, galactic_coordinates)


    def load_info(self):
        file = open("Data/" + self.filename + "_info", "w+")
        if os.stat("Data/" + self.filename).st_size == 0:
            file.write("Observed Source: " + raw_input("Source observed: "))
            file.write("Date of Observation: " + raw_input("Date of Observation (mm-dd): "))
            file.write("Sampling Frequency: " + raw_input("Sampling Frequency (MHz): "))
            file.write("LO Frequency: " + raw_input("Local Oscillator (MHz): "))
        print(file)
        file.close()


    def get_spectra(self, spectra_number, polarization="first"):
        if polarization == "first":
            pol = 'auto0real'
        elif polarization == "second":
            pol = 'auto1real'
        return self.data[spectra_number][pol]


    def get_header(self, spectra_number):
        print(self.data[spectra_number].header)


    def plot_spectra(self, title="Insert Title"):
        self.power_plot = plt.figure(figsize = [15, 6])
        plot.plot_power(self.power, self.freq, title=title)