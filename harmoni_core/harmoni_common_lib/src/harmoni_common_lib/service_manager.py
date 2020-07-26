#!/usr/bin/env python3

# Importing the libraries
import rospy
import roslib


class HarmoniServiceManager(object):
    """
    Service manager for the harware reading and internal service servers.
    Individual service managers overwrite the parent public functions.
    """

    def __init__(self, state):
        rospy.loginfo("Init the service manager state")
        self.state = state

    def update(self, state):
        self.state = state
        rospy.loginfo("Update the state to %i" % state)
        return

    def test(self):
        """ Test the hardware, sending default action """
        return

    # FIXME this rate is not used and it also depends on being set by HarwareReadingServer which calls the start function without the rate argument.
    def start(self, rate):
        """ Start reading or processing data """
        return

    def pause(self):
        """ Pause reading or processing data """
        return

    def stop(self):
        """ Stop reading or processing data """
        return

    def reset_init(self):
        """ Reset harware variables to initial state """
        return


class HarmoniExternalServiceManager(object):
    """
    Service manager for the harware control and external service servers.
    Individual service managers overwrite the parent public functions.
    """

    def __init__(self, state):
        rospy.loginfo("Init the direct service manager")
        self.response_received = False
        self.actuation_completed = False
        self.result_msg = ""
        self.state = state

    def test(self):
        """ Test the hardware, sending default action """
        return

    def update(
        self, state, actuation_completed="", response_received="", result_msg=""
    ):
        self.response_received = response_received  # True if action completed
        self.state = state  # Used IF logic can dictate control flow
        self.result_msg = result_msg  # String
        self.actuation_completed = actuation_completed
        return

    def request(self, rate):
        """ Do a request """
        return

    def do(self, data):
        """ Do an action """
        return data

    def reset_init(self):
        """ Reset harware variables to initial state """
        self.response_received = False
        self.result_msg = ""
        return