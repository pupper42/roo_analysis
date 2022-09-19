import roo_vs_ephemeris
import numpy as np
from datetime import datetime, timedelta

ephemeris_folder = "qzr_ephemeris/" # Choose location of QZSS ephemeris files
telescope_data_folder = "telescope_data/" # Choose where to put the telescope obs csvs
processed_telescope_data = "processed_telescope_data/"

time_offsets = np.arange(0, 100, 100)

for offset in time_offsets:
    offset_datetime = timedelta(milliseconds=int(offset))
    print("Trying offset " + str(offset) + "ms")
    output_dir = "time_offset_analysis/"
    roo_vs_ephemeris.main(ephemeris_folder, telescope_data_folder, output_dir, offset_datetime)