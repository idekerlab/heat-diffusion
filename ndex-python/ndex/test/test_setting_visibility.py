from __future__ import absolute_import

import unittest
from os import path
import ndex.client as nc
import uuid
import time
import json
import ndex.test.test_NdexClient as tt

class NdexClientTestCase4(tt.NdexClientRASMachineTestCase):

    def testNetworkVisibility(self):
        ndex2 = nc.Ndex(tt.TESTSERVER)
        with self.assertRaises(Exception) as context:
            ndex2.get_network_summary(self._networkId)
#        print context.exception
        count = 0
        while count < 30 :
            try :
                self._ndex.make_network_public(self._networkId)
                break
            except Exception as inst :
                d = json.loads(inst.response.content)
                if d.get('errorCode').startswith("NDEx_Concurrent_Modification"):
                    print("retry in 5 seconds(" + str(count) + ")")
                    count += 1
                    time.sleep(5)
                else :
                    raise inst

        summary = ndex2.get_network_summary(self._networkId)
        self.assertEqual(summary.get(u'externalId'), self._networkId)
        print("make_network_public() passed.")

        time.sleep(1)


        count = 0
        while count < 30:
            try:
                self._ndex.make_network_private(self._networkId)
                break
            except Exception as inst:
                d = json.loads(inst.response.content)
                if d.get('errorCode').startswith("NDEx_Concurrent_Modification"):
                    print("retry in 5 seconds(" + str(count) + ")")
                    count += 1
                    time.sleep(5)
                else:
                    raise inst

        with self.assertRaises(Exception) as context:
            ndex2.get_network_summary(self._networkId)
        print("make_network_private() passed.")

if __name__ == '__main__':
    unittest.main()
