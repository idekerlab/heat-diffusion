import unittest

import ndex.client as nc
import time
from os import path
import ndex.test.test_NdexClient as tt

ndex_network_resource = "/v2/network/"

example_network_1 = 'A549-SL-network.cx'


# Python Client APIs tested:
#
#   set_network_properties
#


class MyTestCase(unittest.TestCase):

    def test_network_properties(self):
        ndex = nc.Ndex(host= tt.TESTSERVER, username=tt.testUser1, password=tt.testUserpasswd, debug=True)

        with open(path.join(path.abspath(path.dirname(__file__)),example_network_1), 'r') as file_handler:
            network_in_cx = file_handler.read()

        # test save_cx_stream_as_new_network
        test_network_1_uri = ndex.save_cx_stream_as_new_network(network_in_cx)
        self.assertTrue(test_network_1_uri.startswith(tt.TESTSERVER + ndex_network_resource))

        network_UUID = str(test_network_1_uri.split("/")[-1])


        ################### first, we add a new property with subNetworkId == None ###################

        # get network summary
        network_summary = ndex.get_network_summary(network_UUID)

        property_list = []
        if "properties" in network_summary:
            property_list = network_summary['properties']

        property_list.append({
            'dataType' : 'string',
            'predicateString' : 'newProperty',
            'subNetworkId' : None,
            'value' : 'New Value'
        })

        time.sleep(10)
        number_of_properties = ndex.set_network_properties(network_UUID, property_list)
        self.assertTrue(number_of_properties == len(property_list))

        # get network summary with the new properties
        network_summary_1 = ndex.get_network_summary(network_UUID)
        property_list_1 = network_summary_1['properties']
        self.assertTrue(property_list == property_list_1)




        ################### now, we add a new property with subNetworkId != None ###################

        self.assertTrue("subnetworkIds" in network_summary, "'subnetworkIds' structure is not in network_summary")

        number_of_subnetworks = len(network_summary["subnetworkIds"])
        self.assertTrue(number_of_subnetworks == 1, "Expected 1 subnetwork in network summary, but there are " \
                        + str(number_of_subnetworks))

        subnetwork_id = network_summary["subnetworkIds"][0]

        property_list_1.append({
            'dataType' : 'string',
            'predicateString' : 'newProperty',
            'subNetworkId' : subnetwork_id,
            'value' : 'New Value'
        })

        number_of_properties = ndex.set_network_properties(network_UUID, property_list_1)
        self.assertTrue(number_of_properties == len(property_list_1))

        # get network summary with the new properties
        network_summary_2 = ndex.get_network_summary(network_UUID)
        property_list_2 = network_summary_2['properties']
        self.assertTrue(property_list_1 == property_list_2)



        # test delete_network
        del_network_return = ndex.delete_network(network_UUID)
        self.assertTrue(del_network_return == '')

if __name__ == '__main__':
    unittest.main()

