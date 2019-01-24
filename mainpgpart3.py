#!/usr/bin/env python

#-------------------------------------------------------------------------------------------
# Multiple methods were tried before I pushed this code on git, out of which this method seemed to suit the two videos the best
# I have tried to write the code to be as independent of the videos as possible. However, I belive major changes can be done here.
# like, the edge detection and thresholding can be symmetrical to just isolate the lanes and remove a lot of unecessary regions from the final image
# A few methods I tried were as follows
# => Slope difference method => Slope average method => Polyfitting using linalg in numpy 
# => Second degree poly fitting => Gamma/normal correction for overexposed image frames => Overlap of thresholds 
# As I had already made a custom message for the slope and intercept, I just incorporated the aacln part into it.
#--------------------------------------------------------------------------------------------

import numpy as np
import rospy
import cv2
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import String
from sensor_msgs.msg import Image
import math
from lane_detc.msg import lane
from lane_detc.msg import accln

#global variables 
l_x = []
l_y = []
r_x = []
r_y = []
a1 = []
a2 = []
i = -1
mna = 0
mnd = 0
pub = rospy.Publisher('lane_coeff', lane , queue_size=1)   
pub2 = rospy.Publisher('acceleration', accln , queue_size=1)

#Function to decide the acceleration 
def speedselec( slp ):
    global mnd, mna

    if mnd > 3 or mna >2:
       mnd = 0 if mnd > 3 else mnd
       mna = 0 if mna > 2  else  mna 
       return "MAINTAIN"
    elif slp < 0 and ( abs( slp) < 1.2 and abs(slp) > 0.5 ):
       mnd = mnd + 1
       return "DECCELERATE"
    elif slp > 0 and ( abs( slp) < 0.8 and abs(slp) > 0.6 ):
       mnd = mnd + 1
       return "DECCELERATE"
    else:
       mna = mna + 1
       return "ACCELERATE"    

#function to draw complete lanes on img by fitting a polynomial to the entered data 
def lanedraw(img, m_x, m_y, min_y, max_y, rl):

    poly_right = np.poly1d( np.polyfit( m_y, m_x, deg=1 ) )
    m_x_start = int(poly_right(max_y))
    m_x_end = int(poly_right(min_y))
    msg = lane()
    msg2 = accln()

    slope = float( max_y - min_y ) / float( m_x_start - m_x_end )
    msg.slope = slope
    msg.intercept = max_y - m_x_start * slope
    msg2.accln = speedselec( slope )
    if not rospy.is_shutdown():
          pub.publish(msg)
          pub2.publish(msg2)

    return m_x_start, m_x_end

#function to draw the lines output from Hough line transform
def draw_lines(img, lines):
    
    if lines is None:
            return
    
    img_1 = np.copy(img)
    line_img = np.zeros( ( img_1.shape[0], img_1.shape[1], 3 ), dtype=np.uint8, )

    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(line_img, (x1, y1), (x2, y2), [0,0,255], 5)

    img_1 = cv2.addWeighted(img_1, 0.8, line_img, 1.0, 0.0)
        
    return img_1

#main function
def mainpg():
    rospy.init_node('mainpg', anonymous=True) 
    sub = rospy.Subscriber('lane_img', Image, callback, queue_size=20 )
    rate = rospy.Rate(20)
    print "subscribed to lane_img"
    rospy.spin() 


def callback(data):

     global a1, a2, i

    # Checks if any valid data is passed or not
     if data is None:
       print "no image recieved. aborting."
       exit(0)
     else:
       print "received image!"
       i = i + 1
       
     # Converts input image to Opencv supported format
     bridge = CvBridge() 
     img = bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")      


     #Converts image to HSV color space to isolate yellow and white lanes
     gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
     hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
     lowerthresh = np.array([20, 100, 100], dtype = "uint8")
     upperthresh = np.array([30, 255, 255], dtype= "uint8" ) #threshold for detecting yellow

     img_blurhsv = cv2.GaussianBlur(hsv, (3,3), 0)
     mask_y = cv2.inRange(img_blurhsv, lowerthresh, upperthresh)
     img_blurgray = cv2.GaussianBlur(gray_img, (5,5), 0)
     mask_w = cv2.inRange(img_blurgray, 200, 255) 
     mask_yw = cv2.bitwise_or(mask_w, mask_y)
     maskimg = cv2.bitwise_and(gray_img, mask_yw)

     # Applies canny edge detector after removing the noise and changing to grayscale
     dst = cv2.Canny(maskimg, 50, 200, None, 3)     
  
 
     # crops a region of interest
     imshape = dst.shape
     point1 = [ 0, imshape[0] * 0.90 ]
     point3 = [ imshape[1] * 0.5, imshape[0] * 0.55 ]
     point5 = [ imshape[1], imshape[0] * 0.90 ] 
     
     vertices1 = [ np.array([point1, point3, point5],dtype=np.int32) ]      
     mask = np.zeros_like(dst)
       
     cv2.fillPoly(mask, vertices1, 255)
     masked_image = cv2.bitwise_and(dst, mask)

     global r_x, r_y, l_x, l_y
     cnt1 = 0
     cnt2 = 0

     #Hough line transform, the method is taken from the opencv documention on this line transform.
     lines = cv2.HoughLinesP( masked_image, rho=6, theta=np.pi / 60, threshold=160, minLineLength=40, maxLineGap=40 ) # were 40 and 40 before

     line_image = draw_lines(img, lines)
     
     if line_image is not None:

        for line in lines:
           for x1, y1, x2, y2 in line:
             
             slope = float(y2 - y1) / float(x2 - x1) 

             if abs( slope ) < 0.50:
                continue

             elif slope > 0:
 
                l_x.extend([x1, x2])
                l_y.extend([y1, y2])
                cnt1 = cnt1 + 2
             elif slope < 0:
               
                r_x.extend([x1, x2])
                r_y.extend([y1, y2])
                cnt2 = cnt2 + 2
             else:
                 continue

        a1.append(cnt1)
        a2.append(cnt2)

     else: 
        a1.append(0) #<= if no lines are found on one image, this forces the use of previously fitted polynomial
        a2.append(0)
     
  
     if ( i == 1 ) and ( a1[0] is 0 ) and ( a2[0] is  0 ):
        print "No lines found in the first image. Aborting this iteration"
        i = i - 1
        exit(0)
 
     p = len(a1) - 1
     q = len(a2) - 1


     #Decides whether to continue the lines or not. Pops the previous values from arrays.
     #A stack-esque implementation to memorise previous values for a smooth lane transition at curves.  
     #Another part can be added by the 'and' conjunction to calibrate popping at sepecific values of i
     #however, as you increase the i threshold, memory space needed also increases
     #Max length for any of the global arrays was noted to be 40 (for i>1), which approximates to 20 max lines detected in one of the frames. (harder challenge)
     if i>1:
        if ( a1[p] is not 0):
           for m in range( a1.pop(0) ):
                   del l_x[0:1]
                   del l_y[0:1]
        else:
           del a1[p]

        if ( a2[q] is not 0 ):
           for m in range( a2.pop(0) ):
                    del r_x[0:1]
                    del r_y[0:1] 
        else:
           del a2[q]    

     
     #lines are drawn here          
     min_y = img.shape[0]
     max_y = int ( img.shape[0] * 0.75 )

     if ( l_x or l_y ) and ( r_x or r_y ): 

        left_x_start, left_x_end = lanedraw(img, l_x, l_y, min_y, max_y, 1)
        right_x_start, right_x_end = lanedraw(img, r_x, r_y, min_y, max_y, 0)
        line_img = draw_lines( img, [[[left_x_start, max_y, left_x_end, min_y], [right_x_start, max_y, right_x_end, min_y]]])

            
     elif ( r_x or r_y ): 

        right_x_start, right_x_end = lanedraw(img, r_x, r_y, min_y, max_y, 0)
        line_img = draw_lines( img, [[[right_x_start, max_y, right_x_end, min_y]]])
                    
     elif ( l_x or l_y ):          
            
        left_x_start, left_x_end = lanedraw(img, l_x, l_y, min_y, max_y, 1)
        line_img = draw_lines( img, [[[left_x_start, max_y, left_x_end, min_y]]])
 
     else:    
        print "problems occured!"
        exit(0)
     

     cv2.imshow("second", line_img)
     cv2.waitKey(50)
         
               

if __name__ == '__main__':
     try:
         mainpg()
         cv2.destroyAllWindows()
     except rospy.ROSInterruptException:
         pass
