import georinex as gr
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from scipy.interpolate import lagrange

ax = plt.figure().add_subplot(projection="3d")

sp3_path = Path("qzr_ephemeris\qzr21992.sp3")
sp3_output = Path("./load_sp3")

sp3 = gr.load_sp3(sp3_path, sp3_output)

print(sp3.sel(sv='G01').time)

#X Y Z coords
x = sp3.sel(sv='G01').position.sel(ECEF='x')
y = sp3.sel(sv='G01').position.sel(ECEF='y')
z = sp3.sel(sv='G01').position.sel(ECEF='z')

ax.plot3D(x, y, z, "gray")
plt.show()