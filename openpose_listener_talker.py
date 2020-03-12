#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import String
from sensor_msgs import Image
# import for openpose processing use
import sys
import cv2
import os
from sys import platform
import argparse


# Import Openpose (Windows/Ubuntu/OSX)
dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    # Windows Import
    if platform == "win32":
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append(dir_path + '/../../python/openpose/Release');
        os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
        import pyopenpose as op
    else:
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append('../../python');
        # !!! NEED TO MAKE SURE THE OPENPOSE PATH IS CORRECT OTHERWISE IT WON"T WORK!!!
        # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
        # sys.path.append('/usr/local/python')
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e
# Custom Params (refer to include/openpose/flags.hpp for more parameters)
params = dict()
params["model_folder"] = "../../../models/"

def process(data):
    # rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Process Image
    datum = op.Datum()
    imageToProcess = cv2.imread(args[0].image_path)
    datum.cvInputData = imageToProcess
    opWrapper.emplaceAndPop([datum])

    pub = rospy.Publisher('/openpose/data', String, queue_size=10)
    rospy.init_node('openpose_talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        # hello_str = "hello world %s" % rospy.get_time()
        # rospy.loginfo(hello_str)
        pub.publish(str(datum.poseKeypoints))
        rate.sleep()

    # # Display Image
    # print("Body keypoints: \n" + str(datum.poseKeypoints))
    # cv2.imshow("OpenPose 1.5.1 - Tutorial Python API", datum.cvOutputData)
    # cv2.waitKey(0)

    
def openpose_listener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('openpose_listener', anonymous=True)
    # The anonymous=True flag tells rospy to generate a unique name for the node so that you can have multiple listener.py nodes run easily.

    rospy.Subscriber("/camera/color/image_raw", Image, process)
    # This declares that your node subscribes to the /camera/color/image_raw topic 
    # which is of type Image. When new messages are received, callback is invoked with the message as the first argument.

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    openpose_listener()