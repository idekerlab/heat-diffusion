import unittest

import ndex.client as nc

ndex_host = "http://dev.ndexbio.org"

#
# Python Client APIs tested:
#
#   get_user_by_username
#

class MyTestCase(unittest.TestCase):

    def test_get_user_by_username(self):

        ndex = nc.Ndex(host=ndex_host)

        user_ttt = ndex.get_user_by_username('ttt')
        self.assertTrue(str(user_ttt['externalId']) == 'f4015d8b-aaa3-11e6-8e12-06832d634f41')
        self.assertTrue(str(user_ttt['firstName']) == 'ttt')
        self.assertTrue(str(user_ttt['lastName']) == 'ttt')
        self.assertTrue(str(user_ttt['userName']) == 'ttt')
        self.assertTrue(str(user_ttt['emailAddress']) == 'ttt@ucsd.edu')

        user_drh = ndex.get_user_by_username('drh')
        self.assertTrue(str(user_drh['externalId']) == '662d2d42-7d24-11e6-9265-06832d634f41')
        self.assertTrue(str(user_drh['firstName']) == 'Doctor')
        self.assertTrue(str(user_drh['lastName']) == 'Horrible')
        self.assertTrue(str(user_drh['userName']) == 'drh')
        self.assertTrue(str(user_drh['emailAddress']) == 'dexterpratt.bio+drh@gmail.com')

if __name__ == '__main__':
    unittest.main()

