from skimage.io import imread
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from imutils import contours
import argparse
import imutils
import cv2
from sklearn.cluster import KMeans
import random as rng

def preprocess(img):
  # img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
  # img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

  img = cv2.GaussianBlur(img, (9, 9), 0)
  img = img/255

  return img

def plotImage(img):
  plt.imshow(img)
  plt.show()

# empirical crop 10% of original image to get foot
def cropOrig(oimg):
  # x (Horizontal), y (Vertical Downwards) are start coordinates
  x1, y1, w1, h1 = 0, 0, oimg.shape[1], oimg.shape[0]
  y2 = int(h1/10)
  x2 = int(w1/10)

  crop = oimg[y1+y2:h1-y2,x1+x2:w1-x2]
  return crop

# display the crop foot in the original paper image
def overlayImage(crop, oimg):
  x1, y1, w1, h1 = 0, 0, oimg.shape[1], oimg.shape[0]

  y2 = int(h1/10)

  x2 = int(w1/10)
  new_image = np.zeros((oimg.shape[0], oimg.shape[1]), np.uint8)
  new_image[:, 0:oimg.shape[1]] = 100 # (B, G, R)

  new_image[ y1+y2:y1+y2+crop.shape[0], x1+x2:x1+x2+crop.shape[1]] = crop
  return new_image

def kMeans_cluster(img):
  # For clustering the image using k-means, we first need to convert it into a 2-dimensionary array
  # (H*W, N) N is the channel = 3
  image_2D = img.reshape(img.shape[0]*img.shape[1], img.shape[2])

  # tweak the cluster size and see what happens to the output
  kmeans = KMeans(n_clusters = 2, random_state = 0).fit(image_2D)
  clustOut = kmeans.cluster_centers_[kmeans.labels_]

  # Reshape back the image from 2D to 3D image
  clustered_3D = clustOut.reshape(img.shape[0], img.shape[1], img.shape[2])

  clusteredImg = np.uint8(clustered_3D*255)
  return clusteredImg

def getBoundingBox(img):
  contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  c = max(contours, key=cv2.contourArea) # filter the largest contours

  contours_poly = cv2.approxPolyDP(c, 3, True)
  boundRect = cv2.boundingRect(contours_poly)

  # print('contours poly: ', contours_poly)
  # print('bounding rectangle: ', boundRect)
  drawing = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

  paperbb = boundRect

  color = (0, 255, 0)
  cv2.drawContours(drawing, [contours_poly], 0, color)
  cv2.rectangle(drawing, (int(paperbb[0]), int(paperbb[1])), \
            (int(paperbb[0]+paperbb[2]), int(paperbb[1]+paperbb[3])), color, 2)
  return drawing, boundRect


def extractPaper(img):
    print('img shape:', img.shape)
    print(len(cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)))
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    c = max(contours, key=cv2.contourArea)

    # print('found contours', contours)
    # contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
    # print('sorted contours: ', contours)
    rect = cv2.minAreaRect(c)
    box = cv2.boxPoints(rect)
    box = np.intp(box)
    # box = np.array(box, dtype='int')

    # get width and height of the detected rectangle
    width = int(rect[1][0])
    height = int(rect[1][1])

    src_pts = box.astype("float32")
    # coordinate of the points in box points after the rectangle has been
    # straightened
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    # the perspective transformation matrix
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # directly warp the rotated rectangle to get the straightened rectangle
    warped = cv2.warpPerspective(img, M, (width, height))
    print('warped shape: ', warped.shape)
    # plt.imshow(warped)
    # plt.show()
    return warped

def edgeDetection(clusteredImage):
  edged1 = cv2.Canny(clusteredImage, 0, 255)
  edged = cv2.dilate(edged1, None, iterations = 1)
  edged = cv2.erode(edged, None, iterations = 1)
  return edged


def calcFeetSize(pcropedImg, fboundRect):
    x1, y1, w1, h1 = 0, 0, pcropedImg.shape[1], pcropedImg.shape[0]

    y2 = int(h1 / 10)
    x2 = int(w1 / 10)
    fh = y2 + fboundRect[3]
    fw = x2 + fboundRect[2]
    ph = pcropedImg.shape[0]
    pw = pcropedImg.shape[1]

    print("Feet height: ", fh)
    print("Feet Width: ", fw)

    print("Paper height: ", ph)
    print("Paper width: ", pw)

    opw = 210
    oph = 297

    ofs_w = 0
    ofs_h = 0
    if fw > fh:
        ofs_h = (oph / pw) * fw
        ofs_w = (opw / pw) * ph
    else:
        ofs_h = (oph / ph) * fh
        ofs_w = (opw / pw) * fw

    return round(ofs_h / 10, 2), round(ofs_w / 10, 2)