#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis
#       Error Resilience Analysis for JPEG 2000
#

import PIL
import math
import numpy
import cv2
import sys

# Calculate Peak Signal to Noise Ratio (PSNR) of two images
# Implementented according to: https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio
def calculate_psnr(reference_image_name, filename):
    '''Calculate Peak Signal to Noise Ratio (PSNR) of two images'''
    print("[INFO] Pocitam PSNR ...")
    try:
        original = cv2.imread(reference_image_name)
        contrast = cv2.imread(filename)

        #print("Original:" + str(original))
        #print("Contrast:" + str(contrast))


        mse = numpy.mean((original - contrast) ** 2)
        if mse == 0:
            return 100
        PIXEL_MAX = 255.0
        #return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))
        return 10 * math.log10( (PIXEL_MAX ** 2) / mse)
    except:
        return -1


if __name__ == '__main__':
    result = calculate_psnr(str(sys.argv[1]), str(sys.argv[2]))
    print("PSNR: ", result)

