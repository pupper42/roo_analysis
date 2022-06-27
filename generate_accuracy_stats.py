import matplotlib.pyplot as plt
import numpy as np
import glob

comparison_data = "accuracy_comparison_data/"
satellites = ["qzs1", "qzs2", "qzs3", "qzs4"]
def overall_stats():
    ra_means = []
    ra_stds = []
    dec_means = []
    dec_stds = []
    norm_ra_decs = []
    for satellite in satellites:
        comparison_files = glob.glob(comparison_data + "????????????????" + satellite + "????????.csv")
        
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
    plt.plot(satellites, ra_means, 'o')
    plt.plot(satellites, dec_means, 'o')
    plt.plot(satellites, norm_ra_decs, 'o')
    plt.legend(["RA Mean", "DEC Mean", "Norm of RA and DEC"])
    plt.title("Mean RA/DEC Errors for QZSS Observations")
    plt.savefig("overall_mean.png")
    plt.clf()
    plt.plot(satellites, ra_stds, 'o')
    plt.plot(satellites, dec_stds, 'o')
    plt.legend(["RA Sigma", "DEC Sigma"])
    plt.title("Standard Deviation of RA/DEC Errors for QZSS Observations")
    plt.savefig("overall_std.png")

def individual_stats():
    ra_means = []
    ra_stds = []
    dec_means = []
    dec_stds = []
    ras = []
    decs = []
    norm_ra_decs = []
    for satellite in satellites:
        comparison_files = glob.glob(comparison_data + "????????????????" + satellite + "????????.csv")
        
        for file in comparison_files:
            comparison_file = np.genfromtxt(file, delimiter = ",", dtype = None, encoding='utf-8')
            time = comparison_file[1:, 0].astype(float)
            ra_diff = comparison_file[1:, 5].astype(float)
            ra_diff_mean = [np.mean(ra_diff)]*len(time)
            ra_diff_std = np.std(ra_diff)

            dec_diff = comparison_file[1:,6].astype(float)
            dec_diff_mean = [np.mean(dec_diff)]*len(time)
            dec_diff_std = np.std(dec_diff)

            norm_ra_decs.append(np.linalg.norm([ra_diff_mean, dec_diff_mean]))
            plt.clf()
            plt.plot(time, ra_diff, 'o')
            plt.plot(time, ra_diff_mean, linestyle = '--', label = ra_diff_mean[0])
            plt.plot(time, dec_diff, 'o')            
            plt.plot(time, dec_diff_mean, linestyle = '--', label = dec_diff_mean[0])
            plt.legend(["RA Differences", "RA Mean", "DEC Differences", "DEC Mean"])
            plt.title("RA/DEC Errors for " + satellite.upper())
            plt.xlabel("Observations")
            plt.ylabel("Angle difference (arcseconds)")
            #plt.show()
            plt.savefig("ra_dec_errors" + satellite + ".png")
            
            

overall_stats()
#individual_stats()