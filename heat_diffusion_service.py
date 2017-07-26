import operator

import networkx
from numpy import array
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import expm, expm_multiply

import cxmate

class HeatDiffusionService(cxmate.Service):

    def process(self, input_stream):
        network, params = cxmate.Adapter.to_networkx(input_stream)
        time = params['time']
        input_key = params['input_attribute_name']
        output_key = params['output_attribute_name']
        normalize_laplacian = params['normalize_laplacian']
        network = self.diffusion(network, input_key, output_key, normalize_laplacian, time)
        network.graph['label'] = 'Output'
        return cxmate.Adapter.from_networkx(network)

    def diffusion(self, network, input_key, output_key, normalize_laplacian, time):
        matrix = self.create_sparse_matrix(network, normalize_laplacian)
        heat_array = self.find_heat(network, input_key)
        diffused_heat_array = self.diffuse(matrix, heat_array, time)
        network = self.add_heat(network, output_key, diffused_heat_array)
        return network

    def diffuse(self, matrix, heat_array, time):
        return expm_multiply(-matrix, heat_array, start=0, stop=time, endpoint=True)[-1]


    def create_sparse_matrix(self, network, normalize=False):
        if normalize:
            return csc_matrix(networkx.normalized_laplacian_matrix(network))
        else:
            return csc_matrix(networkx.laplacian_matrix(network))

    def find_heat(self, network, heat_key):
        heat_list = []
        found_heat = False
        for node_id in network.nodes():
            if heat_key in network.node[node_id]:
                found_heat = True
            heat_list.append(network.node[node_id].get(heat_key, 0))
        if not found_heat:
            raise Exception('No input heat found')
        return array(heat_list)

    def add_heat(self, network, output_key, heat_array):
        node_heat = {node_id: heat_array[i] for i, node_id in enumerate(network.nodes())}
        sorted_nodes = sorted(node_heat.items(), key=lambda x:x[1], reverse=True)
        node_rank = {node_id: i for i, (node_id, _) in enumerate(sorted_nodes)}
        networkx.set_node_attributes(network, output_key+'_heat', node_heat)
        networkx.set_node_attributes(network, output_key+'_rank', node_rank)
        return network

if __name__ == '__main__':
    myService = HeatDiffusionService()
    myService.run('0.0.0.0:8080')
