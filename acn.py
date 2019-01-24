#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from lane_detc.msg import accln

def callback(data):
    print "The acceleration verdict is:", data.accln 

def main():
    rospy.init_node('main', anonymous=True) 
    sub = rospy.Subscriber('acceleration', accln, callback, queue_size=20 )
    print "subscribed to acceleration"
    rospy.spin()

if __name__ == '__main__':
     try:
         main()
     except rospy.ROSInterruptException:
         pass
