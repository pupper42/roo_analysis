from skyfield.api import N, W, wgs84, load, Distance
from skyfield.toposlib import ITRSPosition

roo = [-37.680589141, 145.061634327, 155.083]
planets = load('de421.bsp')
ts = load.timescale()
t = ts.now()

obs_location = wgs84.latlon(roo[0], roo[1], roo[2])
satellite = Distance(km=[-3918, -1887, 5209])
satellite_itrs = ITRSPosition(satellite)

difference = satellite_itrs - obs_location
topocentric = difference.at(t)

ra, dec, distance = topocentric.radec()

print(ra)
print(dec)