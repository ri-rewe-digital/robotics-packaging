#!/usr/bin/env python3
import actionlib
import rosparam
import rospy
from ri_packing.msg import PackingResult, PackingGoal, PackingAction
from shape_msgs.msg import SolidPrimitive, geometry_msgs

from genetic_packing.geometry import Cuboid, Point, Space
from genetic_packing.solver import solve_packing_problem, SolutionPlacement


def read_config(file="/home/rutger/ideaworkspace/ri/robotics/src/ri_packing/config.yaml"):
    config_list=rosparam.load_file(file, default_namespace="packing")
    config_tuple=config_list[0]
    return config_tuple[0]



def create_paramaters():
    return read_config(rospy.get_param("packing_config_yaml"))


def decode_geometry_msg(request_geometries):
    product_boxes = []
    for sp in request_geometries:
        product_boxes.append(
            Cuboid(Point(sp.dimensions))
        )
    return product_boxes


def to_solid_primitive(solution_space: Space) -> SolidPrimitive:
    return SolidPrimitive(type=SolidPrimitive.BOX, dimensions=solution_space.dimensions().coords)


def to_location(solution_space: Space) -> geometry_msgs.msg.Point:
    o = solution_space.origin()
    return geometry_msgs.msg.Point(x=o[0], y=o[1], z=o[2])


def create_result(delivery_bins):
    result = PackingResult()
    result.products_geometries = []
    result.locations = []
    for del_bin in delivery_bins:
        placement_solution: SolutionPlacement
        for i, placement_solution in enumerate(delivery_bins[del_bin]):
            result.products_geometries.append(to_solid_primitive(placement_solution.space))
            result.locations.append(to_location(placement_solution.space))
    return result


def solve(packing_request: PackingGoal):
    geometry_message = packing_request.products_geometries

    if len(geometry_message) == 0:
        result = PackingResult()
        result.products_geometries = geometry_message
        result.locations = []
        server.set_aborted(result, "Packing aborted due to empty product-list")
        return
    product_boxes = decode_geometry_msg(geometry_message)
    delivery_bins: dict = solve_packing_problem(parameters=create_paramaters(), product_boxes=product_boxes)
    # TODO rb: think about feedback and preempt requests.
    # if server.is_preempt_requested():
    #     result.products_geometries = geometry_message
    #     result.locations = []
    #     server.set_preempted(result, "Timer preempted")
    #     return
    # feedback = TimerFeedback()
    # feedback.time_elapsed = rospy.Duration.from_sec(time.time() - start_time)
    # feedback.time_remaining = goal.time_to_wait - feedback.time_elapsed
    # server.publish_feedback(feedback)
    # update_count += 1
    # time.sleep(1.0)
    result = create_result(delivery_bins)
    server.set_succeeded(result, "Packing completed successfully")


rospy.init_node('ri_packing_action_server')
server = actionlib.SimpleActionServer('packing', PackingAction, solve, False)
server.start()
print("Packing server started successfully. Now listening on 'packing' topic.")
rospy.spin()
