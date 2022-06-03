import matplotlib.pyplot as plt
import numpy as np
import glob

time_offsets = np.arange(-1000, 1001, 100)
qzs1_ra_means = []
qzs1_dec_means = []


for offset in time_offsets:
    print("Generating statistics for offset " + str(offset) + "ms")
    input_dir = str(offset) + "accuracy_comparison_data/"
    comparison_files = glob.glob(input_dir + "*.csv")
    for file in comparison_files:
        comparison_file = np.genfromtxt(file, delimiter = ",", dtype = None, encoding='utf-8')

        ra_diff = comparison_file[1:, 5].astype(np.float)
        ra_diff_mean = np.mean(ra_diff)
        ra_diff_std = np.std(ra_diff)

        dec_diff = comparison_file[1:,6].astype(np.float)
        dec_diff_mean = np.mean(dec_diff)
        dec_diff_std = np.std(dec_diff)

        ra_means.append(ra_diff_mean)
        #ra_stds.append(ra_diff_std)

        dec_means.append(dec_diff_mean)
        #dec_stds.append(dec_diff_std)

        #print("RA mean: " + str(ra_diff_mean))
        #print("RA standard deviation: " + str(ra_diff_std))

        #print("DEC mean: " + str(dec_diff_mean))
        #print("DEC standard deviation: " + str(dec_diff_std))

QZS1_ra = np.array(ra_means)[1::4]     
QZS1_dec = np.array(dec_means)[1::4]

print(QZS1_ra)
print(QZS1_dec)

plt.plot(time_offsets, QZS1_ra, marker = 'o')
plt.plot(time_offsets, QZS1_dec, marker = 'o')
plt.title("Mean difference in RA/DEC for QZS#")
plt.xlabel("Offset (ms)")
plt.ylabel("Angle (arcseconds)")
plt.legend(["RA", "DEC"])
plt.show()