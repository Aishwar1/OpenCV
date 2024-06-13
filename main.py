import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Variable creation

width, height = 1920, 1080
folderPath = "Presentation"

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)  # 3 here tells the set func to set the width to 'width' it's a way to write it
cap.set(4, height)


# # Check if the camera opened successfully
# if not cap.isOpened():
#     print("Error: Could not open camera.")
# else:
#     print("Camera successfully opened with resolution:", width, "x", height)


# get the list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
# form a list to save the png images sort on the basis of len as so the 1 and 10 are sorted accordingly
# print(pathImages)

# variable
ImgNumber = 0
hs, ws = int(270*1), int(480*1)
gesturesThreshold = 400
buttonPressed = False  # func to iterate the loop when false then only it runs, when true it jumps into the other loop
buttonCounter = 0  # this is the number of times the frames run (count of loop)
buttonDelay = 20  # this represents the frames per second we have made
annotations = [[]]  # empty list for drawing, whenever a new point is there this will get append to it (list in list)
annotationStart = False
annotationNumber = 0


# hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)  # detector confidence
# hands=[]  # it's an empty list that store the information of hands

# Loop to continuously capture frames from the camera
while True:
    # Capture frame-by-frame
    success, img = cap.read()  # success boolean to see success
    img = cv2.flip(img, 1)  # we were getting inverted image as per the windows camera

    pathFullImage = os.path.join(folderPath, pathImages[ImgNumber])  # os.path = func that concat path of folderPath
    imgCurrent = cv2.imread(pathFullImage)  # reads the slides (imgCurrent is the slide images)

    from tkinter import Tk
    root = Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # Desired dimensions based on screen size
    target_width = screen_width
    target_height = screen_height
    target_aspect_ratio = target_width / target_height

    # Get the current dimensions of the image
    height1, width1 = imgCurrent.shape[:2]
    current_aspect_ratio = width1 / height1

    # Resize while maintaining aspect ratio
    if current_aspect_ratio > target_aspect_ratio:
        # Image is wider than target aspect ratio
        new_width = target_width
        new_height = int(target_width / current_aspect_ratio)
    else:
        # Image is taller than target aspect ratio
        new_width = int(target_height * current_aspect_ratio)
        new_height = target_height

    resized_img = cv2.resize(imgCurrent, (new_width, new_height))

    # Calculate padding if needed
    pad_x = (target_width - new_width) // 2
    pad_y = (target_height - new_height) // 2

    # Pad the image to fit the screen dimensions
    padded_img = cv2.copyMakeBorder(resized_img, pad_y, pad_y, pad_x, pad_x, cv2.BORDER_CONSTANT, value=[0, 0, 0])

    hands, img = detector.findHands(img)

    # this hand is important as it stores the coordinates or something cause findHands gives a tuple of 2 values
    # cv2.line(img, (0, gesturesThreshold), (width, gesturesThreshold), (0, 255, 0), 10)
    # now these two are coordinates of the starting and the ending point

    if hands and buttonPressed == False:
        hand = hands[0]  # (1st hand detection) as we do only have one hand
        fingers = detector.fingersUp(hand)  # a function that provides a list of fingers that are up and what are down
        cx, cy = [0, 0]  # got the center coordinates but we don't need it
        lmList = hand['lmList']  # landmark list we call it

        # constrain values for easier drawing
        w: int = imgCurrent.shape[0]  # to get the w defined
        # indexFingers = lmList[8][0],lmList[8][1] #these are index fingers
        xVal = int(np.interp(lmList[8][0], [width//4, w], [0, width]))  # converting the value to small values
        yVal = int(np.interp(lmList[8][1], [70, height-70], [0, height]))  # x and y Val are 1st and 2nd fingers
        indexFingers = xVal, yVal  # x and y coordinates

        # print(fingers)

        if cy <= gesturesThreshold:  # the hand is at the height of face
           # gesture 1 : left
           if fingers == [1, 0, 0, 0, 0]:
               print("left")
               buttonPressed = True  # if it's here the true thing then left won't print when were at the 0th slide
               annotationStart = False
               if ImgNumber > 0:  # for 0 it's important to put buttonPressed, if loop else wise also it's not affect
                   annotations = [[]]
                   annotationNumber = 0
                   ImgNumber -= 1

           # gesture 2 : Right
           if fingers == [0, 0, 0, 0, 1]:
               print("Right")
               buttonPressed = True
               annotationStart = False
               if ImgNumber < len(pathImages)-1:
                   annotations = [[]]
                   annotationNumber = 0
                   ImgNumber += 1

        # show pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(padded_img, indexFingers, 6, (0, 0, 255), cv2.FILLED)
            annotationStart = False

        # Draw pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(padded_img, indexFingers, 6, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFingers)
        else:
            annotationStart = False

        # Eraser
        if fingers == [0, 1, 1, 1, 0]:
           if annotations:
               if annotationNumber >= 0:
                   annotations.pop(-1)
                   annotationNumber -= 1
                   buttonPressed = True

    else:
        annotationStart = False

    # as soon as buttonPressed gets True
    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    # for i, annotation in enumerate(annotations):
    w, h, _ = padded_img.shape
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(padded_img, annotations[i][j-1], annotations[i][j], (0, 0, 255), 6)


# Display the resulting frame
#     cv2.imshow('Image', img)
    # Adding webcam to the slides
    imgSmall = cv2.resize(img, (ws, hs))
    w, h, _ = padded_img.shape  # _ is color channel RGB which we aren't using
    padded_img[0:hs, w+185:w+ws+185] = imgSmall  # this is a matrix we're overlaying it
    cv2.imshow('Slides', padded_img)


# Wait for 1 ms and check if the 'q' key is pressed
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
