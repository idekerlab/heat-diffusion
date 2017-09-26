from __future__ import absolute_import

import unittest
from os import path
import ndex.client as nc
import uuid
import time
import json


## The following 2 test users have to be created on the test server before running the test suite.

TESTSERVER= "http://dev.ndexbio.org"
HERE = path.abspath(path.dirname(__file__))

testUser1='pytest'
testUser2='pytest2'
testUserpasswd = 'pyunittest'

class NdexClientTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._ndex = nc.Ndex(host=TESTSERVER, username=testUser1, password=testUserpasswd, debug=True)
        with open(path.join(HERE, 'tiny_network.cx'),'r') as cx_file:
            cls._nrc = cls._ndex.save_cx_stream_as_new_network(cx_file)
            networkId = uuid.UUID('{'+cls._nrc[-36:] + '}')
            cls._networkId = str(networkId)
            time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls._ndex.delete_network(cls._networkId)
        print("Network " + cls._networkId + " deleted from " + cls._ndex.username +" account " + cls._ndex.host)

class NdexClientRASMachineTestCase(NdexClientTestCase):
    @classmethod
    def setUpClass(cls):
        cls._ndex = nc.Ndex(host=TESTSERVER, username=testUser1, password=testUserpasswd, debug=True)
        with open(path.join(HERE, 'The_RAS_Machine.cx'),'r') as cx_file:
            cls._nrc = cls._ndex.save_cx_stream_as_new_network(cx_file)
            networkId = uuid.UUID('{'+cls._nrc[-36:] + '}')
            cls._networkId = str(networkId)
            time.sleep(2)

class NdexClientTestCase1(unittest.TestCase):

    def testConstructorException(self):
        with self.assertRaises(Exception):
            print("testing ndex client constructor.")
            ndex = nc.Ndex(host="www.google.com", username="foo", password="bar", debug=True)

    def testConstructor2 (self):
        ndex = nc.Ndex(host=TESTSERVER,update_status=True,debug=True)
        self.assertTrue(ndex.status.get('properties')['ServerVersion'].startswith("2."))


class NdexClientTestCase2(NdexClientTestCase):


    def testGetNetwork(self):
        summary = self._ndex.get_network_summary(self._networkId)
        self.assertEqual(summary.get(u'externalId'), self._networkId)
        print("get_network_summary() passed.")

    def testGrantGroupPermission(self):
        ndex2 = nc.Ndex(TESTSERVER, username=testUser2 , password = testUserpasswd,debug=True)
        with self.assertRaises(Exception) as context:
            ndex2.get_network_summary(self._networkId)
#        print context.exception
        count = 0
        while count < 30 :
            try :
                self._ndex.update_network_group_permission('d7ef9957-de81-11e6-8835-06832d634f41', self._networkId, 'READ')
                count = 60
            except Exception as inst :
                d = json.loads(inst.response.content)
                if d.get('errorCode').startswith("NDEx_Concurrent_Modification") :
                    print("retry in 3 seconds(" + str(count) + ")")
                    count += 1
                    time.sleep(3)
                else :
                    raise inst

        summary = ndex2.get_network_summary(self._networkId)
        self.assertEqual(summary.get(u'externalId'), self._networkId)
        print("update_network_group_permission() passed.")



class NdexClientTestCase3(NdexClientTestCase):

    def testGrantUserPermission(self):
        ndex2 = nc.Ndex(TESTSERVER, username=testUser2 , password = testUserpasswd, debug=True)
        with self.assertRaises(Exception) as context:
            ndex2.get_network_summary(self._networkId)
#        print context.exception
        count = 0
        while count < 30 :
            try :
                # User UUID of testUser2 in this test
                self._ndex.update_network_user_permission('0a9d3b58-de82-11e6-8835-06832d634f41', self._networkId, 'READ')
                break
            except Exception as inst :
                d = json.loads(inst.response.content)
                if d.get('errorCode').startswith("NDEx_Concurrent_Modification") :
                    print("retry in 3 seconds(" + str(count) + ")")
                    count += 1
                    time.sleep(3)
                else :
                    raise inst

        summary = ndex2.get_network_summary(self._networkId)
        self.assertEqual(summary.get(u'externalId'), self._networkId)
        print("update_network_user_permission() passed.")


class NdexClientTestCase3(NdexClientTestCase):

    def testUpdateNetwork(self):
        time.sleep(5)
        summary1 = self._ndex.get_network_summary(self._networkId)
        self.assertEqual(summary1['name'], 'rudi')
        time.sleep(5)
        count = 0
        while count < 30 :
            try :
                with open(path.join(HERE, 'A549-SL-network.cx'), 'r') as cx_file:
                    self._ndex.update_cx_network(cx_file, self._networkId)
                break
            except Exception as inst :
                if inst.response and inst.response.get('content') :
                    d = json.loads(inst.response.content)
                    if d and d.get('errorCode') and d.get('errorCode').startswith("NDEx_Concurrent_Modification") :
                        print("retry in 1 seconds(" + str(count) + ")")
                        count += 1
                        time.sleep(1)
                    else:
                        raise inst
                else :
                    raise inst

      #  time.sleep(1)

        count = 0
        while count < 30:
            try:
                summary1 = self._ndex.get_network_summary(self._networkId)
                if ( summary1.get('isValid') ):
                    break
                else:
                     count+=1
            except Exception as inst:
                if (not inst.response) or (not inst.response.get('content')):
                    raise inst
                d = json.loads(inst.response.content)
                if d and d.get('errorCode') and d.get('errorCode').startswith("NDEx_Concurrent_Modification"):
                    print("retry in 1 seconds(" + str(count) + ")")
                    count += 1
                    time.sleep(1)
                else:
                    raise inst

        self.assertEqual(summary1.get(u'name'), "A549-SL-network")
        print("update_cx_network() passed.")


if __name__ == '__main__':
    unittest.main()
