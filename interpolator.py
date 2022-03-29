import georinex as gr
from pathlib import Path
import matplotlib.pyplot as plt

import numpy as np
from numpy.polynomial.polynomial import Polynomial

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy import coordinates as coord
from astropy.time import Time

from scipy.interpolate import lagrange


ax = plt.figure().add_subplot(projection="3d")

sp3_path = Path("qzr_ephemeris\qzr21992.sp3")
sp3_output = Path("./load_sp3")

sp3 = gr.load_sp3(sp3_path, sp3_output)

print(sp3)

# GCRS (ECEF) coordinates
x_itrs = sp3.sel(sv='G01').position.sel(ECEF='x').to_numpy()
y_itrs = sp3.sel(sv='G01').position.sel(ECEF='y').to_numpy()
z_itrs = sp3.sel(sv='G01').position.sel(ECEF='z').to_numpy()
t = sp3.sel(sv='G01').position.time.to_numpy()

ra = []
dec = []
distance = []

x_gcrs = []
y_gcrs = []
z_gcrs = []

array_size = x_itrs.size

for i in range(array_size):
    satellite_itrs = SkyCoord(x=x_itrs[i]*u.km, y=y_itrs[i]*u.km, z=z_itrs[i]*u.km, frame='itrs', obstime=t[i])
    satellite_gcrs = satellite_itrs.transform_to(coord.GCRS(obstime=t[i]))
    satellite_gcrs.representation_type = 'cartesian'
    
    x_gcrs.append(satellite_gcrs.x.value)
    y_gcrs.append(satellite_gcrs.y.value)
    z_gcrs.append(satellite_gcrs.z.value)

ax.plot3D(x_gcrs, y_gcrs, z_gcrs, "gray")
ax.plot3D(x_itrs, y_itrs, z_itrs, "red")
plt.show()