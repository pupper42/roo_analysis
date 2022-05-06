from math import asin, atan2, ceil
import georinex as gr
from pathlib import Path
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from scipy.interpolate import barycentric_interpolate
import numerical_methods as num_meth

from astropy import units as u
from astropy.coordinates import (SkyCoord, EarthLocation)
from astropy import coordinates as coord

from numerical_methods import interp_lagrange

# CONFIG ############## ##############################################
# Choose the sp3 file and satellite and output directory
sp3_file = "qzf21831.sp3"
satellite='J07'
output_dir = "accuracy_comparison_data/"

# Telescope data location 
telescope_data_loc = "telescope_data/QZS1/211108_qzs1_cleaned.csv"

# Observer location 
roo = [-37.680589141*u.deg, 145.061634327*u.deg, 155.083*u.m]
obs_location = EarthLocation.from_geodetic(lat=roo[0], lon=roo[1], height=roo[2], ellipsoid = 'GRS80')

######################################################################

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

# Convert GPS time to UTC time (GPS is ahead by 18s)
utc_time = []

for time in gps_time:
    utc_time.append(time - np.timedelta64(18, 's'))

# Convert the ITRS coordinates to GCRS and TETE coordinates and save it to new arrays


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
    # Convert ITRS coords of satellites to GCRS
    satellite_itrs = SkyCoord(x=satellite_itrs_x[i]*u.km, y=satellite_itrs_y[i]*u.km, z=satellite_itrs_z[i]*u.km, frame='itrs', obstime=utc_time[i])
    satellite_gcrs = satellite_itrs.transform_to(coord.GCRS(obstime=utc_time[i]))

    # Convert ITRS coords of observer location to GCRS
    obsloc_itrs = coord.ITRS((obs_location.x, obs_location.y, obs_location.z), obstime=utc_time[i], representation_type = 'cartesian')
    obsloc_gcrs = obsloc_itrs.transform_to(coord.GCRS(obstime=utc_time[i]))

    # Calculate the vector from the observer to the satellite (obs vector)
    obsloc_to_sat_x = (satellite_gcrs.cartesian.x - obsloc_gcrs.cartesian.x)
    obsloc_to_sat_y = (satellite_gcrs.cartesian.y - obsloc_gcrs.cartesian.y)
    obsloc_to_sat_z = (satellite_gcrs.cartesian.z - obsloc_gcrs.cartesian.z)
    obsloc_to_sat_r = np.array([obsloc_to_sat_x.value, obsloc_to_sat_y.value, obsloc_to_sat_z.value])

    # Calculate magnitude of the obs vector and RA/DEC
    topo_dist = np.linalg.norm(obsloc_to_sat_r)
    topo_rav = atan2(obsloc_to_sat_r[1], obsloc_to_sat_r[0])*180/np.pi

    topo_decv = asin(obsloc_to_sat_r[2]/topo_dist)*180/np.pi
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
    
    print("Transforming... " + str(percentage_complete) + "% complete")
print("Transformation complete!")

# Save geocentric coordinates
str_time = np.datetime_as_string(utc_time)
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
# ax = plt.figure().add_subplot(projection="3d")
# ax.plot3D(satellite_gcrs_x, satellite_gcrs_y, satellite_gcrs_z, "gray")
# ax.plot3D(satellite_itrs_x, satellite_itrs_y, satellite_itrs_z, "red")
# plt.show()

# Interpolate satellite ITRS coordinates to telescope time and compare
telescope_data = np.genfromtxt(telescope_data_loc, delimiter=',', dtype = None, encoding='utf-8')
telescope_time = telescope_data[1:, 0]
telescope_ra = telescope_data[1:, 3].astype(np.float)
telescope_dec = telescope_data[1:, 4].astype(np.float)
print(telescope_ra)
utc_time_timestamp = np.array([pd.to_datetime([time]).astype(int) / 10**6 for time in gps_time]).flatten()
telescope_time_timestamp = np.array([pd.to_datetime([str(time)]).astype(int) / 10**6 for time in telescope_time]).flatten()

interp_ra_list = []
interp_dec_list = []

for i in telescope_time_timestamp:
    interp_ra = num_meth.interp_lagrange(utc_time_timestamp, topo_ra, i, 9)
    interp_dec = num_meth.interp_lagrange(utc_time_timestamp, topo_dec, i, 9)
    interp_ra_list.append(interp_ra)
    interp_dec_list.append(interp_dec)

plt.plot(utc_time_timestamp, topo_ra, marker = 'o', label = 'Ephemeris coordinates')
plt.plot(telescope_time_timestamp, interp_ra_list, marker = 'o', label = 'Interpolated ephemeris coordinates')
plt.plot(telescope_time_timestamp, telescope_ra, marker = 'o', label = 'Telescope coordinates')
plt.show()
print(np.subtract(interp_ra_list, telescope_ra))


