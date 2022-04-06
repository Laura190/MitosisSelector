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
from skimage.io import imsave, imread
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
    # Set dimensions of image
    zct_list = [(z, c, t) for z in range(img.getSizeZ())]
    pixels = img.getPrimaryPixels()
    # Read in data one plane at a time
    return np.array(list(pixels.getPlanes(zct_list)))


def pullOMERO(username, password, server, imageId, channel, stages):
    """
    Get image pixel and metadata from OMERO.
    Apply maximum projection in Z and in t
    Input: username  str  OMERO username
           password  str  User's Password
           server    str  Address of OMERO server
           imageId   int  OMERO ID of image to processing
           channel   int  Index of relevant channel
           stages    str  Stages of mitosis to identify (separate with commas)
    """
    colNames = ['Cell', 'x0', 'y0', 'x1', 'y1', 't0', 't1']
    colNames = colNames + stages.split(',')
    df = pd.DataFrame(columns=colNames)
    try:
        with BlitzGateway(username, password, host=server, port='4064', secure=True) as conn:
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
        return df, sizeX, sizeY, scaleX, maxPrj, maxZPrj, image
    except Exception as e:
        print(e)


def pullLocal(file, stages):
    # sizeX = float(input("sizeX: ") or "1")
    # sizeY = float(input("sizeY: ") or "1")
    # scaleX = float(input("scaleX: ") or "1")
    # TO DO: Pull info from image metadata? Or user input
    colNames = ['Cell', 'x0', 'y0', 'x1', 'y1', 't0', 't1']
    colNames = colNames + stages.split(',')
    df = pd.DataFrame(columns=colNames)
    image = imread(file)
    if len(image.shape) != 4:
        print("Image must have 4 dimensions")
    else:
        maxZPrj = np.max(image, axis=1)
        maxPrj = np.max(maxZPrj, axis=0)
    return df, 1, 1, 1, maxPrj, maxZPrj
    # return df, sizeX, sizeY, scaleX, maxPrj, maxZPrj


def find_rois(df, maxPrj, sizeX, sizeY, box_size):
    """
    Use a method to identify regions of interest. Create rectangles around
    centroid, which are within the limits of the image
    """
    # df dataframe to store results
    thresh = threshold_yen(maxPrj)
    bw = closing(maxPrj > thresh, square(3))
    cleared = clear_border(bw)
    label_image = label(cleared)
    for count, region in enumerate(regionprops(label_image)):
        # take regions with large enough areas
        if region.area >= 10:  # Approx diameter of bright spots
            # draw rectangle around segmented cells
            y0, x0 = region.centroid
            # Ensure numbers aren't negative
            minr = max(0, y0-float(box_size)/2)
            minc = max(0, x0-float(box_size)/2)
            maxr = min(sizeY, minr + box_size)
            maxc = min(sizeX, minc + box_size)
            comb = pd.DataFrame.from_dict([{'Cell': int(count), 'x0': int(minc), 'x1': int(maxc),
                                           'y0': int(minr), 'y1': int(maxr)}])
            df = pd.concat([df, comb])
    return df


def create_roi(conn, img, shapes):
    # helper function for creating an ROI and linking it to new shapes
    updateService = conn.getUpdateService()
    # create an ROI, link it to Image
    roi = omero.model.RoiI()
    # use the omero.model.ImageI that underlies the 'image' wrapper
    roi.setImage(img._obj)
    for shape in shapes:
        roi.addShape(shape)
    # Save the ROI (saves any linked shapes too)
    return updateService.saveAndReturnObject(roi)


def save_rois_to_omero(df, username, password, server, imageId):
    with BlitzGateway(username, password, host=server, port='4064', secure=True) as conn:
        image = conn.getObject('Image', imageId)
        # for cell, corner in enumerate(corners):
        for index, roi in df.iterrows():
            # Create roi and push to OMERO
            rect = omero.model.RectangleI()
            rect.x = rdouble(roi['x0'])
            rect.y = rdouble(roi['y0'])
            rect.width = rdouble(roi['x1']-roi['x0'])
            rect.height = rdouble(roi['y1']-roi['y0'])
            comment = 'Cell '+str(roi['Cell'])
            rect.textValue = rstring(comment)
            create_roi(conn, image, [rect])


def rois_to_pngs(df, maxZPrj, duration, imageId=False):
    # Get time series for each cell and save frames as pngs
    for index, row in df.iterrows():
        roi = maxZPrj[int(row['y0']):int(row['y1']),
                      int(row['x0']):int(row['x1'])]
        # Find the brighttest time in the Max Z projection stack
        if not imageId:
            maxAtEachTime = [np.max(roi[i, :, :]) for i in range(roi.shape[0])]
        else:
            maxAtEachTime = [np.max(roi[:, :, i]) for i in range(roi.shape[2])]
        maxTime = maxAtEachTime.index(max(maxAtEachTime))
        # Get substack, 20 is total number of time frames
        startTime = max(0, maxTime-round(duration))
        endTime = min(roi.shape[2], maxTime + round(duration))
        if not imageId:
            substack = roi[startTime:endTime, :, :]
        else:
            substack = roi[:, :, startTime:endTime]
        df.iloc[index].at['t0'] = startTime
        df.iloc[index].at['t1'] = endTime
        # Save each plane of substack as .png
        for k in range(substack.shape[2]):
            plane = substack[:, :, k]
            # Rescale histogram of each plane
            minusMin = plane - np.min(plane)
            plane = (minusMin/np.max(minusMin)) * 255
            plane = plane.astype(np.uint8)
            imName = "tmp/Image_%s/Cell%04dTime%04d.png" % (
                imageId, index, k+startTime)
            imsave(imName, plane)
    df.to_csv('tmp/Image_%s/Results.csv' % imageId, index=False)


if __name__ == "__main__":
    username = str(input("Username: ") or "public")
    password = getpass()
    server = str(input("Server: ") or "camdu.warwick.ac.uk")
    imageId = int(input("Image ID: ") or "1000")
    channel = int(input("Channel: ") or "0")
    nucleiDiameter = int(input("Nuclei Diameter: ") or "20")
    stages = str(input("Mitosis stages: ") or "Anaphase,Prophase")
    df, sizeX, sizeY, scaleX, maxPrj, maxZPrj, image = pullOMERO(
        username, password, server, imageId, channel)
    box_size = 2*np.ceil(nucleiDiameter/scaleX)
    df = find_rois(df, maxPrj, sizeX, sizeY, box_size)
    print(df)
