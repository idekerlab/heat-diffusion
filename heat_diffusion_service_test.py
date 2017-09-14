import unittest
import random

import networkx

from heat_diffusion_service import HeatDiffusionService

class TestHeatDiffusionService(unittest.TestCase):

    def test_find_heat(self):
        hds = HeatDiffusionService()
        network = create_random_networkx_mock(heats=50)
        heats = hds.find_heat(network, 'diffusion_input')
        self.assertEqual(len(heats), 100)
        for heat in range(0, 50):
            self.assertEqual(heats[heat], 1.0)
        for heat in range(50, 100):
            self.assertEqual(heats[heat], 0.0)

    def test_add_heat(self):
        hds = HeatDiffusionService()
        network = create_random_networkx_mock(num_nodes=50)
        new_heats = [random.uniform(1,100) for node in network.nodes()]
        network = hds.add_heat(network, 'diffusion_output', new_heats)
        data_list = [data for node, data in network.nodes(data=True)]
        s1 = sorted(data_list, key=lambda k: k['diffusion_output_rank'])
        s2 = sorted(data_list, key=lambda k: k['diffusion_output_heat'])
        for index, node in enumerate(s1):
            self.assertIn('diffusion_output_rank', node)
            self.assertIn('diffusion_output_heat', node)
            self.assertEqual(s1[index], s2[index])

    def test_diffusion(self):
        hds = HeatDiffusionService()
        network = create_random_networkx_mock(heats=50)
        network = hds.diffusion(network, 'diffusion_input', 'diffusion_output', False, 1.0)


def create_random_networkx_mock(num_nodes=100, num_edges=100, heats=100, random_heats=False):
    n = networkx.Graph()
    for n_id in range(num_nodes):
        heat = 0.0
        if heats > 0:
            heat = 1.0
            if random_heats:
                heat = random.uniform(1.0, 100.0)
            heats -= 1
        n.add_node(n_id, diffusion_input=heat)
    for e_id in range(num_edges):
        n1 = random.randint(0, num_nodes-1)
        n2 = random.randint(0, num_nodes-1)
        n.add_edge(n1, n2)
    return n

if __name__ == '__main__':
    unittest.main()
