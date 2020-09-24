#!/usr/bin/env python3

# Common Imports
import rospy
import roslib

from harmoni_common_lib.constants import State, ActuatorNameSpace
from harmoni_common_lib.service_server import HarmoniServiceServer
from harmoni_common_lib.service_manager import HarmoniServiceManager
import harmoni_common_lib.helper_functions as hf

# Specific Imports
from std_msgs.msg import String, Bool
import numpy as np
import ast


class GestureService(HarmoniServiceManager):
    """
    Gesture service
    """

    def __init__(self, name, param):
        """ """
        super().__init__(name)
        self.gestures_name = []
        self.gestures_duration = []
        self.gesture_list_received = False
        self.gesture_done = False
        """ Setup Params """
        self.name = name
        self.service_id = hf.get_child_id(self.name)
        """ Setup the gesture """
        self.gesture_pub = rospy.Publisher(ActuatorNameSpace.gesture.value +self.service_id, String, queue_size=1)
        self.gesture_sub = rospy.Subscriber(
            ActuatorNameSpace.gesture.value + self.service_id + "/get_list",
            String,
            self._get_list_callback,
            queue_size=1,
        )
        self.gesture_done_sub = rospy.Subscriber(
            ActuatorNameSpace.gesture.value + self.service_id + "/done",
            Bool,
            self._gesture_done_callback,
            queue_size=1,
        )
        """Setup the gesture service as server """
        self.state = State.INIT
        self.setup_gesture()
        return

    def _gesture_done_callback(self, data):
        """Gesture done """
        if data.data:
            self.gesture_done = True


    def _get_list_callback(self, data):
        """Gesture list """
        if self.gestures_name == []:
            data = ast.literal_eval(data.data)
            self.gestures_name = filter(lambda b: b["name"], data)
            self.gestures_duration = filter(lambda b: b["duration"], data)
            self.gesture_list_received = True

    def setup_gesture(self):
        """ Setup the gesture """
        rospy.loginfo("Setting up the %s" % self.name)
        while not self.gesture_list_received:
            rospy.logdebug("Wait until gesture list received")
        rospy.loginfo("Received list of gestures")
        return

    def do(self, data):
        """ Do the speak """
        self.state = State.REQUEST
        self.actuation_completed = False
        if type(data) == str:
            data = ast.literal_eval(data)
        gesture_data = self._get_gesture_data(data)
        gesture = gesture_data["gesture"]
        timing = gesture_data["timing"]
        try:
            rospy.loginfo(f"length of data is {len(data)}")
            self.gesture_pub(gesture, timing)
            while not self.gesture_done:
                self.state= State.REQUEST
            self.state = State.SUCCESS
            self.actuation_completed = True
        except IOError:
            rospy.logwarn("gesture failed: Audio appears too busy")
            self.state = State.FAILED
            self.actuation_completed = True
        return

    def _get_gesture_data(data):
        """ Get only gesture data"""
        if type(data) == str:
            data = ast.literal_eval(data)
        behavior_data = ast.literal_eval(data["behavior_data"])
        behavior_set = []
        sentence = []
        for b in behavior_data:
            if "id" in b.keys():
                if b["id"] in self.gestures_name:
                    behavior_set.append(b)
            if "character" in b.keys():
                sentence.append(b["value"])
        ordered_gesture_data = list(
            sorted(behavior_set, key=lambda face: face["start"])
        )
        validated_gesture = []
        for fexp in ordered_facial_data:
            validated_gesture.append(self.gestures_name[fexp["id"]])
        if ordered_behaviors == []:
			rospy.loginfo("No gestures")
            return False
        #TODO!
		timing_word_behaviors = word_timing + gesture_behaviors
		ordered_timing_word_behaviors = sorted(timing_word_behaviors, key=lambda behavior: behavior["start"])
		start_time = rospy.Time.now()
		for index, behav in enumerate(ordered_timing_word_behaviors[:-1]):
			print(ordered_timing_word_behaviors[index])
			if behav["type"] != "word":
				print("Here")
				while rospy.Time.now()-start_time < rospy.Duration.from_sec(behav["start"]):
					pass
				gesture_timing = float(ordered_timing_word_behaviors[index +1]["start"]) #you cannot have a behavior sets at the end of the sentence
				rospy.loginfo("Play " + str(behav["id"]) + " at time:" + str(behav["start"]) + " with a duration of: " + str(gesture_timing))
				self.gesture_publisher.publish(gesture_timing, behav["id"])

		if ordered_timing_word_behaviors[len(ordered_timing_word_behaviors)-1]:
			if ordered_timing_word_behaviors[len(ordered_timing_word_behaviors)-1]["type"] != "word":
				print("Here")
				while rospy.Time.now()-start_time < rospy.Duration.from_sec(ordered_timing_word_behaviors[len(ordered_timing_word_behaviors)-1]["start"]):
					pass
				gesture_timing = float(ordered_timing_word_behaviors[len(ordered_timing_word_behaviors)-1]["start"]) #you cannot have a behavior sets at the end of the sentence
				rospy.loginfo("Play " + str(ordered_timing_word_behaviors[len(ordered_timing_word_behaviors)-1]["id"]) + " at time:" + str(ordered_timing_word_behaviors[len(ordered_timing_word_behaviors)-1]["start"]) + " with a duration of: " + str(gesture_timing))
				self.gesture_pub.publish(gesture_timing, ordered_timing_word_behaviors[len(ordered_timing_word_behaviors)-1]["id"])
			


def main():
    service_name = ActuatorNameSpace.gesture.name
    name = rospy.get_param("/name_" + service_name + "/")
    test = rospy.get_param("/test_" + service_name + "/")
    test_input = rospy.get_param("/test_input_" + service_name + "/")
    test_id = rospy.get_param("/test_id_" + service_name + "/")
    try:
        rospy.init_node(service_name)
        param = rospy.get_param(name + "/" + test_id + "_param/")
        if not hf.check_if_id_exist(service_name, test_id):
            rospy.logerr(
                "ERROR: Remember to add your configuration ID also in the harmoni_core config file"
            )
            return
        service = hf.set_service_server(service_name, test_id)
        s = GestureService(service, param)
        service_server = HarmoniServiceServer(name=service, service_manager=s)
        if test:
            rospy.loginfo("Testing the %s" % (service))
            rospy.sleep(1)
            s.gesture_pub.publish(test_input)
            rospy.loginfo("Testing the %s has been completed!" % (service))
        else:
            service_server.update_feedback()
            rospy.spin()
    except rospy.ROSInterruptException:
        pass


if __name__ == "__main__":
    main()
