#Processes the raw angles data to get only date, RA and DEC. Also attempts to remove false positives.
#Output csv structure:
#Col 0: Date, Col 1: RA, Col 2: DEC
#Unique rows: https://gist.github.com/cgois/635ed2f67067df19a7b920e1b32d3fe5

import numpy as np
import os

qzs1_raw_data = "unprocessed_obs/QZS1/"
qzs3_raw_data = "unprocessed_obs/QZS3/"

qzs1_data = "processed_obs/QZS1/"
qzs3_data = "processed_obs/QZS3/"

def unique_rows(A, atol=10e-3):
    remove = np.zeros(A.shape[0], dtype=bool)

    for i in range(A.shape[0]): 	# Not very optimized, but simple.
        equals = np.all(np.isclose(A[i, :], A[(i + 1):, :], atol=atol), axis=1)
        remove[(i + 1):] = np.logical_or(remove[(i + 1):], equals)
    return A[np.logical_not(remove)]

#Process QZS1 data

for directory in os.listdir(qzs1_raw_data):
    
    data_file = qzs1_raw_data + directory + "/CSVs/PNGs_angles.csv"
    
    raw_data = np.genfromtxt(data_file, delimiter=",", dtype=str)
    data = np.delete(raw_data, [1, 2], 1)
    data = np.delete(data, [0], 0)

    processed_data = unique_rows(data)

    save_file = qzs1_data + directory + "_qzs1_radec.csv"
    np.savetxt(save_file, processed_data, delimiter=",", fmt="%s")

    
#Process QZS3 data

for directory in os.listdir(qzs3_raw_data):
    
    data_file = qzs3_raw_data + directory + "/CSVs/PNGs_angles.csv"
    
    raw_data = np.genfromtxt(data_file, delimiter=",", dtype=str)
    data = np.delete(raw_data, [1, 2], 1)

    save_file = qzs3_data + directory + "_qzs3_radec.csv"
    np.savetxt(save_file, data, delimiter=",", fmt="%s")

