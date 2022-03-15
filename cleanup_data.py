#Processes the raw angles data to get only date, RA and DEC. Also attempts to remove false positives.
#Output csv structure:
# Col 0: Date, Col 1: RA, Col 2: DEC

import numpy as np
import os

qzs1_raw_data = "raw_data/QZS1/"
qzs3_raw_data = "raw_data/QZS3/"

qzs1_data = "data/QZS1/"
qzs3_data = "data/QZS3/"

#Process QZS1 data

for directory in os.listdir(qzs1_raw_data):
    
    data_file = qzs1_raw_data + directory + "/CSVs/PNGs_angles.csv"
    
    raw_data = np.genfromtxt(data_file, delimiter=",", dtype=str)
    data = np.delete(raw_data, [1, 2], 1)
    data = np.delete(data, [0], 0)

    RA = np.array(np.unique(data[1:, 1].astype(np.float64).round(2), return_index=True))
    DEC = np.array(np.unique(data[1:, 2].astype(np.float64).round(3), return_index=True))

    #for i in len(RA):
    #   if RA[1, i] == DEC

    satellite_RA = data[np.array(RA)[1, :].astype(np.int32), 1]
    satellite_DEC = data[np.array(DEC)[1, :].astype(np.int32), 2]

    np.savetxt("RAtest.csv", RA, delimiter=",", fmt="%s")
    np.savetxt("DECtest.csv", DEC, delimiter=",", fmt="%s")

    print(data)

    #processed_data = np.column_stack((data[:, 0], satellite_RA, satellite_DEC))

    #save_file = qzs1_data + directory + "_qzs1_radec.csv"
    #np.savetxt(save_file, processed_data, delimiter=",", fmt="%s")

    
#Process QZS3 data

for directory in os.listdir(qzs3_raw_data):
    
    data_file = qzs3_raw_data + directory + "/CSVs/PNGs_angles.csv"
    
    raw_data = np.genfromtxt(data_file, delimiter=",", dtype=str)
    data = np.delete(raw_data, [1, 2], 1)

    save_file = qzs3_data + directory + "_qzs3_radec.csv"
    np.savetxt(save_file, data, delimiter=",", fmt="%s")

