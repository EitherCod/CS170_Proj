import matplotlib.pyplot as plt
import networkx as nx
import os
import sys
from parse import read_input_file, read_output_file
from utils import is_valid_network, average_pairwise_distance, average_pairwise_distance_fast


if __name__ == '__main__':
     assert len(sys.argv) == 2
     graph = sys.argv[1]
     inputt = "inputs/" + graph + ".in"
     output = "out/" + graph + ".out"
     print("Trying files: " + inputt + ", " + output)
     G = read_input_file(inputt)
     T = read_output_file(output, G)
     print("Average  pairwise distance: {}".format(average_pairwise_distance(T)))
     nx.draw_networkx(G)
     plt.show()
     nx.draw_networkx(T)
     plt.show()
     print("finished drawing")