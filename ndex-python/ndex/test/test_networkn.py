__author__ = 'aarongary'

import unittest
import ndex
from ndex.networkn import  FilterSub

class NetworkNTests(unittest.TestCase):
    #==============================
    # TEST LARGE NETWORK
    #==============================
    def test_data_to_type(self):
        self.assertTrue(self, ndex.networkn.data_to_type('true','boolean'))
        print(type(ndex.networkn.data_to_type('1.3','double')))
        print(type(ndex.networkn.data_to_type('1.3','float')))
        print(type(ndex.networkn.data_to_type('1','integer')))
        print(type(ndex.networkn.data_to_type('1','long')))
        print(type(ndex.networkn.data_to_type('1','short')))
        print(type(ndex.networkn.data_to_type('1','string')))
        list_of_boolean = type(ndex.networkn.data_to_type('["true","false"]','list_of_boolean'))
        print(list_of_boolean)

        list_of_double = ndex.networkn.data_to_type('[1.3,1.4]','list_of_double')
        print(list_of_double)

        list_of_float = ndex.networkn.data_to_type('[1.3,1.4]','list_of_float')
        print(list_of_float)

        list_of_integer = ndex.networkn.data_to_type('[1,4]','list_of_integer')
        print(list_of_integer)

        list_of_long = ndex.networkn.data_to_type('[1,4]','list_of_long')
        print(list_of_long)

        list_of_short = ndex.networkn.data_to_type('[1,4]','list_of_short')
        print(list_of_short)

        list_of_string = ndex.networkn.data_to_type(['abc'],'list_of_string')
        print(list_of_string)


if __name__ == '__main__':
    unittest.main()