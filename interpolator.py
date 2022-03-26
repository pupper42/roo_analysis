import georinex as gr
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from scipy.interpolate import lagrange
from numpy.polynomial.polynomial import Polynomial

#ax = plt.figure().add_subplot(projection="3d")

sp3_path = Path("qzr_ephemeris\qzr21992.sp3")
sp3_output = Path("./load_sp3")

sp3 = gr.load_sp3(sp3_path, sp3_output)

print(sp3)

#X Y Z coords
x = sp3.sel(sv='G01').position.sel(ECEF='x').to_numpy()
y = sp3.sel(sv='G01').position.sel(ECEF='y').to_numpy()
z = sp3.sel(sv='G01').position.sel(ECEF='z').to_numpy()

data_x = x[0:20]
t = np.arange(0, 20, 1)

poly = lagrange(t, data_x)
t_new = np.arange(0, 20, 0.1)

plt.scatter(t, data_x, label = "data")
plt.plot(t_new, Polynomial(poly.coef[::-1])(t_new), label = "polynomial")

plt.legend()
plt.show()

#ax.plot3D(x, y, z, "gray")