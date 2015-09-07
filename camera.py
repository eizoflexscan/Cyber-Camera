import cv2
import winsound, sys
import os
import mailer
from threading import Thread
import time
import config
import datetime
class VideoCamera(object):
    binary = True
    def __init__(self, config):
        self.config = config
        self.video = cv2.VideoCapture(int(self.config.get('Video')['camera']))
        self.videoWriter = None
        self.online = False
    
    def __del__(self):
        self.video.release()
        
    def finished(self):
        self.video.release()
        
    def start_video(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.videoWriter = cv2.VideoWriter(self.config.get('File')['videos'] +'video' +timestr +".avi", cv2.cv.CV_FOURCC('M','J','P','G'), int(self.config.get('Video')['fps']),
               (640,480))

    def start(self,sens, method, mail, sound, notif):
        self.online = False
        print "staring..."
        iterator = 0
        count = 0
        while True:
            success, image = self.video.read()
            if not success:
                continue
            iterator += 1
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            if method == 'face':
                faceCascade = cv2.CascadeClassifier("faceDetect.xml")
            elif method == 'ubody':
                faceCascade = cv2.CascadeClassifier("haarcascade_upperbody.xml")
            elif method == 'fbody':
                faceCascade = cv2.CascadeClassifier("haarcascade_fullbody.xml")
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                 )
            if type(faces) is not tuple:
                count+=1
            if self.online:
                print "Stopped by User"
                return
            if count == 6 - sens:
                print "Face Detected!"
                img = self.get_frame(False)
                if notif:
                    try:
                        print "sending Image to mail....."
                        mailer.send_notification(self.config)
                    except:
                        print "ERROR"
                if mail:
                    try:
                        print "sending Image to mail....."
                        mailer.sendMessege(img, self.config)
                        return
                    except:
                        print "ERROR"
                if sound:
                    winsound.PlaySound(self.config.get('Other')['alarm'], winsound.SND_FILENAME)
                return  
            if iterator==5:
                iterator=0
                count=0

    def endVideo(self):
        self.videoWriter.release()
        
    def get_frame(self,faced,saved=False, video=False, videoStop = False):
        while True:
            success, image = self.video.read()
            if not success:
                continue
            else:
                break
        if saved:
            cv2.imwrite("image.jpg",image)
        if video:
            self.videoWriter.write(image)
            cv2.circle(image,(20,20), 15, (0,0,255), -1)
        if faced:
            faceCascade = cv2.CascadeClassifier("faceDetect.xml")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            ret, jpeg = cv2.imencode('.jpg', image)
            return (jpeg.tostring())
        ret, jpeg = cv2.imencode('.jpg', image)
        return (jpeg.tostring())
