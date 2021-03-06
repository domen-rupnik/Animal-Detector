#!/usr/bin/python
# import the necessary packages
import sys

nova_pot = ['/usr/lib/python37.zip', '/usr/lib/python3.7', '/usr/lib/python3.7/lib-dynload',
            '/home/pi/.local/lib/python3.7/site-packages', '/usr/local/lib/python3.7/dist-packages',
            '/usr/lib/python3/dist-packages']
for i in nova_pot:
    sys.path.append(i)
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
from time import sleep
import cv2
import datetime
from mail import Emailer
import RPi.GPIO as GPIO

start = datetime.datetime.utcnow()
pogoj = False
snemaj = False
uzgan = False
gibanje = datetime.datetime.utcnow()
# do some stuff

channel_onoff = 27
channel_record = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel_onoff, GPIO.OUT)
GPIO.setup(channel_record, GPIO.OUT)

def on(pin):
    GPIO.output(pin, GPIO.HIGH)  # Turn motor on
def off(pin):
    GPIO.output(pin, GPIO.LOW)  # Turn motor off

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=700, help="minimum area size")
args = vars(ap.parse_args())
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
# otherwise, we are reading from a video file
else:
    vs = cv2.VideoCapture(args["video"])
# initialize the first frame in the video stream
firstFrame = None
# loop over the frames of the video
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    frame = vs.read()
    frame = frame if args.get("video", None) is None else frame[1]
    text = "Unoccupied"
    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if frame is None:
        break
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # if the first frame is None, initialize it
    if firstFrame is None:
        start = datetime.datetime.utcnow()
        firstFrame = gray
        continue
    end = datetime.datetime.utcnow()
    duration = (end - start).total_seconds()
    if duration > 10:
        start = datetime.datetime.utcnow()
        firstFrame = gray
        continue
    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        gibanje = datetime.datetime.utcnow()
        snemaj = True



    if snemaj and uzgan == False:
        on(channel_onoff)
        time.sleep(.5)
        off(channel_onoff)
        on(channel_record)
        time.sleep(1)
        off(channel_record)
        uzgan = True
    if snemaj and (datetime.datetime.now() - gibanje).total_seconds() > 30:
        snemaj = False
        off(channel_record)
        on(channel_onoff)
        time.sleep(.5)
        off(channel_onoff)

    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break
# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()


