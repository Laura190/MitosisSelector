# README

Author: Laura Cooper, camdu@warwick.ac.uk

## Description

Automatically detects dividing cells from images stored in OMERO. A set of time
points are exported for each cell so that the user can manually identify the
different stages of mitosis. The results are saved and returned to OMERO.

Assumes 2D+t or 3D+t image stacks, will skip images with only 1 time point.

## Installation

Required packages:
- omero-py
- scikit-image
- pyqt5
- pandas

## Usage

### Processing

1. Click 'Settings' and enter the appropriate details for you data.
    - Channel: Enter the number of the channel that shows mitosis
    - Duration: Approximate number of time frames to capture full mitosis
    - Nuclei Diameter: Approximate diameter of nuclei or cells
    - Stages to select: Enter of the names of the stages to select separated by commas.
2. Click 'Save'. This will overwrite the default settings, so they don't need to be changed for each image
3. Enter OMERO image ID, username, password and server address into the appropriate boxes
4. Click 'Run' and wait for the processing to finish.
5. Close and reopen app (or click next?)
