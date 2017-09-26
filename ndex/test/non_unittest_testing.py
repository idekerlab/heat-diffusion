import ndex.client as nc
from ndex.create_aspect import domain
import json
import time

ndex_host = "http://dev2.ndexbio.org"
username_1 = "drh"
password_1 = "drh"

def get_network(ndex, network_id):
    response = ndex.get_network_as_cx_stream(example_network_1_id)
    return response.json()

def network_id_from_uri(network_uri):
    print("network URI: %s" % network_uri)
    return network_uri.rpartition('/')[2]

def update_network_properties(ndex, network_summary, property_dict):
    # This function handles two cases:
    # - there are no subnetworks, no properties have a specified subnetwork id
    # - there is one subnetwork, all properties have that subnetwork id
    # Otherwise, raise an exception
    #
    # new properties are added
    # existing properties with the same names as in the property_dict are updated.
    # other existing properties are preserved
    #
    # Cases to be handled by explicit calls to set_network_properties, not in this function:
    # ** adding / removing items from list values
    # ** property removal
    #
    # python data types in the property_dict are mapped to CX PropertyValuePair objects
    # using ndex.create_aspect.domain to determine the data type
    subnetwork_id = None
    property_list = []
    network_id = network_summary["externalId"]
    if "properties" in network_summary:
        property_list = network_summary["properties"]
    if "subnetworkIds" in network_summary:
        if len(network_summary["subnetworkIds"]) > 1:
            raise Exception("property setting for networks with multiple subnetworks is not handled, use the lower-level set_network_properties directly")
        subnetwork_id = network_summary["subnetworkIds"][0]
        for property in property_list:
            sid = property.get("subNetworkId")
            if not sid:
                raise Exception("property setting for networks with mixed subnetwork and base network properties is not handled")
            if sid != subnetwork_id:
                raise Exception("existing property on subnetwork %s but subnetwork %s is the only one specified in the network summary" % (sid, subnetworkId))

    for name, value in property_dict.iteritems():
        update_cx_property_list(name, value, subnetwork_id, property_list)

    ndex.set_network_properties(network_id, property_list)

def update_cx_property_list(name, value, subnetwork_id, property_list):
    data_type = domain(value)
    if data_type == "unknown":
        raise Exception("in attempt to update property %s with value %s, no CX data type could be determined" % (name, value))
    for property in property_list:
        if property["predicateString"] == name:
            property["value"] = str(value)
            property["dataType"] = data_type
            return
    property_list.append({
        "predicateString": name,
        "subNetworkId": subnetwork_id,
        "value": str(value),
        "dataType": data_type
    })

example_network_1_id = "b612d677-c714-11e6-b48c-0660b7976219"

ndex = nc.Ndex(host=ndex_host, username=username_1, password=password_1,debug=True)

example_network_1_summary = ndex.get_network_summary(example_network_1_id)

print(json.dumps(example_network_1_summary, indent=4))

# Get the network

example_network_1 = get_network(ndex, example_network_1_id)

# Save it as a new network

test_network_1_uri = ndex.save_new_network(example_network_1)

test_network_1_id = network_id_from_uri(test_network_1_uri)

test_network_1_summary = ndex.get_network_summary(test_network_1_id)

print(json.dumps(test_network_1_summary, indent=4))

#----------------------------
# Update visibility

time.sleep(3)
ndex.make_network_public(test_network_1_id)
print("network is public")


#----------------------------
#  Update Properties

test_property_dict = {"string_test": "bar", "int_test": 23, "float_test": 1.001}

update_network_properties(ndex, test_network_1_summary, test_property_dict)

#ndex.set_network_properties(test_network_1_id, test_properties)


# Get the summary
time.sleep(5)
test_network_1_summary = ndex.get_network_summary(test_network_1_id)

print(json.dumps(test_network_1_summary, indent=4))

#----------------------------
# Update the profile

test_profile = {"version": "3.69",
               "name": "test - The Heart Machine",
               "description": "<h1>TEST</h1><div>The Heart Machine reads new publications on the molecular mechanisms governing cardiac cells automatically and assembles a model from them using INDRA.<br/></div>"}

ndex.update_network_profile(test_network_1_id, test_profile)

# Get the summary

test_network_1_summary = ndex.get_network_summary(test_network_1_id)

print(json.dumps(test_network_1_summary, indent=4))



# Get the

# Clean up