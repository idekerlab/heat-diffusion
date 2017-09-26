from __future__ import absolute_import

import unittest
from os import path
import ndex.client as nc
import uuid
import time
import json
import ndex.test.test_NdexClient as tt
from ndex.networkn import NdexGraph


class NdexClientTestCase(tt.NdexClientTestCase):

    def testUpdateNetworkNSetProperty(self):
        count = 0
        while count < 30 :
            try :
                with open(path.join(tt.HERE, 'The_RAS_Machine.cx'), 'r') as cx_file:
                    self._ndex.update_cx_network(cx_file, self._networkId)
                break

            except Exception as inst :
                d = json.loads(inst.response.content)
                if d.get('errorCode').startswith("NDEx_Concurrent_Modification"):
                    print("retry in 1 seconds(" + str(count) + ")")
                    count += 1
                    time.sleep(1)
                else :
                    raise inst

        summary = self._ndex.get_network_summary(self._networkId)
        self.assertEqual(summary.get(u'externalId'), self._networkId)

        profile = {'name': "Rudi's updated network",
                   'description': 'nice_description',
                   'version': 'new_version'}

        #time.sleep(6)
        count = 0
        while count < 30:
            try:
                self._ndex.update_network_profile(self._networkId,profile)
                break
            except Exception as inst:
                d = json.loads(inst.response.content)
                if d.get('errorCode').startswith("NDEx_Concurrent_Modification"):
                    print("retry in 1 seconds(" + str(count) + ")")
                    count += 1
                    time.sleep(1)
                else:
                    raise inst

        summary =  self._ndex.get_network_summary(self._networkId)
        self.assertTrue(summary['name'], profile['name'])
        cx = self._ndex.get_network_as_cx_stream(self._networkId).json()
        G = NdexGraph(cx=cx)
        self.assertEqual(len(G.edgemap),1574)
        self.assertEqual(len(G.node),513)
 #       print G.metadata_original

        print("Update network and setProperty test passed.")

if __name__ == '__main__':
    unittest.main()
