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
        height, width = calcFeetSize(warped, boundRect)

        height_size = [24.4, 24.8, 25.2, 25.7, 26, 26.5, 26.8, 27.3, 27.8, 28.3, 28.6, 29.4]
        Size_VN_h = ['40', '40-41', '41', '41-42', '42', '42-43', '43', '43-44', '44-45', '45', '46']
        Size_UK_h = ['6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '12']
        Size_US_h = ['7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12', '13']

        width_size = [9.8, 10, 10, 10.2, 10.2, 10.4, 10.4, 10.6, 10.6, 10.8, 10.8, 11, 11]
        Size_VN_w = ['38', '38-39', '39', '39-40', '40','40-41', '41', '41-42', '42', '42-43', '43', '43-44', '44']
        Size_UK_w = ['4.5', '5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5']
        Size_US_w = ['5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11']
        menu = ["Height", "Width"]
        choice = st.selectbox("Measurement: ", menu)
        if choice == 'Height':
            st.write('The estimated height is: {} cm'.format(height))
            index = -1
            for i in range(len(height_size)-1):
                if height_size[i] <= height <= height_size[i+1]:
                    index = i

            if index >=0:
                st.write('The suitable size by foot height is: ')
                st.write('+ Size VN: {}\n + Size UK: {}\n + Size US: {}'.format(Size_VN_h[index], Size_UK_h[index], Size_US_h[index]))
            else:
                st.write('Cannot estimate size')
        elif choice == 'Width':
            st.write('The estimated height is: {} cm'.format(width))
            index = -1
            for i in range(len(width_size)-1):
                if width_size[i] <= width < width_size[i + 1]:
                    index = i

            if index >= 0:
                st.write('The suitable size by foot width is: ')
                st.write('+ Size VN: {}\n + Size UK: {}\n + Size US: {}'.format(Size_VN_w[index], Size_UK_w[index],
                                                                                Size_US_w[index]))
            else:
                st.write('Cannot estimate size')
if __name__ == '__main__':
    main()