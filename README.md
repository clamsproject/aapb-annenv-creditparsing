# Annotation Environment for Credits and Slates parsing

## Overview
This directory contains the gold-standard annotation environment for "role-filler binding" (RFB) data. The most recent iteration of the RFB model uses a different "BIO" annotation structure based in NER, and uses training data generated from "silver standard" LLM outputs. 
- To use/view that environment, see the `llm-silver-anno` directory. 
- To use/view the original gold-standard annotation environment, see this (top-level) directory

## Installation
* Create a virtual environment `conda create -n annotate python=3.8`
* Activate the virtual environment `conda activate annotate`
* Install the app requirements `pip install -r requirements.txt`

## Run OCR Preprocessing
`python ocr.py <directory_of_images>`

## Run Annotation Environment
`streamlit run main.py <directory_of_images>:<annotation_output_directory>`

### Input and Output Directories
* `<directory_of_images>` is the directory containing the images to be annotated and is the only
volume that can be mounted to the container image
* `<annotation_output_directory>` is the directory where the annotations will be saved. This directory will always
be a subdirectory of the mounted volume `<directory_of_images>`

## Running in Container
> **Note:** Containerization does not currently support the OCR preprocessing step.
> Running in a container will require the user to run the OCR preprocessing step first
* `docker build -t annotation_env .`
* `docker run -p 8501:8501 -v <directory_of_images>:/app/images annotation_env <directory_of_images>:<annotation_output_directory>`

## Usage
* For each image, annotate each Key-Value pair in the Annotation container
* Click on the `KEY` or `VALUE` buttons with OCR output to copy the OCR output to the corresponding text box. Will
append to existing text in the text box with a space in between
* After annotating the whole image, there are four options:
  * Click `Next Frame` to save your annotations and move to the next image
  * Click `Continuing Credits` to append your annotations to the previous image and move to the next image. (This will 
continue to append to the first image in this continuing chain until `Next Frame` is clicked)
  * Click `Duplicate Frame` to mark the current image as a duplicate of the previous image
  * Click `Skip Frame` to skip the current image after indicating the reason for skipping
    * Could be due to an unreadable image or an image with data not applicable to the current task
* If there is an error in the annotations for a given image, set the index in the `Delete Annotation` container to
the index of the annotation to be deleted and click `Delete Key-Value Pair`
* OCR output is color coded to indicate the confidence of the OCR output. 
  * <span style="color:green">Green</span> indicates high confidence
  * <span style="color:orange">Orange</span> indicates medium confidence
  * <span style="color:red">Red</span> indicates low confidence

## Screenshot
<img src="docs/UI_screenshot.png" alt="annotation environment" width="700">



# InterAnnotator Agreement Assessment
IAA Calculations by Dean Cahill have been added to this repository. 

This calculates the difference in annotations across annotators. Currently, the IAA calc is only between two annotators.
Please go to [/raw_annotation_iaa_assessment](/raw_annotation_iaa_assessment). 
The IAA metric is handled currently as an IOU metric between sets of strings.  
TODO: Explanation of the IAA calculation tba.

Round 2 was created around date 240201, and is on a previous Annotation Guideline, probably around v3.5. 
Round 3 was created around date 240223, and is on the Annotation Guideline [v5.2](https://docs.google.com/document/d/1Kxa99JMfDuy-y2xFqmgPkuLnLqEGhNB8iMxBT3E1Tx4/edit) or v5.3.

Please see the [RFB Visualizer v2 README.md](https://github.com/clamsproject/RFB_annotation_visualizer/blob/v2-adjudicator-buttons/README.md)
for more information on how to do Adjudication. 

