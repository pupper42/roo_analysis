import matplotlib.pyplot as plt
import numpy as np
import glob

time_offsets = np.arange(-1000, 1000, 100)
#satellites = ["qzs1", "qzs2", "qzs3", "qzs4"]
satellites = ["qzs4"]

def get_satellite_stats(satellite):
    ra_means = []
    dec_means = []
    ra_stds = []
    dec_stds = []
    norm_ra_decs = []
    for offset in time_offsets:      
        input_dir = "time_offset_analysis/" + str(offset) + "accuracy_comparison_data/"
        comparison_files = glob.glob(input_dir + "????????????????" + satellite + "????????.csv")
        for file in comparison_files:
            comparison_file = np.genfromtxt(file, delimiter = ",", dtype = None, encoding='utf-8')

            ra_diff = comparison_file[1:, 5].astype(float)
            ra_diff_mean = np.mean(ra_diff)
            ra_diff_std = np.std(ra_diff)

            dec_diff = comparison_file[1:,6].astype(float)
            dec_diff_mean = np.mean(dec_diff)
            dec_diff_std = np.std(dec_diff)

            ra_means.append(ra_diff_mean)
            ra_stds.append(ra_diff_std)

            dec_means.append(dec_diff_mean)
            dec_stds.append(dec_diff_std)
            print(ra_diff_mean)
            print(dec_diff_mean)
            norm_ra_decs.append(np.linalg.norm([ra_diff_mean, dec_diff_mean]))
    return ra_means, dec_means, ra_stds, dec_stds, norm_ra_decs

for satellite in satellites:
    ra_means, dec_means, ra_stds, dec_stds, norm_ra_decs = get_satellite_stats(satellite)
    print(ra_means)
    plt.clf()
    plt.plot(time_offsets, ra_means, marker = 'o')
    plt.plot(time_offsets, dec_means, marker = 'o')
    plt.plot(time_offsets, norm_ra_decs, marker = 'o')
    plt.title("Mean difference in RA/DEC for " + satellite.upper())
    plt.xlabel("Offset (ms)")
    plt.ylabel("Angle (arcseconds)")
    plt.legend(["RA", "DEC", "Norm of RA and DEC"])
    plt.savefig(satellite + ".png")