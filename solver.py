import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_network, average_pairwise_distance
import sys
import os


def solve(G):
    """
    Args:
        G: networkx.Graph

    Returns:
        T: networkx.Graph
    """

    # TODO: your code here!
    # Generate an mst
    min_tree = nx.minimum_spanning_tree(G, 'weight')
    if not nx.is_tree(min_tree):
    	print("Min tree is not a tree!")

    # calculate average edge weight
    sum = 0
    for (u, v, wt) in G.edges.data('weight'):
    	sum += wt
    avg = sum / nx.number_of_edges(G)

    # remove leaf edges whose weights are
    # not less than the avg:
    # step 1: create list of leaves
    leaves = []
    for v in min_tree.nodes:
    	if min_tree.degree[v] == 1:
    		leaves.append(v)

    # consider leaves in reverse order of their
    # corresponding edge weight
    print(min_tree.edges(v, data='weight'))
    leaves.sort(reverse=True, key=lambda v: list(min_tree.edges(v, data='weight'))[0][2])

    # remove edges with weights that are 
    # greater than or equalt to the average, 
    # and recalculate the average
    for leaf in leaves:
    	edge_weight = list(min_tree.edges(leaf, data='weight'))[0][2]
    	if edge_weight >= avg:
    		min_tree.remove_node(leaf)
    		num_edges = nx.number_of_edges(min_tree)
    		if (num_edges):
    			avg = (((num_edges + 1) * avg) - edge_weight) / num_edges
    		else:
    			avg = 0

    # maybe: iterate through remaining leaves and see if removing
    # them will lower cost (this will be an expensive computation)

    return min_tree


    



# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

if __name__ == '__main__':
     assert len(sys.argv) == 2
     p = sys.argv[1]
     for path in os.listdir(p):
     	G = read_input_file(p + '/' + path)
     	T = solve(G)
     	assert is_valid_network(G, T)
     	print("Average  pairwise distance: {}".format(average_pairwise_distance(T)))
     	out = 'out/' + path[len('input/ '):len(path) - 3]
     	out = out + '.out'
     	# print('output path: ' + out)
     	write_output_file(T, out)
