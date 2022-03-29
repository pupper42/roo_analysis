from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy import coordinates as coord

from datetime import datetime

c_itrs = SkyCoord(x=3000*u.km, y=3000*u.km, z=3000*u.km, frame='itrs', obstime=datetime.now())
c_gcrs = c_itrs.transform_to(coord.GCRS(obstime=datetime.now()))
c_gcrs.representation_type = 'cartesian'

print(c_gcrs)