#!/usr/bin/env python3
import csv

import actionlib
import rospy
from shape_msgs.msg import SolidPrimitive

from ri_packing.msg import PackingAction, PackingGoal, PackingFeedback, PackingResult


def read_csv_data(file="/home/rutger/ideaworkspace/ri/robotics/src/ri_packing/data/product_boxes.csv"):
    packaging_goal = PackingGoal()
    with open(file, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            count = int(row['count'])
            index = 0
            while index < count:
                print("Adding a box: {}".format(row))
                packaging_goal.products_geometries.append(
                    SolidPrimitive(type=SolidPrimitive.BOX,
                                   dimensions=[int(row['width']), int(row['depth']), int(row['height'])])
                )
                index += 1
    return packaging_goal


# RB: no feedback sent at the moment
def feedback_cb(feedback: PackingFeedback):
    print('[Feedback] Current generation: {}'.format(feedback.generation))
    print('[Feedback] Generations remaining: {}'.format((feedback.total_generations - feedback.generation)))


rospy.init_node('packing_action_client')
client = actionlib.SimpleActionClient('packing', PackingAction)
print("going to wait for packing server")
client.wait_for_server()

print("going to read data")
goal = read_csv_data(rospy.get_param("data_file"))

# Uncomment this line to test server-side abort:
# goal.time_to_wait = rospy.Duration.from_sec(500.0)
print("going to send data")
client.send_goal(goal, feedback_cb=feedback_cb)

# Uncomment these lines to test goal preemption:
# time.sleep(3.0)
# client.cancel_goal()
client.wait_for_result()
print("[Result] State: {}".format((client.get_state())))
print('[Result] Status: {}'.format(client.get_goal_status_text()))
result: PackingResult = client.get_result()
print('[Result] Updates: {}'.format(result.updates_sent))
print('[Result] locations: {}'.format(result.locations))
print('[Result] products_geometries: {}'.format(result.products_geometries))
