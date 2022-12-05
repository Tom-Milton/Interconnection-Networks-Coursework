from tqdm import tqdm
from collections import Counter
import matplotlib.pyplot as plt

def increment_node(k, n, node):
    """ Builds the lexicographically next node after 'node' or signals
        that 'node' is the last node via 'last_node' = True """
    last_node = True
    all_checked = False
    i = k - 1
    while last_node == True and all_checked == False:
        if node[i] < n - 1:
            last_node = False
            node[i] = node[i] + 1
            for j in range(k - 1, i, -1):
                node[j] = 0
        else:
            i = i - 1
            if i == -1:
                all_checked = True
    return last_node, node

def test_permutation(k, n, node):
    """ Checks that the list 'node' is in the form of a permutation, i.e., all k elements are distinct """
    permutation = True
    i = 0
    while i < k - 1 and permutation == True:
        j = i + 1
        while j < k and permutation == True:
            if node[i] == node[j]:
                permutation = False
            j = j + 1
        i = i + 1
    return permutation

def alltoall_traffic(k, n):
    """ Generates a list of source nodes 'list_of_sources' and a list of destination nodes
        'list_of_destinations', both lists of length [n!/(n-k)!]^2, such that every pair of nodes
        appears as a pair in 'list_of_sources[i]' x 'list_of_destinations[i]' (including
        pairs of the form [node, node]) """
    list_of_nodes = []
    node = []
    for i in range(0, k):
        node.append(i)
    list_of_nodes.append(node[:])

    last_node = False
    while last_node == False:
        last_node, node = increment_node(k, n, node)
        if last_node == False:
            if test_permutation(k, n, node):
                list_of_nodes.append(node[:])

    list_of_sources = []
    list_of_destinations = []
    for source in list_of_nodes:
        for target in list_of_nodes:
            list_of_sources.append(source[:])
            list_of_destinations.append(target[:])
    return list_of_sources, list_of_destinations

def zero_edge(k, n, node, i): 
    """ Swap position 0 with some i not already in the node """
    new_node = node[:]
    new_node[0] = i
    return node, new_node

def i_edge(k, n, node, i):
    """ Swap position 0 with position i """
    new_node = node[:]
    new_node[0], new_node[i] = new_node[i], new_node[0]
    return node, new_node

def relabelling(k, n, source, destination):
    """ Create forward dict to map source-destination case to source'-[0,1,2,...] case
        and reverse dict to map source'-[0,1,2,...] case to source-destination case """
    forward_dict = {v: k for k, v in enumerate(destination)}
    not_used = list(range(k, n+1))
    for i in range(n):  # Assign unique arbitrary label to those values not already in the dict
        if i not in forward_dict:
            forward_dict[i] = not_used.pop(0) 
    reverse_dict = {v: k for k, v in forward_dict.items()}
    return forward_dict, reverse_dict

def simple_routing(k, n, source, destination):
    """ Get route from source' to [0,1,2,...] """
    route = [source]
    node = source[:]
    for i in range(k):

        if node[i]==i:  # Already in position
            # print('Identity case i={}'.format(i))
            pass

        elif i in node:  # Internal cycle
            # print('Internal cycle i={}'.format(i))
            og_node, node = i_edge(k, n, node, i)
            if node != og_node: route.append(node[:])
            og_node, node = i_edge(k, n, node, node.index(i))
            if node != og_node: route.append(node[:])
            og_node, node = i_edge(k, n, node, i) 
            if node != og_node: route.append(node[:])

        elif i not in node:  # External cycle
            # print('External cycle i={}'.format(i))
            og_node, node = i_edge(k, n, node, i)
            if node != og_node: route.append(node[:])
            og_node, node = zero_edge(k, n, node, i)
            if node != og_node: route.append(node[:])
            og_node, node = i_edge(k, n, node, i)
            if node != og_node: route.append(node[:])

    return route

def nkstar_routing(k, n, source, destination):
    """ Get route from any source to any distination """
    forward_dict, reverse_dict = relabelling(k, n, source, destination)
    source, destination = [*map(forward_dict.get, source)], [*map(forward_dict.get, destination)]
    route = simple_routing(k, n, source, destination)
    route = [[*map(reverse_dict.get, node)] for node in route]
    return route

def check_route(k, n, source, destination, route):
    """ Check route starts at source, ends at destination,
        and all edges are valid 0-edges or i-edges """
    if route[0] != source:  # Check route starts at source
        print("{} is not source {}".format(route[0], source))
    if route[-1] != destination:  # Check route finished at destination
        print("{} is not destination {}".format(route[-1], destination))

    j = 0
    while route[j] != destination:  # Check edges are vald
        possible_zero_nodes = [zero_edge(k, n, route[j], i)[1] for i in list(set(range(n))-set(route[j]))]
        possible_i_nodes = [i_edge(k, n, route[j], i)[1] for i in range(1, k)]
        if (route[j+1] not in possible_zero_nodes) and (route[j+1] not in possible_i_nodes):
            print("{} is not connected to {}".format(route[j], route[j+1]))
        j += 1

def report_stats(k, n):
    """ Calculate node and channel loads for an all-to-all traffic pattern.
        Calculate maximal and average path-lengths for an all-to-all traffic pattern. 
        Print results and analysis as required by the question."""
    list_of_sources, list_of_destinations = alltoall_traffic(k, n)

    all_nodes = []
    all_edges = []
    max_path_length = 0
    total_path_length = 0

    for i in tqdm(range(len(list_of_sources))): 
        route = nkstar_routing(k, n, list_of_sources[i], list_of_destinations[i])
        # check_route(k, n, list_of_sources[i], list_of_destinations[i], route)
        route = list(map(tuple, route))  # Map to tuples for Counter

        # Paths of length 1 contribute no loads
        if len(route) != 1: all_nodes.extend(route)  # Add all nodes in route
        if len(route) != 1: all_edges.extend(list(zip(route[::1], route[1::1])))  # Add consecutive pairs of notes in route
        if len(route) > max_path_length: max_path_length = len(route)  # Update longest path if found
        total_path_length += len(route)
    
    node_loads = Counter(all_nodes)
    edge_loads = Counter(all_edges)
    avg_path_length = total_path_length/len(list_of_sources)

    print("node load: #nodes \t {}".format(Counter(list(node_loads.values()))))
    print("edge load: #edges \t {}".format(Counter(list(edge_loads.values()))))
    print("Maximum path length \t {}".format(max_path_length))
    print("Average path length \t {}".format(avg_path_length))
    print("")
    print("In the n=7, k=4 case all nodes have load 7565")
    print("In the n=7, k=4 case all 0-edges have load 638 and all i-edges have load 1520, 1604, or 1688")
    print("We already know S(n,k) is node symmetric. Since S(n,k) has two types of edges, it cannot be edge symmetric.")
    print("Since all 0-edges have the same load and all i-edges have similar load, we conclude that S(n,k) is likely edge symmetric w.r.t to the edge type.")

report_stats(4, 7)