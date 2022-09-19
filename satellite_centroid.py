import matplotlib.pyplot as plt
import numpy as np
from astropy.stats import SigmaClip
from astropy.io import fits
from astropy.visualization import SqrtStretch, simple_norm
from astropy.visualization.mpl_normalize import ImageNormalize
from astropy.table import Table
from astropy.nddata import NDData
from photutils.aperture import CircularAperture
from photutils.background import Background2D, MedianBackground
from photutils.detection import DAOStarFinder
from photutils.psf import extract_stars, EPSFBuilder

#Load the image
data_folder = "centroid_test"
image = fits.open('centroid_test/control_00053456_QZS-4__MICHIBIKI-4__#42965U_20220808_1.000secs_2x2_Light.fit')
data = image[0].data

#Remove background and noise
sigma_clip = SigmaClip(sigma=3.0, maxiters=10)
bkg_estimator = MedianBackground()
bkg = Background2D(data, (50,50), filter_size=(3, 3), sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
data_nobkg = data - bkg.background #The cleaned data
image[0].data = data_nobkg
#image.writeto('test_nobkg.fits')
image.close()

#Get rough locations of sources
mean, median, std = np.mean(data_nobkg), np.median(data_nobkg), np.std(data_nobkg)
daofind = DAOStarFinder(fwhm=20.0, threshold=3.5*std)
sources = daofind(data_nobkg)
print(sources)

#Plot image and source detections
positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
apertures = CircularAperture(positions, r=4.)
norm = ImageNormalize(stretch=SqrtStretch())
plt.imshow(data_nobkg, cmap='Greys', origin='lower', norm=norm, interpolation='nearest')
apertures.plot(color='blue', lw=1.5, alpha=0.5)
plt.show()

#Build psf
#Specify size of cutouts and create a mask to not use stars on the edge of the image
size = 25
hsize = (size - 1) / 2
x = sources['xcentroid']
y = sources['ycentroid']
mask = ((x > hsize) & (x < (data_nobkg.shape[1] -1 - hsize)) &
        (y > hsize) & (y < (data_nobkg.shape[0] -1 - hsize)))  

#Remove stars on edge of image using mask
stars_tbl = Table()
stars_tbl['x'] = x[mask]
stars_tbl['y'] = y[mask]
nddata = NDData(data=data_nobkg)
stars = extract_stars(nddata, stars_tbl, size=size)
nrows = 5
ncols = 5
fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(20, 20), squeeze=True)
ax = ax.ravel()
for i in range(nrows * ncols):
    norm = simple_norm(stars[i], 'log', percent=99.)
    ax[i].imshow(stars[i], norm=norm, origin='lower', cmap='viridis')
epsf_builder = EPSFBuilder(oversampling=4, maxiters=3, progress_bar=True)
epsf, fitted_stars = epsf_builder(stars)
plt.imshow(epsf.data, norm=norm, origin='lower', cmap='viridis')
plt.colorbar()
plt.show()