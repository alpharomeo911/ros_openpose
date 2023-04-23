'''
@Implementation of MASK-RCNN using Detectron2 for RSS Final Project
@authors - Sarvesh
@affiliation - Northeastern University

To-Do --> Rewrite implementation using U-Net rather than detectron2.
^^^~~~ I don't know if I'll able to achieve this in the given time frame...

This script is a helper script that semantically segments object in 2D, 
extracts the point cloud from that region and publishes the pointnet, 
which are further subscribed by object detection methods like pointnet,
pointnet++ and DGCNN.

What works for now--
Segmenting the desired object - works
Generating point cloud of desired object - works
Able to publish point cloud - works but need to work with transforms!!!
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
_____________________________________________________________________
'''
#!/usr/bin/python3
# ^~ Shebang line, change it as per your system
# can be found using which command in terminal `which python3`

# v~ Necessary imports for the project
import numpy as np
import cv2
import message_filters
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import Header
from sensor_msgs.msg import Image, PointCloud, CameraInfo, PointCloud2, PointField
import rospy
import torch, detectron2
from detectron2.utils.logger import setup_logger
import numpy as np
import os, json, random
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
import open3d as o3d
from open3d_ros_helper import open3d_ros_helper as orh
import ros_numpy
import sys


class align_depth(object):
    '''
    @To-DO
    '''
    def __init__(self):
        self.rgb_image = None
        self.depth_image = None
        self.pcd = None
        self.rgbd = None
        self.bridge = CvBridge()
        self.loop_rate = rospy.Rate(0.25)
        
        self.depth_aligned = rospy.Publisher('/hsrb/head_rgbd_sensor/depth_registered/depth_aligned', Image, queue_size=10)
        self.image_sub = message_filters.Subscriber('/hsrb/head_rgbd_sensor/rgb/image_raw', Image)
        self.depth_sub = message_filters.Subscriber('/hsrb/head_rgbd_sensor/depth_registered/image_raw', Image)
        self.ts = message_filters.ApproximateTimeSynchronizer([self.image_sub, self.depth_sub], queue_size=100, slop=0.02)
        self.ts = message_filters.ApproximateTimeSynchronizer([self.image_sub, self.depth_sub], queue_size=100, slop=0.02)
        self.ts.registerCallback(self.project_2d_3d)
        self.pinhole_camera_intrinsic = o3d.camera.PinholeCameraIntrinsic()
        self.fx = 533.8970730178461
        self.fy = 534.3109677231259
        self.cx = 321.0284419169324
        self.cy = 241.1102341748379
        self.pinhole_camera_intrinsic.set_intrinsics(640, 480, 533.8970730178461, 534.3109677231259, 321.0284419169324, 241.1102341748379)


    def project_2d_3d(self, image_msg, depth_msg):
        rospy.loginfo('Message Received')
        # self.rgb_image = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')
        self.rgb_image = self.bridge.imgmsg_to_cv2(image_msg)
        self.depth_image = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding='16UC1')
        self.rgb_image = o3d.geometry.Image(self.rgb_image)
        self.depth_image = o3d.geometry.Image(self.depth_image)
        self.rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(self.rgb_image, self.depth_image, convert_rgb_to_intensity=False)
        self.depth_aligned.publish(self.bridge.cv2_to_imgmsg(self.rgbd))


    
    def start(self):
        rospy.loginfo('[+] hsr_cnn_detection_node fired!')
        rospy.spin()
        self.bridge = CvBridge()
        while not rospy.is_shutdown():
            self.rate.sleep()



if __name__ == '__main__':
    rospy.init_node('hsr_align_depth', anonymous=True)
    cnn_node = align_depth()
    cnn_node.start()
    