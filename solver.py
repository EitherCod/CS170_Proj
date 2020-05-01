import networkx as nx
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
    if not nx.number_of_edges(G):
        return G

    # Generate an mst
    min_tree = nx.minimum_spanning_tree(G, 'weight')


    # step 1: create list of leaves
    leaves = []
    for v in min_tree.nodes:
        if min_tree.degree[v] == 1:
            leaves.append(v)

    # Cost-compare method:
    # Iterate through leaves and see if removing them will 
    # lower cost (this is an expensive computation).
    # Continue looping through remaining leaves until
    # no more leaves are removed
    #
    removed = 1
    while removed > 0:
        min_tree, leaves, removed = prune_leaves(leaves, min_tree)

    return min_tree


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

def prune_leaves(leaves, min_tree):
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
            if (new_cost > cost):
                min_tree.add_node(leaf)
                min_tree.add_edge(e[0], e[1], weight=e[2])
                #print("Leaf kept")
                kept_leaves.append(leaf)
            else:
                removed += 1
    if (removed):
        print("We removed " + str(removed) + " leaves in this iter")
    return min_tree, kept_leaves, removed




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
     for path in os.listdir(p):
        # print("Trying file: " + path)
        G = read_input_file(p + '/' + path)
        T = solve(G)
        assert is_valid_network(G, T)
        print("Average  pairwise distance: {}".format(average_pairwise_distance(T)))
        out = 'out/' + path[:len(path) - 3]
        out = out + '.out'
        # print('output path: ' + out)
        write_output_file(T, out)
        read_output_file(out, G)
