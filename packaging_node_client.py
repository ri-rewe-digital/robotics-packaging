import csv

import actionlib
import roslib
import rospy
from ri_packaging.msg import PackagingAction, PackagingGoal, PackagingFeedback
from shape_msgs.msg import SolidPrimitive

roslib.load_manifest('basics')


def read_csv_data(file="data/product_boxes.csv"):
    packaging_goal = PackagingGoal()
    with open(file, 'r') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            count = int(row['count'])
            index = 0
            while index < count:
                packaging_goal.products_geometries.append(
                    SolidPrimitive(type=SolidPrimitive.BOX,
                                   dimensions=[int(row['width']), int(row['depth']), int(row['height'])])
                )
                index += 1
    return packaging_goal


# RB: no feedback sent at the moment
def feedback_cb(feedback: PackagingFeedback):
    print('[Feedback] Current generation: {}'.format(feedback.generation))
    print('[Feedback] Generations remaining: {}'.format((feedback.total_generations - feedback.generation)))


rospy.init_node('packaging_node_client')
client = actionlib.SimpleActionClient('packaging_node_client', PackagingAction)
client.wait_for_server()

goal = PackagingGoal()
goal.products_geometries = read_csv_data()

# Uncomment this line to test server-side abort:
# goal.time_to_wait = rospy.Duration.from_sec(500.0)

client.send_goal(goal, feedback_cb=feedback_cb)

# Uncomment these lines to test goal preemption:
# time.sleep(3.0)
# client.cancel_goal()
client.wait_for_result()
print("[Result] State: {}".format((client.get_state())))
print('[Result] Status: {}'.format(client.get_goal_status_text()))
print('[Result] Time elapsed: {}'.format((client.get_result().time_elapsed.to_sec())))
print('[Result] Updates sent: {}'.format(client.get_result().updates_sent))
