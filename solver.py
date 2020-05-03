import networkx as nx
from networkx.algorithms import approximation
from parse import read_input_file, write_output_file, read_output_file
from utils import is_valid_network, average_pairwise_distance, average_pairwise_distance_fast
import sys
import os
import time


def solve(G):
    """
    Args:
        G: networkx.Graph

    Returns:
        T: networkx.Graph
    """

    # TODO: your code here!
    # if no edges, return G
    if not nx.number_of_edges(G):
        return G, 'None'

    # nx documentation here: https://networkx.github.io/documentation/stable/tutorial.html

        # Method 1: MST Pruning

    # Generate an mst
    min_spanning_tree = nx.minimum_spanning_tree(G, 'weight')
    # prune mst until we cannot anymore
    iters = 1
    while iters > 0:
        min_spanning_tree, iters = remove_leaves(min_spanning_tree, G)

        # Method 1.5: Another version of MST: remove based on cost

    min_spanning_tree_cost = nx.minimum_spanning_tree(G, 'weight')
    iters = 1
    while iters > 0:
        min_spanning_tree_cost, iters = remove_leaves_cost(min_spanning_tree_cost)

        # Method 2: Dominating Set

    # set the weight of each node (to be used in the
    # calculation of dominating set)
    centerList = nx.algorithms.distance_measures.barycenter(G, weight='weight')
    # calculate distances of all vertices to center
    distanceToCenters, pathToCenters = nx.algorithms.shortest_paths.weighted.multi_source_dijkstra(G, centerList, weight='weight')
    # set the weights for dom set
    for v in G.nodes:
        G.nodes[v]['w'] = distanceToCenters[v]
    # calculate a dominating set, using a provided algo
    dom_set = list(nx.algorithms.approximation.dominating_set.min_weighted_dominating_set(G, weight='w'))

    # calculates a collection of all shortest paths
    shortest_paths = nx.algorithms.shortest_paths.generic.shortest_path(G, weight='weight')

    # build a new graph based on our dominating set
    X = nx.Graph()

    # iterate through every possible pair of nodes int
    # the dominating set
    for i in range(len(dom_set)):
        v = dom_set[i]
        #print("i: " + str(i) + ", dom_set[i]: " + str(v))
        for j in range(len(dom_set)):
            if(i != j):
                u = dom_set[j]
                #print("j: " + str(j) + ", dom_set[j]: " + str(u))
                path = shortest_paths[v][u]
                # print(path)
                lis = []
                for i in range(len(path) - 1):
                    v = path[i]
                    u = path[i + 1]
                    p = 0
                    try:
                        # this errors if the edge does not exist
                        p = X.edges[v, u]
                    except:
                        # if the edge deosn't exist, add it
                        w = G.edges[v, u]['weight']
                        e = (v, u, w)
                        # print(e)
                        lis.append(e)
                # print(paths)
                if (lis):
                    X.add_weighted_edges_from(lis)
    dom_mst = nx.minimum_spanning_tree(X, 'weight')
    iters = 1
    while iters > 0:
        dom_mst, iters = remove_leaves_cost(dom_mst)

    # Final section: display data and choose best method

    dom = ['none', float('inf'), None]
    # sometimes the dominating set method produces a null value.
    # this typically happens on graphs where the best answer
    # is a single vertex, with no edges. We should fix this bug.
    if not dom_mst:
        print("Dom mst is null")
    else:
        cost1 = average_pairwise_distance_fast(dom_mst)
        dom = ["Dominating Set", cost1, dom_mst]
        print("Dominating Set: " + str(cost1))

    cost2 = average_pairwise_distance_fast(min_spanning_tree)
    mst = ["Removal MST", cost2, min_spanning_tree]
    print("   Removal MST: " + str(cost2))

    cost3 = average_pairwise_distance_fast(min_spanning_tree_cost)
    cost_mst = ["Cost-First MST", cost3, min_spanning_tree_cost]
    print("Cost-First MST: " + str(cost3))

    best = min([dom, mst, cost_mst], key=lambda x: x[1])
    print(best[0] + ' was best!')
    return best[2], best[0]


# Handles removing appropriate leaves from
# the given minimum spanning tree.
def remove_leaves(min_tree, G):
    # Create list of leaves
    leaves = []
    for v in min_tree.nodes:
        if min_tree.degree[v] == 1:
            leaves.append(v)

    # order leaves so that we remove the
    # largest-weighted ones first
    # this will be irrelevant if we implement dp
    leaves.sort(reverse=True, key=lambda x: list(min_tree.edges(x, data='weight'))[0][2])

    # Continue looping through remaining leaves until
    # no more leaves are removed
    iters = -1
    removed = 1
    while removed > 0:
        min_tree, leaves, removed = prune_leaves(leaves, min_tree, G)
        iters += 1

    return min_tree, iters


# This method removes leaves from a given min_tree
# if the tree remains a dominating set on G
# [previous behavior: remove if doing so decreases
# the cost (average pairwise distance)]
def prune_leaves(leaves, min_tree, G):
    removed = 0
    kept_leaves = []
    for leaf in leaves:
        if (leaf):

            e = list(min_tree.edges(leaf, data='weight'))[0]
            #print("leaf: " + str(leaf))
            #print("leaf edge: " + str(e))
            #cost = average_pairwise_distance_fast(min_tree)
            min_tree.remove_node(leaf)
            #new_cost = average_pairwise_distance_fast(min_tree)
            # if (new_cost > cost):

            # IMPLEMENT DP HERE?
            # choose between keeping node and removing it
            # like choose min_cost(keeping_node, removing_node)
            # idk how to implement tho
            if (not nx.is_dominating_set(G, min_tree.nodes)):
                min_tree.add_node(leaf)
                min_tree.add_edge(e[0], e[1], weight=e[2])
                #print("Leaf kept")
                kept_leaves.append(leaf)
            else:
                removed += 1
    if (removed):
        print("(Removal) We removed " + str(removed) + " leaves in this iter")
    return min_tree, kept_leaves, removed


# Handles removing appropriate leaves from
# the given minimum spanning tree.
def remove_leaves_cost(min_tree):
    # Create list of leaves
    leaves = []
    for v in min_tree.nodes:
        if min_tree.degree[v] == 1:
            leaves.append(v)

    # Continue looping through remaining leaves until
    # no more leaves are removed
    iters = -1
    removed = 1
    while removed > 0:
        try:
            min_tree, leaves, removed = prune_leaves_cost(leaves, min_tree)
        except:
            return min_tree, -1
        iters += 1

    return min_tree, iters


# [previous behavior: remove if doing so decreases
# the cost (average pairwise distance)]
def prune_leaves_cost(leaves, min_tree):
    removed = 0
    kept_leaves = []
    for leaf in leaves:
        if (leaf):
            e = list(min_tree.edges(leaf, data='weight'))[0]
            #print("leaf: " + str(leaf))
            #print("leaf edge: " + str(e))
            cost = average_pairwise_distance_fast(min_tree)
            min_tree.remove_node(leaf)
            new_cost = average_pairwise_distance_fast(min_tree)
            if (new_cost > cost or not nx.is_dominating_set(G, min_tree.nodes)):
                min_tree.add_node(leaf)
                min_tree.add_edge(e[0], e[1], weight=e[2])
                #print("Leaf kept")
                kept_leaves.append(leaf)
            else:
                removed += 1
    if (removed):
        print("(Cost) We removed " + str(removed) + " leaves in this iter")
    return min_tree, kept_leaves, removed


# Prints a list of all leaves in a given
# leaf-list
def print_leaves(leaves, min_tree):
    lis = []
    for leaf in leaves:
        lis.append(list(min_tree.edges(leaf, data='weight'))[0])
    print("Leaves: ")
    print(lis)


# To run: python3 solver.py inputs


if __name__ == '__main__':
    assert len(sys.argv) == 2
    p = sys.argv[1]
    methods = {}
    total = 0
    for path in os.listdir(p):
        print()
        print("Trying file: " + path)
        G = read_input_file(p + '/' + path)
        T, met = solve(G)
        if (met in methods):
            methods[met] += 1
        else:
            methods[met] = 1
        assert is_valid_network(G, T)
        print("Average  pairwise distance: {}".format(average_pairwise_distance(T)))
        out = 'out/' + path[:len(path) - 3]
        out = out + '.out'
        # print('output path: ' + out)
        write_output_file(T, out)
        read_output_file(out, G)
        total += 1
    best_method = max(methods, key=methods.get)
    percent = (float)(methods[best_method] * 100) / total
    print("The best method is " + str(best_method) + ", at " + str(percent) + "%")

    # Avg-weight/Cost-Checking Hybird Method:
    # this is outperformed by full cost-checking method,
    # an I'm not sure why. rip. this is what it does:
    # First, Use avg to cull obvious large leaf edges:
    # Remove edges with weights that are
    # greater than or equal to the average,
    # and recalculate the average.
    # Then use cost-checking for the rest

#    sum = 0
#    for (u, v, wt) in G.edges.data('weight'):
#        sum += wt
#    avg = sum / nx.number_of_edges(G)
#
#    phase = 0
#    for leaf in leaves:
#        if (leaf):
#            if phase == 0:
#                #print("leaf: " + str(list(min_tree.edges(leaf, data='weight'))[0]))
#                edge_weight = list(min_tree.edges(leaf, data='weight'))[0][2]
#                if edge_weight >= avg:
#                    #print("Leaf removed!")
#                    min_tree.remove_node(leaf)
#                    num_edges = nx.number_of_edges(min_tree)
#                    if (num_edges):
#                        avg = (((num_edges + 1) * avg) - edge_weight) / num_edges
#                    else:
#                        avg = 0
#                else:
#                    phase = 1
#                    print("phase 0 removed " + str(removed) + " leaves")
#            else:
#                e = list(min_tree.edges(leaf, data='weight'))[0]
#                #print("leaf: " + str(leaf))
#                #print("leaf edge: " + str(e))
#                cost = average_pairwise_distance_fast(min_tree)
#                min_tree.remove_node(leaf)
#                new_cost = average_pairwise_distance_fast(min_tree)
#                if (new_cost > cost):
#                    min_tree.add_node(leaf)
#                    min_tree.add_edge(e[0], e[1], weight=e[2])
