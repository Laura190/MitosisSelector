# Packages
# OMERO
import omero
from omero.gateway import BlitzGateway
from omero.rtypes import rdouble, rstring
# skimage
from skimage.filters import threshold_yen
from skimage.morphology import closing, square
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.io import imsave
# Data
import numpy as np
import pandas as pd
# Files and Folders
import os.path
import errno
from shutil import copy
# Progress bar
from tqdm import tqdm
# User inputs
from getpass import getpass

def get_z_stack(img, c=0, t=0):
        """
        Convert OMERO image object to numpy array
        Input: img  OMERO image object
               c    number of colour channls
               t    number of time steps
        """
        zct_list = [(z, c, t)
                    for z in range(img.getSizeZ())]  # Set dimensions of image
        pixels = img.getPrimaryPixels()
        # Read in data one plane at a time
        return np.array(list(pixels.getPlanes(zct_list)))

def pullOMERO(username,password,server,imageId,channel):
    try:
        with BlitzGateway(username, password,host=server, port='4064',secure=True) as conn:
                message = "Connected to OMERO, processing..."
                print(message)
                image = conn.getObject('Image', imageId)
                if image is None:
                    message = "Image %s not found, process ended" % imageId
                    print(message)
                else:
                    sizeT = image.getSizeT()
                    sizeX = image.getSizeX()
                    sizeY = image.getSizeY()
                    p = image.getPrimaryPixels()._obj
                    scaleX = p.getPhysicalSizeX().getValue()
                    # If multiple time steps, create max projection for each time
                    if sizeT > 1:
                        for t in tqdm(range(sizeT)):
                            zStack = get_z_stack(image, channel, t)
                            if t == 0:
                                maxZPrj = np.max(zStack, axis=0)
                            else:
                                maxZPrj = np.dstack(
                                    [maxZPrj, np.max(zStack, axis=0)])
                        maxPrj = np.max(maxZPrj, axis=2)
                        np.save('maxPrj.npy', maxPrj)
                        np.save('maxZPrj.npy', maxZPrj)
                    else:
                        message = "Image %s has only one time point, skipping processing" % imageId
        return sizeX, sizeY, scaleX, maxPrj, maxZPrj, image
    except Exception as e:
        print(e)


if __name__ == "__main__":
    username = str(input("Username:") or "public")
    password = getpass()
    server = str(input("Server:") or "camdu.warwick.ac.uk")
    imageId = int(input("Image ID:") or "1000")
    channel = int(input("Channel:") or "0")
    results = pullOMERO(username,password,server,imageId,channel)
    print(results)
    
    
