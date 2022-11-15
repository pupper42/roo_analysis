from astropy.io import fits

axy = fits.open("corr.fits")

print(axy[1].data)