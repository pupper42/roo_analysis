from photutils.detection import find_peaks, DAOStarFinder
from photutils.background import Background2D, MedianBackground
from photutils.aperture import aperture_photometry, CircularAperture
from photutils.psf import extract_stars, EPSFBuilder
from astropy.table import Table
from astropy.stats import mad_std, SigmaClip, sigma_clipped_stats
from astropy.io import fits
from astropy.nddata import NDData
from astropy.visualization import simple_norm
import numpy as np
import matplotlib.pyplot as plt

image = fits.open('astrometry_testing/00051718_QZS-4__MICHIBIKI-4__#42965U_20220502_1.000secs_2x2_Light.fit')

data = image[0].data

# Estimate background
sigma_clip = SigmaClip(sigma=3.)
bkg_estimator = MedianBackground()
bkg = Background2D(data, (50, 50), filter_size=(3, 3), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)

# Remove background
data_nobkg = data - bkg.background

# Find stars
mean, median, std = sigma_clipped_stats(data, sigma=3.0)
daofind = DAOStarFinder(fwhm=5.0, threshold=5.*std)
sources = daofind(data_nobkg)

size = 25
hsize = (size-1)/2
x = sources['xcentroid']
y = sources['ycentroid']
mask = ((x > hsize) & (x < (data_nobkg.shape[1] -1 - hsize)) &
(y > hsize) & (y < (data_nobkg.shape[0] -1 - hsize)))
stars_tbl = Table()
stars_tbl['x'] = x[mask]
stars_tbl['y'] = y[mask]

norm = simple_norm(data_nobkg, 'log', percent = 99.)
plt.imshow(data_nobkg, cmap='viridis', norm=norm)
plt.plot(x, y, 'o', 'bo', markerfacecolor='none')
plt.show()
#plt.imshow(data_nobkg, origin='lower', cmap='viridis')
#plt.plot(stars_tbl['x'], stars_tbl['y'], 'bo', markerfacecolor='none')
#plt.show()

nddata = NDData(data = data_nobkg)
stars = extract_stars(nddata, stars_tbl, size = 35)
print(stars.all_stars)

nrows = 5
ncols = 4
fig, ax = plt.subplots(nrows = len(stars), ncols = 1, figsize = (20, 20), squeeze=True)
ax = ax.ravel()
for i in range(len(stars)):
    norm = simple_norm(stars[i], 'log', percent = 99.)
    ax[i].imshow(stars[i], norm=norm, origin='lower', cmap='viridis')

epsf_builder = EPSFBuilder(oversampling=4, maxiters=3, progress_bar=True)
epsf, fitted_stars = epsf_builder(stars)

print(fitted_stars.center_flat)
norm = simple_norm(epsf.data, 'log', percent = 99.)
plt.imshow(epsf.data, norm=norm, origin='lower', cmap='viridis')
plt.colorbar()
plt.show()