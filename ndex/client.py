#!/usr/bin/env python

import requests
import json
import ndex
from requests_toolbelt import MultipartEncoder
import os
import io
import sys

if sys.version_info.major == 3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

from requests import exceptions as req_except
import time

userAgent = 'NDEx-Python/2.0'

class Ndex:


    '''A class to facilitate communication with an NDEx server.'''
    def __init__(self, host = "http://public.ndexbio.org", username = None, password = None, update_status=False, debug = False):
        '''Creates a connection to a particular NDEx server.

                :param host: The URL of the server.
                :type host: string
                :param username: The username of the NDEx account to use. (Optional)
                :type username: string
                :param password: The account password. (Optional)
                :type password: string
        '''
        self.debug = debug
        self.version = 1.3
        self.status = {}
        self.username = username
        self.password = password
        if "localhost" in host:
            self.host = "http://localhost:8080/ndexbio-rest"
        else:
            status_url = "/rest/admin/status"

            try:
                version_url = urljoin(host, status_url)


                response = requests.get(version_url,headers = {'User-Agent': userAgent})
                response.raise_for_status()
                data = response.json()

                prop = data.get('properties')
                if(prop is not None):
                    pv = prop.get('ServerVersion')
                    if(pv is not None):
                        if not pv.startswith('2.'):
                            raise Exception("This release only supports NDEx 2.x server.")
                        else:
                            self.version = pv
                            self.host = host + "/v2"
                    else:
                        sys.stderr.write("Warning: This release doesn't fully support 1.3 version of NDEx")
                        self.version = "1.3"
                        self.host = host + "/rest"

            except req_except.HTTPError as he:
                ndex.get_logger('CLIENT').warning('Can''t determine server version.' + host + ' Server returned error -- '  + he.message)
                self.version = "1.3"
                self.host = host + "/rest"
                #TODO - how to handle errors getting server version...

#            self.host = host + "/rest"

        # create a session for this Ndex
        self.s = requests.session()
        if username and password:
            # add credentials to the session, if available
            self.s.auth = (username, password)
        if update_status:
            self.update_status()

# Base methods for making requests to this NDEx

    def set_debug_mode(self, debug):
        self.debug = debug

    def debug_response(self, response):
        if self.debug:
            print("status code: " + str(response.status_code))
            if not response.status_code == requests.codes.ok:
                print("response text: " + response.text)

    def require_auth(self):
        if not self.s.auth:
            raise Exception("this method requires user authentication")

    def put(self, route, put_json=None):
        url = self.host + route
        if self.debug:
            print("PUT route: " + url)
            if put_json is not None:
                print("PUT json: " + put_json)

        headers = self.s.headers
        headers['Content-Type'] ='application/json;charset=UTF-8'
        headers['Accept'] =  'application/json'
        headers['User-Agent']= userAgent

        if put_json is not None:
            response = self.s.put(url, data = put_json, headers = headers)
        else:
            response = self.s.put(url, headers = headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response.json()


    def post(self, route, post_json):
        url = self.host + route
        if self.debug:
            print("POST route: " + url)
            print("POST json: " + post_json)
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Cache-Control': 'no-cache',
                   'User-Agent':  userAgent,
                   }
        response = self.s.post(url, data=post_json, headers=headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response.json()

    def delete(self, route):
        url = self.host + route
        if self.debug:
            print("DELETE route: " + url)
        headers = self.s.headers
        headers['User-Agent'] = userAgent
        response = self.s.delete(url, headers = headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response.json()

    def get(self, route, get_params = None):
        url = self.host + route
        if self.debug:
            print("GET route: " + url)
        headers = self.s.headers
        headers['User-Agent'] = userAgent
        response = self.s.get(url, params = get_params, headers=headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return None
        return response.json()

    # The stream refers to the Response, not the Request
    def get_stream(self, route, get_params = None):
        url = self.host + route
        if self.debug:
            print("GET stream route: " + url)
        headers = self.s.headers
        headers['User-Agent'] = userAgent
        response = self.s.get(url, params = get_params, stream = True,headers = headers)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response

    # The stream refers to the Response, not the Request
    def post_stream(self, route, post_json):
        url = self.host + route
        if self.debug:
            print("POST stream route: " + url)
        headers = self.s.headers

        headers['Content-Type'] = 'application/json'
        headers['Accept'] ='application/json'
        headers['User-Agent'] = userAgent
        response = self.s.post(url, data=post_json, headers=headers, stream = True)
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        return response

    # The Request is streamed, not the Response
    def put_multipart(self, route, fields):
        url = self.host + route
        multipart_data = MultipartEncoder(fields=fields)
        if self.debug:
            print("PUT route: " + url)

        headers = {'Content-Type' : multipart_data.content_type,
                   'Accept' : 'application/json',
#                   'Cache-Control': 'no-cache',
                   'User-Agent':userAgent
                   }
        response = requests.put(url, data=multipart_data, headers=headers,auth=(self.username, self.password))
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        try:
            result = response.json()
        except ValueError:
            result = response.text
        return result

    # The Request is streamed, not the Response
    def post_multipart(self, route, fields):
        url = self.host + route
        multipart_data = MultipartEncoder(fields=fields)
        if self.debug:
            print("POST route: " + url)
        headers = {'Content-Type': multipart_data.content_type,
                   #'Accept': 'multipart/form-data', #'application/json',
 #                  'Cache-Control': 'no-cache',
                   'User-Agent': userAgent,
                   }
        response = requests.post(url, data=multipart_data, headers=headers, auth=(self.username, self.password))
        self.debug_response(response)
        response.raise_for_status()
        if response.status_code == 204:
            return ""
        try:
            result = response.json()
        except ValueError:
            result = response.text
        return result

# Network methods

    def save_new_network (self, cx):
        if(len(cx) > 0):
            if(cx[len(cx) - 1] is not None):
                if(cx[len(cx) - 1].get('status') is None):
                    # No STATUS element in the array.  Append a new status
                    cx.append({"status" : [ {"error" : "","success" : True} ]})
                else:
                    if(len(cx[len(cx) - 1].get('status')) < 1):
                        # STATUS element found, but the status was empty
                        cx[len(cx) - 1].get('status').append({"error" : "","success" : True})

            if sys.version_info.major == 3:
                stream = io.BytesIO(json.dumps(cx).encode('utf-8'))
            else:
                stream = io.BytesIO(json.dumps(cx))

            return self.save_cx_stream_as_new_network(stream)
        else:
            raise IndexError("Cannot save empty CX.  Please provide a non-empty CX document.")

    # CX Methods
    # Create a network based on a stream from a source CX format
    def save_cx_stream_as_new_network (self, cx_stream):
        ''' Create a new network from a CX stream, optionally providing a provenance history object to be included in the new network.

        :param cx_stream: The network stream.
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_
        '''
        self.require_auth()
        route = ''
        fields = {}
        if(self.version == "2.0"):
            route = '/network'
            fields = {
                'CXNetworkStream': ('filename', cx_stream, 'application/octet-stream')
            }
        else:
            route = '/network/asCX'
            fields = {
                'CXNetworkStream': ('filename', cx_stream, 'application/octet-stream')
            }

        return self.post_multipart(route, fields)

    # Create a network based on a JSON string or Dict in CX format
    def update_cx_network(self, cx_stream, network_id):
        '''Update the network specified by UUID network_id using the CX stream cx_stream.

        :param cx_stream: The network stream.
        :param network_id: The UUID of the network.
        :type network_id: str
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        self.require_auth()
        fields = {
            'CXNetworkStream': ('filename', cx_stream, 'application/octet-stream')
        }

        if(self.version == "2.0"):
            route = "/network/%s" % (network_id)
        else:
            route = '/network/asCX/%s' % (network_id)

        return self.put_multipart(route, fields)

    # Get a CX stream for a network
    def get_network_as_cx_stream(self, network_id):
        '''Get the existing network with UUID network_id from the NDEx connection as a CX stream.

        :param network_id: The UUID of the network.
        :type network_id: str
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        route = ""
        if(self.version == "2.0"):
            route = "/network/%s" % (network_id)
        else:
            route = "/network/%s/asCX" % (network_id)

        return self.get_stream(route)

    def get_neighborhood_as_cx_stream(self, network_id, search_string, search_depth=1, edge_limit=2500):
        ''' Get a CX stream for a subnetwork of the network specified by UUID network_id and a traversal of search_depth steps around the nodes found by search_string.

        :param network_id: The UUID of the network.
        :type network_id: str
        :param search_string: The search string used to identify the network neighborhood.
        :type search_string: str
        :param search_depth: The depth of the neighborhood from the core nodes identified.
        :type search_depth: int
        :param edge_limit: The maximum size of the neighborhood.
        :type edge_limit: int
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        if(self.version == "2.0"):
            route = "/search/network/%s/query" % (network_id)
        else:
            route = "/network/%s/query" % (network_id)

        post_data = {'searchString': search_string,
                   'searchDepth': search_depth,
                   'edgeLimit': edge_limit}
        post_json = json.dumps(post_data)
        return self.post_stream(route, post_json=post_json)


    def get_neighborhood(self, network_id, search_string, search_depth=1, edge_limit=2500):
        ''' Get the CX for a subnetwork of the network specified by UUID network_id and a traversal of search_depth steps around the nodes found by search_string.

        :param network_id: The UUID of the network.
        :type network_id: str
        :param search_string: The search string used to identify the network neighborhood.
        :type search_string: str
        :param search_depth: The depth of the neighborhood from the core nodes identified.
        :type search_depth: int
        :param edge_limit: The maximum size of the neighborhood.
        :type edge_limit: int
        :return: The CX json object.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_
        '''
        response = self.get_neighborhood_as_cx_stream(network_id, search_string, search_depth=search_depth, edge_limit=edge_limit)

        if(self.version == "2.0"):
            #response_in_json = response.json()
            #data =  response_in_json["data"]
            #return data
            return response.json()["data"]
        else:
            raise Exception("get_neighborhood is not supported for versions prior to 2.0, use get_neighborhood_as_cx_stream")


    # Search for networks by keywords
    #    network    POST    /network/search/{skipBlocks}/{blockSize}    SimpleNetworkQuery    NetworkSummary[]
    def search_networks(self, search_string="", account_name=None, start=0, size=100, include_groups=False):
        ''' Search for networks based on the search_text, optionally limited to networks owned by the specified account_name.

        :param search_string: The text to search for.
        :type search_string: str
        :param account_name: The account to search
        :type account_name: str
        :param start: The number of blocks to skip. Usually zero, but may be used to page results.
        :type start: int
        :param size: The size of the block.
        :type size: int
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        post_data = {"searchString" : search_string}
        if self.version == "2.0":
            route = "/search/network?start=%s&size=%s"  % (start, size)
            if include_groups:
                post_data["includeGroups"] = True
        else:
            route = "/network/search/%s/%s" % (start, size)

        if account_name:
            post_data["accountName"] = account_name
        post_json = json.dumps(post_data)
        return self.post(route, post_json)

    def find_networks(self, search_string="", account_name=None, skip_blocks=0, block_size=100):
        print("find_networks is deprecated, please use search_networks")
        return self.search_networks(search_string, account_name, skip_blocks, block_size)

    def search_networks_by_property_filter(self, search_parameter_dict={}, account_name=None, limit=100):
        raise Exception("This function is not supported in NDEx 2.0")
     #   self.require_auth()
     #   route = "/network/searchByProperties"
     #   if account_name:
     #       search_parameter_dict["admin"] = account_name
     #   search_parameter_dict["limit"] = limit
     #   post_json = json.dumps(search_parameter_dict)
     #   return self.post(route, post_json)

    def network_summaries_to_ids(self, network_summaries):
        network_ids = []
        for network in network_summaries:
            network_ids.append(network['externalId'] )
        return network_ids

    #    network    GET    /network/{networkUUID}       NetworkSummary
    def get_network_summary(self, network_id):
        ''' Gets information about a network.

        :param network_id: The UUID of the network.
        :type network_id: str
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        if(self.version == "2.0"):
            route = "/network/%s/summary" % (network_id)
        else:
            route = "/network/%s" % (network_id)

        return self.get(route)

    def make_network_public(self, network_id):
        ''' Makes the network specified by the network_id public.

        :param network_id: The UUID of the network.
        :type network_id: str
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        if(self.version == "2.0"):
            return self.set_network_system_properties(network_id, {'visibility': 'PUBLIC'})

        else:
            return self.update_network_profile(network_id, {'visibility': 'PUBLIC'})

    def make_network_private(self, network_id):
        ''' Makes the network specified by the network_id private.

        :param network_id: The UUID of the network.
        :type network_id: str
        :return: The response.
        :rtype: `response object <http://docs.python-requests.org/en/master/user/quickstart/#response-content>`_

        '''
        if(self.version == "2.0"):
            return self.set_network_system_properties(network_id, {'visibility': 'PRIVATE'})

        else:
            return self.update_network_profile(network_id, {'visibility': 'PRIVATE'})


    def get_task_by_id (self, task_id):
        self.require_auth()
        route = "/task/%s" % (task_id)
        return self.get(route)

    def delete_network(self, network_id, retry=5):
        self.require_auth()
        route = "/network/%s" % (network_id)
        count = 0
        while count < retry:
            try:
                return self.delete(route)
            except Exception as inst:
                d = json.loads(inst.response.content)
                if d.get('errorCode').startswith("NDEx_Concurrent_Modification"):
                    print("retry deleting network in 1 second(" + str(count) + ")")
                    count += 1
                    time.sleep(1)
                else:
                    raise inst
        raise Exception("Network is locked after " + retry + " retry.")

    def get_provenance(self, network_id):
        route = "/network/%s/provenance" % (network_id)
        return self.get(route)

    def set_provenance(self, network_id, provenance):
        self.require_auth()
        route = "/network/%s/provenance" % (network_id)
        if isinstance(provenance, dict):
            putJson = json.dumps(provenance)
        else:
            putJson = provenance
        return self.put(route, putJson)


 #   def set_network_flag(self, network_id, parameter, value):
 #       self.require_auth()
 #       route = "/network/%s/setFlag/%s=%s" % (network_id, parameter, value)
 #       return self.get(route)

    def set_read_only(self, network_id, value):
        self.require_auth()
        return self.set_network_system_properties(network_id, {"readOnly": value})

    def set_network_properties(self, network_id, network_properties):
        self.require_auth()
        route = "/network/%s/properties" % (network_id)
        if isinstance(network_properties, list):
            putJson = json.dumps(network_properties)
        elif isinstance(network_properties, basestring):
            putJson = network_properties
        else:
            raise Exception("network_properties must be a string or a list of NdexPropertyValuePair objects")
        return self.put(route, putJson)

    def set_network_system_properties(self, network_id, network_properties):
        self.require_auth()
        route = "/network/%s/systemproperty" % (network_id)
        if isinstance(network_properties, dict):
            putJson = json.dumps(network_properties)
        elif isinstance(network_properties, basestring):
            putJson = network_properties
        else:
            raise Exception("network_properties must be a string or a dict")
        return self.put(route, putJson)

    def update_network_profile(self, network_id, network_profile):
        # network profile attributes that can be updated by this method:
        #   name
        #   description
        #   version

        self.require_auth()
        if isinstance(network_profile, dict):
            if network_profile.get("visibility") and self.version.startswith("2."):
                raise Exception("Ndex 2.x doesn't support setting visibility by this function. Please use make_network_public/private function to set network visibility.")
            json_data = json.dumps(network_profile)
        elif isinstance(network_profile, basestring):
            json_data = network_profile
        else:
            raise Exception("network_profile must be a string or a dict")

        if(self.version == "2.0"):
            route = "/network/%s/profile" % (network_id)
            return self.put(route, json_data)
        else:
            route = "/network/%s/summary" % (network_id)
            return self.post(route, json_data)

    def upload_file(self, filename):
        raise Exception("This function is not supported in this release. Please use the save_new_network function to create new networks in NDEx server.")
 #       self.require_auth()
 #       fields = {

 #           'fileUpload': (filename, open(filename, 'rb'), 'application/octet-stream'),
 #           'filename': os.path.basename(filename)#filename
 #       }
 #       route = '/network/upload'
 #       return self.post_multipart(route, fields)

   # def update_network_membership_by_id(self, account_id, network_id, permission):
   #     route ="/network/{networkId}/member"  % (network_id)
   #     postData = {
   #         "permission": permission,
   #         "networkUUID": network_id,
   #         "userUUID": account_id
   #     }
   #     postJson = json.dumps(postData)
   #     self.post(route, postJson)

    def update_network_group_permission(self, groupid, networkid, permission):
        route = "/network/%s/permission?groupid=%s&permission=%s" % (networkid, groupid, permission)
        self.put(route)

    def update_network_user_permission(self, userid, networkid, permission):
        route = "/network/%s/permission?userid=%s&permission=%s" % (networkid, userid, permission)
        self.put(route)

    # Group methods

    # this group of functions are commented out for this release. We might need to wrap the showcase functions to
    # replace this function
  #  def get_network_summaries_for_group(self, group_name):
  #      route = "/group/network/%s" % (group_name)
  #      return self.get(route)

  #  def get_network_ids_for_group(self, group_name):
  #      return self.network_summaries_to_ids(self.get_network_summaries_for_group(group_name))

    def grant_networks_to_group(self, groupid, networkids, permission="READ"):
        for networkid in networkids:
            self.update_network_group_permission(groupid, networkid, permission)

    # User methods

    def get_user_by_username(self, username):
        route = "/user?username=%s" % (username)
        return self.get(route)

    def get_network_summaries_for_user(self, username):
        network_summaries = self.search_networks("", username, size=1000)

        if (network_summaries and network_summaries['networks']):
            network_summaries_list = network_summaries['networks']
        else:
            network_summaries_list = []

        return network_summaries_list

    def get_network_ids_for_user(self, username):
        network_summaries_list = self.get_network_summaries_for_user(username)

        return self.network_summaries_to_ids(network_summaries_list)

    def grant_network_to_user_by_username(self, username, network_id, permission):
        user = self.get_user_by_username(username).json
        self.update_network_user_permission(user["externalid"], network_id, permission)

    def grant_networks_to_user(self, userid, networkids, permission="READ"):
        for networkid in networkids:
            self.update_network_user_permission(userid, networkid, permission)

    # admin methods

    def update_status(self):
        route = "/admin/status"
        self.status = self.get(route)



