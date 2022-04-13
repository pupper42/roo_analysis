from math import asin, atan2, ceil
import georinex as gr
from pathlib import Path
import matplotlib.pyplot as plt

import numpy as np
from numpy.polynomial.polynomial import Polynomial

from astropy import units as u
from astropy.coordinates import (SkyCoord, EarthLocation)
from astropy import coordinates as coord
from astropy.time import Time

from scipy.interpolate import lagrange
from numerical_methods import interp_lagrange # Credit to https://github.com/gehly/metis

# Observer location 
roo = [-37.680589141*u.deg, 145.061634327*u.deg, 155.083*u.m]
obs_location = EarthLocation.from_geodetic(lat=roo[0], lon=roo[1], height=roo[2], ellipsoid = 'GRS80')

# Choose the sp3 file and satellite and output directory
sp3_file = "qzf21831.sp3"
satellite='J03'
output_dir = "truth_orbit_data/"

# Load the sp3 file
sp3_path = Path("qzr_ephemeris/" + sp3_file)
sp3_output = Path("./load_sp3")
sp3 = gr.load_sp3(sp3_path, sp3_output)
print("Loaded SP3 file")

# Read the ITRS (ECEF) coordinates of the satellites + time
satellite_itrs_x = sp3.sel(sv=satellite).position.sel(ECEF='x').to_numpy()
satellite_itrs_y = sp3.sel(sv=satellite).position.sel(ECEF='y').to_numpy()
satellite_itrs_z = sp3.sel(sv=satellite).position.sel(ECEF='z').to_numpy()
gps_time = sp3.sel(sv=satellite).position.time.to_numpy()
print("Coordinates read successfully")

# Convert the ITRS coordinates to GCRS and TETE coordinates and save it to new arrays
utc_time_list = []

satellite_gcrs_x = []
satellite_gcrs_y = []
satellite_gcrs_z = []

geo_distance = []
geo_ra = []
geo_dec = []

topo_distance = []
topo_ra = []
topo_dec = []

array_size = satellite_itrs_x.size
for i in range(array_size):
    # Correct GPS time offset (GPS is ahead by 18s, so subtract 18s from GPS time)
    utc_time = gps_time[i] - np.timedelta64(18, 's')
    utc_time_list.append(utc_time)
    # Convert ITRS coords of satellites to GCRS
    satellite_itrs = SkyCoord(x=satellite_itrs_x[i]*u.km, y=satellite_itrs_y[i]*u.km, z=satellite_itrs_z[i]*u.km, frame='itrs', obstime=utc_time)
    satellite_gcrs = satellite_itrs.transform_to(coord.GCRS(obstime=utc_time))

    # Convert ITRS coords of observer location to GCRS
    obsloc_itrs = coord.ITRS((obs_location.x, obs_location.y, obs_location.z), obstime=utc_time, representation_type = 'cartesian')
    obsloc_gcrs = obsloc_itrs.transform_to(coord.GCRS(obstime=utc_time))

    # Calculate the vector from the observer to the satellite (obs vector)
    obs_vec_x = (satellite_gcrs.cartesian.x - obsloc_gcrs.cartesian.x)
    obs_vec_y = (satellite_gcrs.cartesian.y - obsloc_gcrs.cartesian.y)
    obs_vec_z = (satellite_gcrs.cartesian.z - obsloc_gcrs.cartesian.z)
    obs_vec_r = np.array([obs_vec_x.value, obs_vec_y.value, obs_vec_z.value])

    # Calculate magnitude of the obs vector and RA/DEC
    topo_dist = np.linalg.norm(obs_vec_r)
    topo_rav = atan2(obs_vec_r[1], obs_vec_r[0])*180/np.pi
    print(topo_rav)
    topo_decv = asin(obs_vec_r[2]/topo_dist)*180/np.pi
    if topo_rav < 0:
        topo_rav += 360
    
    # Save the satellite's GCRS coordinates in cartesian for plotting
    satellite_gcrs.representation_type = 'cartesian'
    satellite_gcrs_x.append(satellite_gcrs.x.value)
    satellite_gcrs_y.append(satellite_gcrs.y.value)
    satellite_gcrs_z.append(satellite_gcrs.z.value)

    # Save the satellite's GCRS coordinates in RA/DEC for plotting
    satellite_gcrs.representation_type = 'spherical'
    geo_distance.append(satellite_gcrs.distance.value)
    geo_ra.append(satellite_gcrs.ra.degree)
    geo_dec.append(satellite_gcrs.dec.degree)

    # Save the satellite's topocentric coordinates in RA/DEC
    topo_distance.append(topo_dist)
    topo_ra.append(topo_rav)
    topo_dec.append(topo_decv)

    percentage_complete = ceil((i/array_size)*100)
    
    #print("Transforming... " + str(percentage_complete) + "% complete")

print("Transformation complete!")
print(topo_ra)
# Save geocentric coordinates
str_time = np.datetime_as_string(utc_time_list)
gcrs_coords = np.stack((str_time, geo_ra, geo_dec, geo_distance), axis=1)
output_file = output_dir + satellite + "_" + sp3_file + "_geo.csv"
np.savetxt(output_file, gcrs_coords, delimiter=',', fmt='%s')
print("Geocentric coordinates CSV saved in " + output_file)

# Save topocentric coordinates
topo_coords = np.stack((str_time, topo_ra, topo_dec, topo_distance), axis=1)
output_file = output_dir + satellite + "_" + sp3_file + "_topo.csv"
np.savetxt(output_file, topo_coords, delimiter=',', fmt='%s')
print("Topocentric coordinates CSV saved in " + output_file)

# Plot the orbit
ax = plt.figure().add_subplot(projection="3d")
ax.plot3D(satellite_gcrs_x, satellite_gcrs_y, satellite_gcrs_z, "gray")
ax.plot3D(satellite_itrs_x, satellite_itrs_y, satellite_itrs_z, "red")
plt.show()