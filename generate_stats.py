import matplotlib.pyplot as plt
import numpy as np

time_offsets = np.arange(-1000, 1001, 100)

for offset in time_offsets:
    print("Generating statistics for offset " + str(offset) + "ms")
    input_dir = str(offset) + "accuracy_comparison_data/"
    