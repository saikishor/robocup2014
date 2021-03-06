#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri May 6 17:40:00 2014

@author: Chang Long Zhu Jin
@email: changlongzj@gmail.com
"""

import smach
import rospy

import smach_ros
from smach_ros import SimpleActionState, ServiceState

from reem_tabletop_grasping.msg import ObjectManipulationAction, ObjectManipulationActionGoal,ObjectManipulationActionResult, ObjectManipulationGoal
from object_recognition_msgs.msg import ObjectType, RecognizedObject, RecognizedObjectArray
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped

OPERATION_PICK = 1
OPERATION_PLACE = 2
OBJECT_MANIPULATION_TOPIC = '/object_manipulation_server_dual_arms'
GROUP_NAME = 'right_arm_torso'


class Prepare_data(smach.State):
    def __init__(self, object_position_std):
        smach.State.__init__(self, 
                             outcomes = ['succeeded', 'aborted'], 
                             input_keys = ['object_position'], 
                             output_keys = ['object_pick_position'])
        self.object_position = object_position_std
        
    def execute(self, userdata):
        if not self.object_position and not userdata.object_position:
            rospy.logerr("No Object to Detect")
            return 'aborted'
        #Object Position is a PoseStamped --> Deprecated
        #userdata.object_pick_position = self.object_position if self.object_position else userdata.object_position
        
        #Need to transform object_position (PoseWithCovarianceStamped) to object_pick_position (PoseStamped)
        object_covariance = self.object_position if self.object_position else userdata.object_position
        object_stamped = PoseStamped()
        object_stamped.header = object_covariance.header
        object_stamped.pose = object_covariance.pose
        userdata.object_pick_position = object_stamped
        return 'succeeded'

class Prepare_Pick_Goal(smach.State):
    def __init__(self):
        smach.State.__init__(self, 
                             outcomes = ['succeeded', 'aborted'], 
                             input_keys = ['object_pick_position'], 
                             output_keys = ['object_manipulation_goal'])
        
    def execute(self, userdata):
        goal_to_send = ObjectManipulationGoal()
        goal_to_send.operation = ObjectManipulationGoal.PICK
        goal_to_send.group = GROUP_NAME
        
        goal_to_send.target_pose = userdata.object_pick_position
        
        userdata.object_manipulation_goal = goal_to_send
        print "Data to Send to Pick Object final --> " + str(goal_to_send)
        return 'succeeded'        

class pick_object_sm(smach.StateMachine):
    def __init__(self, object=''):
        smach.StateMachine.__init__(self, 
                                    outcomes=['succeeded', 'preempted', 'aborted'],
                                    input_keys=['object_position'],
                                    output_keys=[])
        with self:
            smach.StateMachine.add("Prepare_data", 
                                   Prepare_data(object), 
                                   transitions={'succeeded':'Pick_Object_Goal','aborted':'aborted'})
            
            smach.StateMachine.add('Pick_Object_Goal',
                                   Prepare_Pick_Goal(),
                                   transitions={'succeeded':'Pick_Object'})
            
            smach.StateMachine.add('Pick_Object', 
                                SimpleActionState(OBJECT_MANIPULATION_TOPIC,
                                                   ObjectManipulationAction,
                                                   goal_key='object_manipulation_goal',
                                                   input_keys=['standard_error'],
                                                   output_keys=['standard_error']), 
                                transitions={'succeeded':'succeeded', 'aborted':'aborted'})
            

                