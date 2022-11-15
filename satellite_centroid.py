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
data_folder = "220502_qzs3_astrometrynet/"
image = fits.open(data_folder + '00051021_QZS-3__MICHIBIKI-3__#42917U_20220502_1.000secs_2x2_Light.fit')
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