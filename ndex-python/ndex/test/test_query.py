import unittest

import ndex.client as nc

import json
import ndex.test.test_NdexClient as tt


# Python Client APIs tested:
#
#   save_cx_stream_as_new_network
#   get_neighborhood_as_cx_stream
#   get_neighborhood
#   delete_network
#


class MyTestCase(tt.NdexClientTestCase):

    @classmethod
    def getNumberOfNodesAndEdgesFromCX(self, network_in_cx):
        for aspect in network_in_cx:
            if 'metaData' in aspect:
                metaData = aspect['metaData']

                for element in metaData:
                    if (('name' in element) and (element['name'] == 'nodes')):
                        numberOfNodes = element['elementCount']

                    if (('name' in element) and (element['name'] == 'edges')):
                        numberOfEdges = element['elementCount']

                break

        return numberOfNodes, numberOfEdges


    def test_get_neighborhood_as_cx_stream(self):

        search_string = 'AANAT-T3M'
        # run neighborhood query with depth 1; expected to receive subnetwork with 2 edges and 3 nodes
        network_neighborhood = self._ndex.get_neighborhood_as_cx_stream(self._networkId, search_string, 1)
        self.assertTrue(network_neighborhood.status_code == 200)
        network_in_cx = json.loads(network_neighborhood.text)

        numberOfNodes, numberOfEdges = self.getNumberOfNodesAndEdgesFromCX(network_in_cx['data'])
        self.assertTrue(numberOfNodes == 3)
        self.assertTrue(numberOfEdges == 2)


        # now run neighborhood query with depth 2; expected to receive subnetwork with 6 edges and 5 nodes
        network_neighborhood = self._ndex.get_neighborhood_as_cx_stream(self._networkId, search_string, 2)
        self.assertTrue(network_neighborhood.status_code == 200)
        network_in_cx = json.loads(network_neighborhood.text)

        numberOfNodes, numberOfEdges = self.getNumberOfNodesAndEdgesFromCX(network_in_cx['data'])
        self.assertTrue(numberOfNodes == 5)
        self.assertTrue(numberOfEdges == 6)

        # run neighborhood query with depth 1; expected to receive subnetwork with 2 edges and 3 nodes
        network_neighborhood = self._ndex.get_neighborhood(self._networkId, search_string, 1)
        numberOfNodes, numberOfEdges = self.getNumberOfNodesAndEdgesFromCX(network_neighborhood)
        self.assertTrue(numberOfNodes == 3)
        self.assertTrue(numberOfEdges == 2)


        # now run neighborhood query with depth 2; expected to receive subnetwork with 6 edges and 5 nodes
        network_neighborhood = self._ndex.get_neighborhood(self._networkId, search_string, 2)
        numberOfNodes, numberOfEdges = self.getNumberOfNodesAndEdgesFromCX(network_neighborhood)
        self.assertTrue(numberOfNodes == 5)
        self.assertTrue(numberOfEdges == 6)


if __name__ == '__main__':
    unittest.main()

