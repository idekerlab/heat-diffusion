import unittest

import ndex.client as nc
import time
from os import path


ndex_host = "http://dev.ndexbio.org"
ndex_network_resource = "/v2/network/"
username_1 = "ttt"
password_1 = "ttt"

example_network_1 = 'A549-SL-network.cx'

# Python Client APIs tested:
#
#   save_cx_stream_as_new_network
#   get_network_as_cx_stream
#   delete_network
#


class MyTestCase(unittest.TestCase):

    def test_get_network_as_cx_stream(self):
        ndex = nc.Ndex(host=ndex_host, username=username_1, password=password_1)

        with open(path.join(path.abspath(path.dirname(__file__)),example_network_1), 'r') as file_handler:
            network_in_cx_from_file = file_handler.read()

        # test save_cx_stream_as_new_network
        test_network_1_uri = ndex.save_cx_stream_as_new_network(network_in_cx_from_file)
        self.assertTrue(test_network_1_uri.startswith(ndex_host + ndex_network_resource))

        network_UUID = str(test_network_1_uri.split("/")[-1])

        network_as_cx_stream = ndex.get_network_as_cx_stream(network_UUID)
        network_as_cx = str(network_as_cx_stream.text)

        self.assertTrue(network_in_cx_from_file == network_as_cx)

        time.sleep(10)


        # test delete_network
        del_network_return = ndex.delete_network(network_UUID)
        self.assertTrue(del_network_return == '')



if __name__ == '__main__':
    unittest.main()

