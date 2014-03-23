#! /usr/bin/env python

import rospy
import smach




class Listen_Comands(smach.State):

    def __init__(self):
        smach.State.__init__(
            self,
            outcomes=['succeeded', 'aborted','preempted'],input_keys=['standard_error'],output_keys=['standard_error'])

    def execute(self, userdata):
        rospy.sleep(2)
        userdata.standard_error="Dummy"
        return 'succeeded'
     
class Follow_operator(smach.State):

    def __init__(self):
        smach.State.__init__(
            self,
            outcomes=['succeeded', 'aborted','preempted'],input_keys=['standard_error'],output_keys=['standard_error'])

    def execute(self, userdata):
        rospy.sleep(2)
        userdata.standard_error="Dummy"
        return 'succeeded'

#Defining the state Machine of follow_me 1st part
class follow_me_1st(smach.StateMachine):
    """
    Executes a SM that do the first part of the follow_me.
    This part consist in follow the operator,
    2 person it will cross, one of them it will stops for 3 seconds 
    this part of the follow_me it will be finished when the robot 
    arrives to the "small room"
    
    It creates a concurrence state machine for:
        Listen
        Follow
    
    """
    def __init__(self):
# Concurrence
         smach.Concurrence.__init__(self,outcomes=['succeeded', 'aborted', 'preempted', 'endTime'],
                                        default_outcome='succeeded',
                                        input_keys=['id_learn_person'],
                                        output_keys=['standard_error'])
         
         with self:
   
                # Go around the room 
                smach.Concurrence.add('Follow_operator', Follow_operator()) 
                           
                # Move head
             #   smach.Concurrence.add('move_head', DummyStateMachine())
                smach.Concurrence.add('Listen_Comands', Listen_Comands())
                
                  
           

