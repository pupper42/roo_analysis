from math import asin, atan2, ceil
import georinex as gr
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import glob
import numerical_methods as num_meth
from astropy import units as u
from astropy.coordinates import (SkyCoord, EarthLocation)
from astropy import coordinates as coord

# CONFIG
# Place telescope data in <telescope_data_folder>/QZSS1 or QZSS3
# Program will automatically detect the correct satellite (provided you put the data in the right spot)
# Program will also automatically choose the correct ephemeris in <ephemeris_folder>. 
# Might cause problems if the telescope's data includes 2 different days (TODO: Fix and also pull ephemeris data from online repo)
# The UTC time, interpolated RA/DEC, telescope RA/DEC and the difference will be saved in csv files under <output_dir>

ephemeris_folder = 'qzr_ephemeris/' # Choose location of QZSS ephemeris files
telescope_data_folder = 'telescope_data/'

output_dir = "accuracy_comparison_data/" # Choose where to save final comparison data

####################################################################
def pick_ephemeris_file(file):
    telescope_obs_file = np.genfromtxt(file, delimiter = ",", dtype = None, encoding='utf-8')
    print(telescope_obs_file[1, 0])
    first_timestamp = datetime.strptime(telescope_obs_file[1, 0],)
    print(first_timestamp)

def choose_input_files(ephemeris_folder, telescope_data_folder):
    telescope_obs_files = glob.glob(telescope_data_folder + "*/*.csv")
    ephemeris_files = []
    satellite = []

    for file in telescope_obs_files:
        if ("QZS1" in file):
            print("This is data for QZS1")
            ephemeris_files.append(pick_ephemeris_file(file))
            satellite.append("J01")
        elif ("QZS3" in file):
            print("This is data for QZS3")
            ephemeris_files.append(pick_ephemeris_file(file))
            satellite.append("J07")

choose_input_files(ephemeris_folder, telescope_data_folder)