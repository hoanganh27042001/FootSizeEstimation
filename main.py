from sklearn.cluster import KMeans
import random as rng
import cv2
import imutils
import argparse
from imutils import contours
from skimage.io import imread
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image
import streamlit as st

from utils import *

ImgPath = 'images/23840.jpeg'


def main():
    st.title("Foot size estimation ")
    st.markdown(
        """
        **Requirements:**
        
        - Printer Paper is used as a reference (Height/Width is known and White background will help in Preprocessing)
        - Foot should be in center, touching one edge of paper.
        - Floor color should be different than white.
        - Paper should be completely visible (with 4 corners) in the image.
        - No other objects are included in the image.
        - Avoid the foot shadow in the image.
        """
    )
    image_file = st.file_uploader("Choose an image", type = ["png", "jpg", "jpeg"])
    menu = ["", "Height", "Width"]
    choice = st.selectbox("Measurement: ", menu)
    if image_file is not None:
        # To See Details
        file_details = {"filename": image_file.name, "filetype": image_file.type,
                        "filesize": image_file.size}
        # st.write(file_details)
        st.image(Image.open(image_file), 'Uploaded image', width=250)
        oimg = imread(image_file)


        if not os.path.exists('output'):
            os.makedirs('output')

        st1, st2, st3 = st.columns(3)
        st4, st5, st6 = st.columns(3)
        preprocessedOimg = preprocess(oimg)
        # cv2.imwrite('output/preprocessedOimg.jpg', preprocessedOimg)
        st1.image(preprocessedOimg,'1. Gaussian blur', width = 250)

        clusteredImg = kMeans_cluster(preprocessedOimg)
        # cv2.imwrite('output/clusteredImg.jpg', clusteredImg)
        st2.image(clusteredImg, '2. cluster with kmeans', width = 250)


        edgedImg = edgeDetection(clusteredImg)
        # cv2.imwrite('output/edgedImg.jpg', edgedImg)
        st3.image(edgedImg, '3. edge detection', width = 250)

        warped = extractPaper(edgedImg)
        # cv2.imwrite('output/warped.jpg', warped)
        st4.image(warped, '4. warped image', width = 250)

        crop = cropOrig(warped)
        # cv2.imwrite('output/croppedImg.jpg', crop)
        # st.image(crop, '5. crop foot', width = 250)

        overlay = overlayImage(crop, warped)
        # cv2.imwrite('output/overlayImg.jpg', overlay)
        st5.image(overlay,'5. crop foot', width = 250)

        fedged = edgeDetection(crop)
        draw, boundRect = getBoundingBox(fedged)
        # cv2.imwrite('output/fdraw.jpg', draw)
        st6.image(draw, '6. foot measurement', width = 250)

        print("feet size (cm): ", calcFeetSize(warped, boundRect))
        st.write("Estimated foot size (cm): ", calcFeetSize(warped, boundRect))

if __name__ == '__main__':
    main()