#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat May 29 13:30:00 2014

@author: Chang Long Zhu
@email: changlongzj@gmail.com
"""


import rospy
import smach
from navigation_states.nav_to_poi import nav_to_poi
from speech_states.say import text_to_say
from gesture_states.search_wave_sm import Search_Wave_SM

# Some color codes for prints, from http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
ENDC = '\033[0m'
FAIL = '\033[91m'
OKGREEN = '\033[92m'
possible_pois = []

class Prepare_Data(smach.State):
    """
    State Machine that prepares the data, concretely the pois, for the 'Search Emergency Wave Room".
    It lists all the possible pois for the robot to search the person in emergency
    """
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeeded'], 
            input_keys=['possible_pois'],
            output_keys=['possible_pois'])

    def execute(self, userdata):
        aux_pois = rospy.get_param("/emergency_possible_pois/pois/emergency/")
        for poi_aux in aux_pois.keys():
            str(poi_aux).replace('_',' ')
            userdata.possible_pois.append(poi_aux)
            
        userdata.possible_pois = aux_pois.keys()
        
        rospy.sleep(1)
        return 'succeeded'

class Select_Possible_Poi(smach.State):
    """
    From the userdata, it selects a poi from the list, in order to get the robot to that location
    """
    
    def __init__(self):
        smach.State.__init__(self, outcomes=['succeeded', 'finished_searching'], 
                                input_keys=['possible_pois', 'n_item'],
                                output_keys=['n_item','standard_error', 'nav_to_poi_name_possible'])
    def execute(self, userdata):
        print "EXECUTE SELECT POSSIBLE POI"
        
        print "POIS:: ----- " + str(userdata.possible_pois)
        
        aux_possible = userdata.possible_pois.pop()
        
        userdata.nav_to_poi_name_possible = aux_possible
        rospy.loginfo("Possible Location POI:: " + str(aux_possible))
        userdata.n_item = userdata.n_item + 1
        
        print "Length of List:: " + str(len(userdata.possible_pois))
        
        if len(userdata.possible_pois) == 0:
            return 'finished_searching'
        
        rospy.loginfo("To Succeeded")
        return 'succeeded'


class Search_Emergency_Wave_Room_Change(smach.StateMachine):
    """
    Executes a SM that navigates to each room to detect a wave gesture, in order to find the person in emergency state.

    Required parameters:
    No parameters.

    Optional parameters:
    No optional parameters

    Input_keys:
        None
    Output Keys:
        @key poi_location: location of the emergency room
        @key wave_position: A PointStamped point referenced to /base_link
        @key wave_yaw_degree: the yaw for the wave position
    No io_keys.

    Nothing must be taken into account to use this SM.
    """
    def __init__(self):
        smach.StateMachine.__init__(self, 
                                    outcomes=['succeeded', 'preempted', 'aborted'],
                                    input_keys=[],
                                    output_keys=['poi_location', 'wave_position', 'wave_yaw_degree'])


        with self:           
            self.userdata.emergency_location = []
            self.userdata.tts_lang = 'en_US'
            self.userdata.tts_wait_before_speaking = 0
            self.userdata.possible_pois = []
            self.userdata.n_item = 0
                        
            smach.StateMachine.add(
                'Prepare_Data',
                Prepare_Data(),
                transitions={'succeeded': 'Search_Emergency'})
                
            smach.StateMachine.add(
                'Search_Emergency',
                Select_Possible_Poi(),
                transitions={'succeeded':'Say_Go_to_Room','finished_searching':'aborted'})
            
            smach.StateMachine.add(
                'Say_Go_to_Room',
                text_to_say("Now I am going to the next room"),
                transitions={'succeeded':'Navigate_to_Room','aborted':'aborted'})
            
            smach.StateMachine.add(
                'Navigate_to_Room',
                nav_to_poi(),
                remapping={'nav_to_poi_name':'nav_to_poi_name_possible'},
                transitions={'succeeded': 'Search_Wave', 'aborted': 'Navigate_to_Room', 'preempted': 'preempted'})
            
            smach.StateMachine.add(
                'Search_Wave',
                Search_Wave_SM(),
                transitions={'succeeded':'succeeded', 'preempted':'preempted', 'aborted':'aborted', 'end_searching':'Search_Emergency'})


def main():
    rospy.loginfo('Search Wave Detection Node')
    rospy.init_node('search_wave_detection_node')
    sm = smach.StateMachine(outcomes=['succeeded', 'preempted', 'aborted'])
    with sm:      
        smach.StateMachine.add(
            'Search_SM',
            Search_Emergency_Wave_Room_Change(),
            transitions={'succeeded': 'succeeded','preempted':'preempted', 'aborted':'aborted'})

    sm.execute()
    rospy.spin()

if __name__=='__main__':
    main()


