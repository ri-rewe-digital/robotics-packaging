import actionlib
import roslib
import rospy
import yaml
from ri_packaging.msg import PackagingResult, PackagingGoal, PackagingAction
from shape_msgs.msg import SolidPrimitive, geometry_msgs

from geometry import Cuboid, Point, Space
from src.packaging_solver import solve_packing_problem, SolutionPlacement

roslib.load_manifest('basics')


def read_config(file="config.yaml"):
    with open(file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


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
    result = PackagingResult()
    result.products_geometries = []
    result.locations = []
    for del_bin in delivery_bins:
        placement_solution: SolutionPlacement
        for i, placement_solution in enumerate(delivery_bins[del_bin]):
            result.products_geometries.append(to_solid_primitive(placement_solution.space))
            result.locations.append(to_location(placement_solution.space))
    return result


def solve(packaging_request: PackagingGoal):
    geometry_message = packaging_request.products_geometries

    if len(geometry_message) == 0:
        result = PackagingResult()
        result.products_geometries = geometry_message
        result.locations = []
        server.set_aborted(result, "Packaging aborted due to empty product-list")
        return
    product_boxes = decode_geometry_msg(geometry_message)
    delivery_bins: dict = solve_packing_problem(parameters=read_config(), product_boxes=product_boxes)
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
    server.set_succeeded(result, "Timer completed successfully")


rospy.init_node('ri_packaging_action_server')
server = actionlib.SimpleActionServer('packer', PackagingAction, solve, False)
server.start()
rospy.spin()
