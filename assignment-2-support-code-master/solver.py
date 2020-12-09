import sys
import random
import math
import time

from problem_spec import ProblemSpec
from robot_config import write_robot_config_list_to_file
from tester import test_config_equality, test_obstacle_collision, test_environment_bounds, test_self_collision
from angle import Angle
from robot_config import make_robot_config_from_ee1, make_robot_config_from_ee2

"""
Template file for you to implement your solution to Assignment 2. Contains a class you can use to represent graph nodes,
and a method for finding a path in a graph made up of GraphNode objects.

COMP3702 2020 Assignment 2 Support Code
"""


class GraphNode:
    """
    Class representing a node in the state graph. You should create an instance of this class each time you generate
    a sample.
    """

    def __init__(self, spec, config):
        """
        Create a new graph node object for the given config.

        Neighbors should be added by appending to self.neighbors after creating each new GraphNode.

        :param spec: ProblemSpec object
        :param config: the RobotConfig object to be stored in this node
        """
        self.spec = spec
        self.config = config
        self.neighbors = []

    def __eq__(self, other):
        return test_config_equality(self.config, other.config, self.spec)

    def __hash__(self):
        return hash(tuple(self.config.points))

    def get_successors(self):
        return self.neighbors

    @staticmethod
    def add_connection(n1, n2):
        """
        Creates a neighbor connection between the 2 given GraphNode objects.

        :param n1: a GraphNode object
        :param n2: a GraphNode object
        """
        n1.neighbors.append(n2)
        n2.neighbors.append(n1)


def find_graph_path(spec, init_node):
    """
    This method performs a breadth first search of the state graph and return a list of configs which form a path
    through the state graph between the initial and the goal. Note that this path will not satisfy the primitive step
    requirement - you will need to interpolate between the configs in the returned list.

    You may use this method in your solver if you wish, or can implement your own graph search algorithm to improve
    performance.

    :param spec: ProblemSpec object
    :param init_node: GraphNode object for the initial configuration
    :return: List of configs forming a path through the graph from initial to goal
    """
    # search the graph
    init_container = [init_node]

    # here, each key is a graph node, each value is the list of configs visited on the path to the graph node
    init_visited = {init_node: [init_node.config]}

    while len(init_container) > 0:
        current = init_container.pop(0)

        if test_config_equality(current.config, spec.goal, spec):
            # found path to goal
            return init_visited[current]

        successors = current.get_successors()
        for suc in successors:
            if suc not in init_visited:
                init_container.append(suc)
                init_visited[suc] = init_visited[current] + [suc.config]

    return None


def generate_config(spec):
    """
    Generates a random RobotConfig object
    :param spec: ProblemSpec object
    :return: RobotConfig object
    """
    angles = []
    lengths = []

    for i in range(spec.num_segments):
        angles.append(Angle(degrees=random.randint(-165, 165)))
        lengths.append(random.uniform(spec.min_lengths[i], spec.max_lengths[i]))

    next_node = make_robot_config_from_ee1(spec.initial.get_ee1()[0], spec.initial.get_ee1()[1], angles, lengths,
                                           spec.initial.ee1_grappled, spec.initial.ee2_grappled)

    return next_node


def sample_config(spec):
    """
    Creates two random RobotConfig objects. If non-grappled EE of only one RobotConfig collides with an obstacle, then
    the other RobotConfig is returned.
    :param spec: The ProblemSpec object
    :return: RobotConfig Object, otherwise None
    """
    # TODO: MAKE THIS SO THAT IT CHECKS COORDINATES OF 2 END EFFECTORS TO DECIDE WHETHER TO SAMPLE POINT
    # Right now this is uniform random sampling
    config = generate_config(spec)

    collides = test_obstacle_collision(config, spec, spec.obstacles)

    if collides:
        return config
    else:
        return None


def interpolate_path(start_config, end_config, is_end, spec):
    """
    produces a series of primitive steps between two RobotConfigs
    :param start_config: Beginning RobotConfig to check
    :param end_config: End RobotConfig to check
    :param is_end: Whether a path has been found
    :param spec: The ProblemSpec object defining problem
    :return: List of primitive steps if valid, None otherwise
    """
    primitive_steps = []
    angle_diffs = []
    length_diffs = []
    primitive_angles = []
    primitive_lengths = []

    for i in range(len(start_config.ee1_angles)):
        angle_diffs.append(end_config.ee1_angles[i].in_radians() - start_config.ee1_angles[i].in_radians())
        length_diffs.append(end_config.lengths[i] - start_config.lengths[i])

    abs_angles = [abs(angle) for angle in angle_diffs]
    abs_lengths = [abs(length) for length in length_diffs]
    segs = max(max(abs_angles), max(abs_lengths))
    total_configs = int(math.ceil(segs/0.001))

    for arm in range(len(start_config.ee1_angles)):
        primitive_angles.append(angle_diffs[arm] / total_configs)
        primitive_lengths.append(length_diffs[arm] / total_configs)

    for prim_step in range(total_configs):
        ee1_angles = []
        lengths = []
        for arm in range(len(start_config.ee1_angles)):
            angle = Angle(radians=start_config.ee1_angles[arm].in_radians() + (prim_step * primitive_angles[arm]))
            ee1_angles.append(angle)

            length = start_config.lengths[arm] + prim_step * primitive_lengths[arm]
            lengths.append(length)

        config = make_robot_config_from_ee1(start_config.get_ee1()[0], start_config.get_ee1()[1], ee1_angles, lengths,
                                            start_config.ee1_grappled, start_config.ee2_grappled)

        # If collision check happened, don't do it again
        if not is_end:
            if not test_obstacle_collision(config, spec, spec.obstacles) or not test_environment_bounds(config) \
                    or not test_self_collision(config, spec):
                return None

        primitive_steps.append(config)

    primitive_steps.append(end_config)

    return primitive_steps


def collision_check(current_node, nodes, spec):
    """
    Checks whether there is a valid path between two GraphNodes. If there is, then they are added as neighbours.
    :param config: Current GraphNode config
    :param nodes: List of all GraphNode configs
    :return: None
    """
    for node in nodes:
        path = interpolate_path(current_node.config, node.config, False, spec)

        if path is None:
            continue

        GraphNode.add_connection(current_node, node)


def main(arglist):
    input_file = arglist[0]
    output_file = arglist[1]

    spec = ProblemSpec(input_file)

    init_node = GraphNode(spec, spec.initial)
    goal_node = GraphNode(spec, spec.goal)
    nodes = [init_node, goal_node]

    steps = []
    timeout = time.time() + 45

    while True:
        robot_config = sample_config(spec)

        if robot_config is None:
            continue

        current_node = GraphNode(spec, robot_config)

        # Check for collisions between current_node and other nodes
        collision_check(current_node, nodes, spec)
        nodes.append(current_node)
        route = find_graph_path(spec, init_node)

        if route or time.time() > timeout:
            # Start at init and get to end appending to list of steps
            break

    for i in range(len(route) - 1):
        steps.extend(interpolate_path(route[i], route[i + 1], True, spec))
    steps.append(goal_node.config)

    if len(arglist) > 1:
        write_robot_config_list_to_file(output_file, steps)

    #
    # You may uncomment this line to launch visualiser once a solution has been found. This may be useful for debugging.
    # *** Make sure this line is commented out when you submit to Gradescope ***
    #
    #v = Visualiser(spec, steps)


if __name__ == '__main__':
    main(sys.argv[1:])
