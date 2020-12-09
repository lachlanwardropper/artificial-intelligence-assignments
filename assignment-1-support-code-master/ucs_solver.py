#!/usr/bin/python
import sys
from laser_tank import LaserTankMap
from queue import *
import heapq
import copy
import time
start_time = time.time()
print("--- %s seconds ---" % (time.time() - start_time))

"""
Template file for you to implement your solution to Assignment 1.

COMP3702 2020 Assignment 1 Support Code
"""


class Node:
    """
    Details the characteristics of a node object
    """
    def __init__(self):
        self.position = []
        self.f_score = 0
        self.g_score = 0
        self.h_score = 0
        self.parent = None
        self.heading = None
        self.shot = False
        self.map = None
        self.move = None

    def get_child(self, move, game_map, end_node):
        """
        Successor function that finds the neighbouring state of the current node based
        on the move parameter. If the state is valid, a new node is created.
        :param move: action made by player
        :param game_map: current state of the game map
        :param end_node: node representing the flag (goal space)
        :return: newly created child node
        """
        new_grid = [row[:] for row in game_map.grid_data]
        tmp = LaserTankMap(game_map.x_size, game_map.y_size, new_grid, game_map.player_x,
                           game_map.player_y, game_map.player_heading)
        next_move = tmp.apply_move(move)

        if next_move == 0:
            child = Node()
            child.position = [tmp.player_x, tmp.player_y]
            child.g_score = self.g_score + 1
            child.h_score = abs(tmp.player_x - end_node.position[0]) \
                + abs(tmp.player_y - end_node.position[1])
            child.f_score = child.h_score + child.g_score
            child.heading = tmp.player_heading
            child.parent = self
            child.map = tmp
            child.move = move

            if move == 's':
                child.shot = True
            else:
                child.shot = False

            return child

        return None

    def __lt__(self, obj):
        return self.g_score < obj.g_score

    def __eq__(self, obj):
        # NEED TO COMPARE SOMETHING ABOUT GRID_DATA WITHOUT SCANNING WHILE ARRAYS
        return self.position == obj.position and self.heading == obj.heading and \
            self.shot == obj.shot


def write_output_file(filename, actions):
    """
    Write a list of actions to an output file. You should use this method to write your output file.
    :param filename: name of output file
    :param actions: list of actions where is action is in LaserTankMap.MOVES
    """
    f = open(filename, 'w')
    for i in range(len(actions)):
        f.write(str(actions[i]))
        if i < len(actions) - 1:
            f.write(',')
    f.write('\n')
    f.close()


def initialise_end_node(game_map):
    """
    Creates a node object to represent the flag node. This method allows the program
    to use this node to find the heurisitc for each state of the game, and to see if
    the game is complete.
    :param game_map: initial state of the game
    :return: node representing the flag
    """
    end_node = Node()
    end_pos = []
    x_pos = 0

    for row in game_map.grid_data:
        y_pos = 0
        for col in row:
            if col == game_map.FLAG_SYMBOL:
                end_pos.append(y_pos)
                end_pos.append(x_pos)
                break
            y_pos += 1
        x_pos += 1

    end_node.position = end_pos

    return end_node


def configure_start_node(end_node, game_map):
    """
    Initialises the starting player node in order to begin searching neighbouring states.
    :param end_node: flag symbol represented as node object
    :param game_map: initial game map state
    :return: initial node object
    """
    init_node = Node()
    init_node.position = [game_map.player_x, game_map.player_y]
    init_node.h_score = abs(init_node.position[0] - end_node.position[0]) \
                        + abs(init_node.position[1] - end_node.position[1])
    init_node.f_score = init_node.g_score + init_node.h_score
    init_node.heading = game_map.player_heading
    init_node.map = copy.deepcopy(game_map)
    return init_node


def check_closed(child, closed_list):
    """
    Checks to see if a child node has already been searched and thus added to the closed list.
    :param child: node to check
    :param closed_list: list of already searched nodes
    :return: true if child in closed list, false otherwise
    """
    for node in closed_list:
        if child.position == node.position and \
                child.heading == node.heading and child.map.grid_data == node.map.grid_data:
            return True
    return False


def check_shorter_path(new_node, open_list):
    """
    Checks to see if the current node already exists in the open list. If it does, then the F costs
    of both nodes will be compared, and the one with the smalled F cost value will remain in the list.
    :param new_node: node to check
    :param open_list: list containing all nodes that need to be searched
    :return: 1 if new_node replaces another node, 0 if new_node F cost is greater, and 2 if no other instances
    """
    for node in open_list:
        if node.__eq__(new_node):
            if node.g_score > new_node.g_score:
                open_list.remove(node)
                open_list.append(new_node)
                return 1
            else:
                return 0
    return 2


def get_sequence(end_node):
    """
    Returns the sequence of actions that have led to the agent reaching the goal state. Method starts
    at the end node and finds the nodes parents and adds their move to the list.
    :param end_node: node that reached the goal state
    :return: list of moves that led to agent reaching goal state
    """
    # Actions are initially reversed
    rev_actions = [end_node.move]
    parent = end_node.parent

    while parent:
        rev_actions.append(parent.move)
        parent = parent.parent

    rev_actions.remove(None)
    actions = rev_actions[::-1]

    return actions


def main(arglist):
    start_time = time.time()
    input_file = arglist[0]
    output_file = arglist[1]

    # Read the input testcase file
    game_map = LaserTankMap.process_input_file(input_file)
    actions = []
    moves = game_map.MOVES

    end_node = initialise_end_node(game_map)
    init_node = configure_start_node(end_node, game_map)

    # Nodes requiring searching
    open_list = [init_node]
    heapq.heapify(open_list)
    # Nodes that have been searched previously
    closed_list = []

    while len(open_list):
        current = heapq.heappop(open_list)
        current_map = current.map
        closed_list.append(current)

        if current.position == end_node.position:
            actions = get_sequence(current)
            break

        for move in moves:
            child = current.get_child(move, current_map, end_node)

            if not child or check_closed(child, closed_list):
                continue

            status = check_shorter_path(child, open_list)

            if status == 2:
                heapq.heappush(open_list, child)

    print("--- %s seconds ---" % (time.time() - start_time))

    # Write the solution to the output file
    #write_output_file(output_file, actions)


if __name__ == '__main__':
    main(sys.argv[1:])

