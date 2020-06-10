#!/usr/bin/env python3

# Importing the libraries
import rospy
import roslib
from harmoni_common_lib.behavior_pattern import BehaviorPatternService
from harmoni_common_lib.constants import *

class DialogueState():
    SENSING = "pc_microphone_default"
    SPEECH_DETECTING = "harmoni_stt_default"
    DIALOGING = "harmoni_lex_default"
    SYNTHETIZING = "harmoni_tts_default"
    SPEAKING = "pc_speaker_default"
    EXPRESSING = "pc_face_default"
    MOVING = ""
    
class DialogingPattern(BehaviorPatternService):
    """
    Dialoging pattern class
    """
    def __init__(self, sequence, loop):
        """Init the behavior pattern """
        super().__init__(self.result_callback, self.feedback_callback)
        self.sequence = sequence
        self.loop = loop
        self.count = -1
        self.count_loop = -1
        self.end_sequence = False
        self.end_single_loop = False
        self.end_looping = False 
        self.action_info = {
            DialogueState.DIALOGING: {"router": Router.DIALOGUE.value, "action_goal": ActionType.REQUEST},
            DialogueState.SENSING: {"router": Router.SENSOR.value, "action_goal": ActionType.ON} ,
            DialogueState.SYNTHETIZING: {"router": Router.ACTUATOR.value, "action_goal": ActionType.REQUEST} ,
            DialogueState.SPEAKING: {"router": Router.ACTUATOR.value, "action_goal": ActionType.REQUEST} ,
            DialogueState.EXPRESSING: {"router": Router.ACTUATOR.value, "action_goal": ActionType.REQUEST} ,
            DialogueState.MOVING: {"router": Router.ACTUATOR.value, "action_goal": ActionType.REQUEST},
            DialogueState.SPEECH_DETECTING: {"router": Router.DETECTOR.value, "action_goal": ActionType.ON}
        }

    def result_callback(self, result):
        """ Do something when result has been received """
        rospy.loginfo("The result has been received")
        data = result
        if result["do_action"]:
            if not self.end_sequence:
                self.do_sequence(data["message"])
            elif not self.end_looping and self.end_sequence:
                self.do_loop(data)["message"]
        else:
            # if the dialogue intent is finalized
            #END THE BEHAVIOR PATTERN
            print("END BEHAVIOR PATTERN. DO SOMETHING.")
        return

    def feedback_callback(self, feedback):
        """ Send the feedback state to the Behavior Pattern tree to decide what to do next """
        rospy.logdebug("The feedback is %s" %feedback)
        return 

    def _get_action_info(self, action):
        """Get action info """
        self.state = action
        child_server = action
        router = self.action_info[child_server]["router"]
        action_goal = self.action_info[child_server]["action_goal"]
        return (child_server, router, action_goal)

    def do_sequence(self, data):
        """
        Do sequence, Update state and send the goal according to the current state
        
        Args:
            data: are the optional data to input to the service
        """
        self.count += 1  
        action = self.sequence[self.count]
        if isinstance(action, list):
            for item in action: # If it is an array, it means that is a parallel actions, so I start multiple goals
                [child_server, router, action_goal] = self._get_action_info(item)
        else:
            [child_server, router, action_goal] = self._get_action_info(action)
        optional_data = data
        super().start(action_goal, child_server, router, optional_data)
        self.update(self.state)
        if self.count == len(self.sequence):
            print("End of the sequence")
            self.end_sequence = True
        return

    def do_loop(self, data):
        """
        Do loop, Update state and send the goal according to the current state
        
        Args:
            data: are the optional data to input to the service
        """
        self.count += 1
        action = self.loop[self.count]
        if isinstance(action, list):
            for item in action: # If it is an array, it means that is a parallel actions, so I start multiple goals
                [child_server, router, action_goal] = self._get_action_info(item)
        else:
            [child_server, router, action_goal] = self._get_action_info(action)
        optional_data = data
        self.update(self.state)
        super().start(self, action_goal, child_server, router, optional_data)
        if self.count == len(self.loop):
            print("End of the single loop")
            self.end_single_loop = True
            self.count_loop += 1
            self.count = -1
            if self.end_looping:
                print("End looping")
        return

    def stop(self):
        pass
        

def main():
    trigger_intent = "Hey"
    parallel = [DialogueState.SPEAKING, DialogueState.EXPRESSING]
    sequence = [DialogueState.DIALOGING, DialogueState.SYNTHETIZING, parallel]
    loop = [DialogueState.SENSING, DialogueState.SPEECH_DETECTING, DialogueState.DIALOGING, DialogueState.SYNTHETIZING, parallel]
    try:
        rospy.init_node("dialoging_pattern")
        dp = DialogingPattern(sequence, loop)
        dp.do_sequence(data = trigger_intent)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
