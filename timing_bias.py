import roo_accuracy_analysis
import numpy as np

ephemeris_folder = "qzr_ephemeris/" # Choose location of QZSS ephemeris files
telescope_data_folder = "telescope_data/" # Choose where to put the telescope obs csvs
processed_telescope_data = "processed_telescope_data/"

time_offsets = np.arange(-1000, 1001, 100)

for offset in time_offsets:
    print("Trying offset " + str(offset) + "ms")
    output_dir = str(offset) + "accuracy_comparison_data/"
    roo_accuracy_analysis.main(ephemeris_folder, telescope_data_folder, output_dir, offset)