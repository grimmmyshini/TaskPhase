#!/usr/bin/env python

import numpy as np
import sys
import rospy
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import time

def img_publisher():
    
   pub = rospy.Publisher( 'lane_img', Image, queue_size=100) 
   rospy.init_node('img_publisher', anonymous = True)
   rate = rospy.Rate(50000)  
   bridge = CvBridge()
   
   strm = sys.argv[1]
   print "Fetching video stream..."
   vid = cv2.VideoCapture(strm)

   if not vid.isOpened():
      print "stream failed to open. Aborting"
      time.sleep(5)
      exit(0)
   
   print "stream successfully opened."
   retval, scrn = vid.read()

   while retval and not rospy.is_shutdown():
        cv2.imshow("Stream:", scrn)
        cv2.waitKey(500)
        retval, scrn = vid.read()

        if scrn is not None:
           scrn = np.uint8(scrn)
           image_msg = bridge.cv2_to_imgmsg(scrn, encoding="passthrough")
           pub.publish(image_msg)
           rate.sleep()
    
   cv2.destroyWindow("Stream:")


if __name__ == '__main__':
    try:
        img_publisher()
    except rospy.ROSInterruptException:
        pass

