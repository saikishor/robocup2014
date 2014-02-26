#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Cristina De Saint Germain
@email: crsaintc8@gmail.com

26 Feb 2014
"""

import rospy
import smach
from navigation_states.nav_to_poi import nav_to_poi

# Some color codes for prints, from http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
ENDC = '\033[0m'
FAIL = '\033[91m'
OKGREEN = '\033[92m'

class DummyStateMachine(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeeded','aborted', 'preempted'], 
            input_keys=[], 
            output_keys=[])

    def execute(self, userdata):
        print "Dummy state just to change to other state"  # Don't use prints, use rospy.logXXXX

        rospy.sleep(3)
        return 'succeeded'

# Class that prepare the value need for nav_to_poi
class prepare_location(smach.State):
    def __init__(self):
         smach.State.__init__(self, outcomes=['succeeded','aborted', 'preempted'], 
            input_keys=[], 
            output_keys=['nav_to_poi_name']) 

    def execute(self,userdata):
        userdata.nav_to_poi_name='find_me'
        return 'succeeded'


class FindMeSM(smach.StateMachine):
    """
    Executes a SM that does the test find me and go over there.
    The robot recognize one TC and it must reconize this person inside a room.
    When it do it, it must go to the side that the TC indicates. 


    Required parameters:
    No parameters.

    Optional parameters:
    No optional parameters


    No input keys.
    No output keys.
    No io_keys.

    Nothing must be taken into account to use this SM.
    """
    def __init__(self):
        smach.StateMachine.__init__(self, ['succeeded', 'preempted', 'aborted'])

        with self:
            # We must initialize the userdata keys if they are going to be accessed or they won't exist and crash!
            self.userdata.nav_to_poi_name=''
            
            # Save the data from the TC
            smach.StateMachine.add(
                'save_face',
                DummyStateMachine(),
                transitions={'succeeded': 'prepare_location', 'aborted': 'aborted', 
                'preempted': 'preempted'}) 

            # Prepare the info to go to the room
            smach.StateMachine.add(
                'prepare_location',
                prepare_location(),
                transitions={'succeeded': 'go_location', 'aborted': 'aborted', 
                'preempted': 'preempted'})  

            # Go to the location
            smach.StateMachine.add(
                'go_location',
                nav_to_poi(),
                transitions={'succeeded': 'find_person', 'aborted': 'aborted', 
                'preempted': 'preempted'})    

            # Find a particular person 
            smach.StateMachine.add(
                'find_person',
                DummyStateMachine(),
                transitions={'succeeded': 'go_to_person', 'aborted': 'aborted', 
                'preempted': 'preempted'}) 

            # Go to the person - We assume that find person will return the position for the person
            smach.StateMachine.add(
                'go_to_person',
                DummyStateMachine(),
                transitions={'succeeded': 'say_found', 'aborted': 'aborted', 
                'preempted': 'preempted'})     

            # Say "I found you!"
            smach.StateMachine.add(
                'say_found',
                DummyStateMachine(),
                transitions={'succeeded': 'gesture_recognition', 'aborted': 'aborted', 
                'preempted': 'preempted'}) 

            # Recognize the direction
            smach.StateMachine.add(
                'gesture_recognition',
                DummyStateMachine(),
                transitions={'succeeded': 'go_side', 'aborted': 'aborted', 
                'preempted': 'preempted'})    

            # Go to the direction
            smach.StateMachine.add(
                'go_side',
                DummyStateMachine(),
                transitions={'succeeded': 'succeeded', 'aborted': 'aborted', 
                'preempted': 'preempted'})    

           
