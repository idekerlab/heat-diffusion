import networkx as nx
from networkx.classes.multidigraph import MultiDiGraph
import ndex.create_aspect as ca
import io
import json
import copy
import ndex.client as nc
from time import time
from six import string_types
import sys

#NDEXGRAPH_RESERVED_ATTRIBUTES = [
#    "subnetwork_id"
#    "view_id",
#    "max_node_id",
#    "max_edge_id",
#    "max_citation_id",
#    "max_support_id",
#    "pos",
#    "unclassified_cx",
#    "metadata_original",
#    "status",
#    "citation_map",
#    "node_citation_map",
#    "edge_citation_map",
#    "support_map",
#    "node_support_map",
#    "edge_support_map",
#    "self.edgemap"
#]


def parse_attribute(attribute):
    value = attribute['v']
    if 'd' in attribute:
        d = attribute['d']
        value = data_to_type(value,d)
    return value


def data_to_type(data, data_type):
    return_data = None

    if(type(data) is str):
        data = data.replace('[', '').replace(']','')
        if('list_of' in data_type):
            data = data.split(',')

    if data_type == "boolean":
        if(type(data) is str):
            return_data = data.lower() == 'true'
        else:
            return_data = bool(data)
    elif data_type == "byte":
        return_data = str(data).encode()
    elif data_type == "char":
        return_data = str(data)
    elif data_type == "double":
        return_data = float(data)
    elif data_type == "float":
        return_data = float(data)
    elif data_type == "integer":
        return_data = int(data)
    elif data_type == "long":
        return_data = int(data)
    elif data_type == "short":
        return_data = int(data)
    elif data_type == "string":
        return_data = str(data)
    elif data_type == "list_of_boolean":
        # Assumption: if the first element is a string then so are the rest...
        if(type(data[0]) is str):
            return_data = [s.lower() == 'true' for s in data]
        else:
            return_data = [bool(s) for s in data]
    elif data_type == "list_of_byte":
        return_data = [bytes(s) for s in data]
    elif data_type == "list_of_char":
        return_data = [str(s) for s in data]
    elif data_type == "list_of_double":
        return_data = [float(s) for s in data]
    elif data_type == "list_of_float":
        return_data = [float(s) for s in data]
    elif data_type == "list_of_integer":
        return_data = [int(s) for s in data]
    elif data_type == "list_of_long":
        return_data = [int(s) for s in data]
    elif data_type == "list_of_short":
        return_data = [int(s) for s in data]
    elif data_type == "list_of_string":
        return_data = [str(s) for s in data]
    else:
        return None

    return return_data

class NdexGraph (MultiDiGraph):
    """A graph compatible with NDEx"""
    def __init__(self, cx=None, server=None, username=None, password=None, uuid=None, networkx_G=None, data=None, **attr):
        """There are generally four ways to create a graph.

            1. An empty graph. G = NdexGraph()
            2. Using a cx dictionary. G = NdexGraph(cx)
            3. Loading it from an NDEx server.
                G = NdexGraph(server='http://test.ndexbio.org' uuid='983a2b93-2c55-11e6-a7c5-0630eb0972a1')
            4. Just like any other NetworkX MultiDiGraph().
            5. From an existing networkx graph. G = NdexGraph(networkx_G=networkx_G)

        """
        MultiDiGraph.__init__(self, data, **attr)
        self.subnetwork_id = None
        self.view_id = None
        self.max_node_id = None
        self.max_edge_id = None
        self.max_citation_id = None
        self.max_support_id = None
        self.pos = {}
        self.unclassified_cx = []
        self.metadata_original = None
        self.status = {'status': [{'error': '','success': True}]} #Added because status is now required
        self.citation_map = {}
        self.node_citation_map = {}
        self.citation_reference_map = {}
        self.edge_citation_map = {}
        self.support_map = {}
        self.support_reference_map = {}
        self.node_support_map = {}
        self.edge_support_map = {}
        self.function_term_map = {}
        self.reified_edges = {}
        self.provenance = None
        self.namespaces = {}
     #   self.edge_type_map = {}  # stores the mapping from cx edgeId to its 'i' attribute
     #   self.node_prepresent_map ={} #stores the mapping from cx nodeId to its represents

        # Maps edge ids to node ids. e.g. { edge1: (source_node, target_node), edge2: (source_node, target_node) }
        self.edgemap = {}

        if networkx_G is not None:
            node_id_x = 0
            node_dict_x = {}
            self.max_edge_id = 0
            for node_name, node_attr in networkx_G.nodes_iter(data=True):
                if 'name' in node_attr:
                    self.add_node(node_id_x, node_attr)
                    print(node_attr)
                else:
                    self.add_node(node_id_x, node_attr, name=node_name)
                node_dict_x[node_name] = node_id_x
                node_id_x += 1

            if isinstance(networkx_G, nx.MultiGraph):
                for s, t, key, data in networkx_G.edges_iter(keys=True, data=True):
                    self.add_edge(node_dict_x[s], node_dict_x[t], key, data) #s, t, key, data)
            else:
                for s, t, edge_attr in networkx_G.edges_iter(data=True):
                    self.add_edge(node_dict_x[s], node_dict_x[t], self.max_edge_id, edge_attr)
                    self.max_edge_id += 1

            if hasattr(networkx_G, 'pos'):
                self.pos = {node_dict_x[a] : b for a, b in networkx_G.pos.items()}
                self.subnetwork_id = 1
                self.view_id = 1
            return

        if not cx and server and uuid:
            ndex = nc.Ndex(server,username,password)
            cx = ndex.get_network_as_cx_stream(uuid).json()
            if not cx:
                raise RuntimeError("Failed to retrieve network with uuid " + uuid + " from " + server)
            else:
                metadata_temp = (item for item in cx if item.get("metaData") is not None).next()
                if(metadata_temp is not None):
                    self.metadata_original = metadata_temp["metaData"]

        # If there is no CX to process, just return.
        if cx == None:
            return

        # First pass, get information about subnetworks.
        for aspect in cx:
            if 'status' in aspect :
                if aspect['status'][0]['success']:
                    continue
                else:
                    raise RuntimeError("Error in CX status aspect: " + aspect['status'][0]['error'])
            if "numberVerification" in aspect:
                # new status and numberVerification will be added when the network is output to_cx
                continue
            if 'subNetworks' in aspect:
                for subnetwork in aspect.get('subNetworks'):
                    id = subnetwork.get('@id')
                    if self.subnetwork_id != None:
                        raise ValueError("networkn does not support collections!")
                    self.subnetwork_id = id
            elif 'cyViews' in aspect:
                for cyViews in aspect.get('cyViews'):
                    id = cyViews.get('@id')
                    if self.view_id != None:
                        raise ValueError("networkn does not support more than one view!")
                    self.view_id = id
            elif 'metaData' in aspect:
                self.metadata_original = aspect["metaData"]
                # Strip metaData
                continue
            elif 'provenanceHistory' in aspect:
                elements = aspect['provenanceHistory']
                if len(elements) > 0:
                    if len(elements)>1 or self.provenance :
                        raise RuntimeError('profenanceHistory aspect can only have one element.')
                    else :
                        self.provenance = elements[0]
            elif '@context' in aspect :
                elements = aspect['@context']
                if len(elements) > 0:
                    if  len(elements) > 1 or self.namespaces:
                        raise RuntimeError('@context aspect can only have one element')
                    else :
                        self.namespaces = elements[0]
            else:
                self.unclassified_cx.append(aspect)

            cx = self.unclassified_cx

        # Second pass, just build basic graph.
        self.unclassified_cx = []
        for aspect in cx:
            if 'nodes' in aspect:
                for node in aspect.get('nodes'):
                    id = node.get('@id')
                    name = node['n'] if 'n' in node else None
                    if name:
                        self.add_node(id, name=name)
                    else:
                        self.add_node(id)
                    represents = node.get('r') if 'r' in node else None
                    if represents:
                        self.node.get(id)['represents'] = represents

            elif 'edges' in aspect:
                for edge in aspect.get('edges'):
                    id = edge.get('@id')
                    interaction = edge['i'] if 'i' in edge else None
                    s = edge['s']
                    t = edge['t']
                    self.edgemap[id] = (s, t)
                    if interaction:
                        self.add_edge(s, t, key=id, interaction=interaction)
                    else:
                        self.add_edge(s, t, key=id)
            else:
                self.unclassified_cx.append(aspect)
        cx = self.unclassified_cx

        # Third pass, handle attributes
        # Notes. Not handled, datatypes.
        self.unclassified_cx = []
        for aspect in cx:
            if 'networkAttributes' in aspect:
                for networkAttribute in aspect['networkAttributes']:
                    name = networkAttribute['n']
                    # special: ignore selected
           #         if name == 'selected':
           #             continue
                    value = parse_attribute(networkAttribute)
                    value = networkAttribute['v']
                    if value is not None:
                        if 's' in networkAttribute or name not in self.graph:
                            self.graph[name] = value

            elif 'nodeAttributes' in aspect:
                for nodeAttribute in aspect['nodeAttributes']:
                    id = nodeAttribute['po']
                    name = nodeAttribute['n']
                    value = parse_attribute(nodeAttribute)
                    if value is not None:
                        if 's' in nodeAttribute or name not in self.node[id]:
                            self.node[id][name] = value

            elif 'edgeAttributes' in aspect:
                for edgeAttribute in aspect['edgeAttributes']:
                    id = edgeAttribute['po']
                    s, t = self.edgemap[id]
                    name = edgeAttribute['n']
                    value = parse_attribute(edgeAttribute)
                    if value is not None:
                        if 's' in edgeAttribute or name not in self[s][t][id]:
                            self[s][t][id][name] = value
            else:
                self.unclassified_cx.append(aspect)

        cx = self.unclassified_cx
        self.unclassified_cx = []

        # Fourth pass, node locations
        self.pos = {}
        for aspect in cx:
            if 'cartesianLayout' in aspect:
                for nodeLayout in aspect['cartesianLayout']:
                    id = nodeLayout['node']
                    x = nodeLayout['x']
                    y = nodeLayout['y']
                    self.pos[id] = [x,y]
            else:
                self.unclassified_cx.append(aspect)

        cx = self.unclassified_cx
        self.unclassified_cx = []

        # Fifth pass, citations
        for aspect in cx:
            if 'citations' in aspect:
                for citation in aspect['citations']:
                    attributes = copy.deepcopy(citation)
                    attributes.pop("@id")
                    self.citation_map[citation["@id"]] = attributes
                    self.citation_reference_map[citation["@id"]] = 0
            else:
                self.unclassified_cx.append(aspect)

        cx = self.unclassified_cx
        self.unclassified_cx = []

        # Sixth pass, supports, the attributes include the mapping to their citation (if any) by its id
        for aspect in cx:
            if 'supports' in aspect:
                for support in aspect['supports']:
                    attributes = copy.deepcopy(support)
                    attributes.pop("@id")
                    self.support_map[support["@id"]] = attributes
                    self.support_reference_map[support["@id"]] = 0

            else:
                self.unclassified_cx.append(aspect)

        cx = self.unclassified_cx
        self.unclassified_cx = []
        # Seventh pass, map supports and citations to nodes and edges
        for aspect in cx:
            if 'nodeCitations' in aspect:
                for node_citation in aspect['nodeCitations']:
                    for node in node_citation["po"]:
                        self.node_citation_map[node] = node_citation["citations"]
                        for citation_id in node_citation["citations"]:
                            cit_ref = self.citation_reference_map.get(citation_id)
                            if(cit_ref is not None):
                                self.citation_reference_map[citation_id] += 1
            elif 'edgeCitations' in aspect:
                for edge_citation in aspect['edgeCitations']:
                    for edge in edge_citation["po"]:
                        self.edge_citation_map[edge] = edge_citation["citations"]
                        for citation_id in edge_citation["citations"]:
                            cit_ref = self.citation_reference_map.get(citation_id)
                            if(cit_ref is not None):
                                self.citation_reference_map[citation_id] += 1
            elif 'nodeSupports' in aspect:
                for node_support in aspect['nodeSupports']:
                    for node_sup_po in node_support["po"]:
                        self.node_support_map[node_sup_po] = node_support["supports"]
                        for supports_id in node_support["supports"]:
                            sup_ref = self.support_reference_map.get(supports_id)
                            if(sup_ref is not None):
                                self.support_reference_map[supports_id] += 1
            elif 'edgeSupports' in aspect:
                for edge_support in aspect['edgeSupports']:
                    for edge_sup in edge_support["po"]:
                        self.edge_support_map[edge_sup] = edge_support["supports"]
                        for supports_id in edge_support["supports"]:
                            sup_ref = self.support_reference_map.get(supports_id)
                            if(sup_ref is not None):
                                self.support_reference_map[supports_id] += 1
            elif 'functionTerms' in aspect:
                for function_term in aspect['functionTerms']:
                    self.function_term_map[function_term["po"]] = function_term
            elif 'reifiedEdges' in aspect:
                for reified_edge in aspect["reifiedEdges"]:
                    self.reified_edges [reified_edge['node']] = reified_edge
            else:
                self.unclassified_cx.append(aspect)


    def create_from_aspects(self, aspect, aspect_type):
        """ adds the corresponding networkn properties from a self-contained aspect.

        :param aspect: json based aspect
        :type aspect: dict
        :param aspect_type: name of aspect
        :type aspect_type: str
        :return: None
        :rtype: None
        """
        self.pos = {}
        #self.unclassified_cx = []

        if 'subNetworks' == aspect_type:
            for subnetwork in aspect:
                id = subnetwork['@id']
                if self.subnetwork_id != None:
                    raise ValueError("networkn does not support collections!")
                self.subnetwork_id = id

        elif 'cyViews' == aspect_type:
            for cyViews in aspect:
                id = cyViews['@id']
                if self.view_id != None:
                    raise ValueError("networkn does not support more than one view!")
                self.view_id = id

        elif 'metaData' == aspect_type:
            this_type_is_ignored_for_now = 'placeholder'

        elif 'nodes' == aspect_type:
            for node in aspect:
                id = node['@id']
                name = node['n'] if 'n' in node else None
                if name:
                    self.add_node(id, name=name)
                else:
                    self.add_node(id)
                represents = node['r'] if 'r' in node else None
                if represents:
                    self.node[id]['represents'] = represents

        elif 'edges' == aspect_type:
            for edge in aspect:
                id = edge['@id']
                interaction = edge['i'] if 'i' in edge else None
                s = edge['s']
                t = edge['t']
                self.edgemap[id] = (s, t)
                if interaction:
                    self.add_edge(s, t, key=id, interaction=interaction)
                else:
                    self.add_edge(s, t, key=id)

        elif 'networkAttributes' == aspect_type:
            for networkAttribute in aspect:
                name = networkAttribute['n']
                # special: ignore selected
                if name == 'selected':
                    continue
                value = networkAttribute['v']
                if 'd' in networkAttribute:
                    d = networkAttribute['d']
                    if d == 'boolean':
                        value = value.lower() == 'true'
                if 's' in networkAttribute or name not in self.graph:
                    self.graph[name] = value

        elif 'nodeAttributes' == aspect_type:
            for nodeAttribute in aspect:
                id = nodeAttribute['po']
                name = nodeAttribute['n']
                # special: ignore selected
                if name == 'selected':
                    continue
                value = nodeAttribute['v']
                if 'd' in nodeAttribute:
                    d = nodeAttribute['d']
                    if d == 'boolean':
                        value = value.lower() == 'true'
                if 's' in nodeAttribute or name not in self.node[id]:
                    self.node[id][name] = value

        elif 'edgeAttributes' == aspect_type:
            for edgeAttribute in aspect:
                id = edgeAttribute['po']
                s, t = self.edgemap[id]
                name = edgeAttribute['n']
                # special: ignore selected and shared_name columns
                if name == 'selected' or name == 'shared name':
                    continue
                value = edgeAttribute['v']
                if 'd' in edgeAttribute:
                    d = edgeAttribute['d']
                    if d == 'boolean':
                        value = value.lower() == 'true'
                if 's' in edgeAttribute or name not in self[s][t][id]:
                    self[s][t][id][name] = value

        elif 'cartesianLayout' == aspect_type:
            for nodeLayout in aspect:
                id = nodeLayout['node']
                x = nodeLayout['x']
                y = nodeLayout['y']
                self.pos[id] = [x,y]

        else:
            self.unclassified_cx.append({aspect_type: aspect})
            #self.unclassified_cx.append(aspect)

    def create_from_edge_list(self, edge_list, interaction='interacts with'):
        """ Create a network from a list of tuples that represent edges. Each tuple consists of  two nodes names that are to be connected. This operation will first clear ALL data already in the network.

            :param edge_list: A list of tuples containing node names that are connected.
            :type edge_list: list
            :param interaction: Either a list of interactions that is the same length as the edge_list a single string with an interaction to be applied to all edges.
            :type interaction: str or list

        """
        self.clear()
        node_names_added = {}
        for i, edge in enumerate(edge_list):
            #name 1 and name 2 are the node names from the tuple.
            name1 = edge[0]
            name2 = edge[1]
            if name1 in node_names_added:
                n1 = node_names_added[name1]
            else:
                n1 = self.add_new_node(name1)
                node_names_added[name1] = n1
            if name2 in node_names_added:
                n2 = node_names_added[name2]
            else:
                n2 = self.add_new_node(name2)
                node_names_added[name2] = n2

            edge_interaction = interaction if isinstance(interaction,string_types) else interaction[i]
            self.add_edge_between(n1,n2,edge_interaction)

    #------------------------------------------
    #       NETWORK
    #------------------------------------------

    def clear(self):
        """Eliminate all graph data in this network.  The network will then be empty and can be filled with data starting "from scratch".


        """
        super(NdexGraph, self).clear()
        self.subnetwork_id = None
        self.view_id = None
        self.max_node_id = None
        self.max_edge_id = None
        self.max_citation_id = None
        self.max_support_id = None
        self.pos = None
        self.edgemap = {}
        self.unclassified_cx = []
        self.citation_map = {}
        self.node_citation_map = {}
        self.edge_citation_map = {}
        self.support_map = {}
        self.node_support_map = {}
        self.edge_support_map = {}

    def set_name(self, name):
        """Set the name of this graph

        :param name: A descriptive name for the network which will show up on NDEx.
        :type name: str

        """
        self.graph['name'] = name

    def set_network_attribute(self, name, value):
    #    if name in NDEXGRAPH_RESERVED_ATTRIBUTES:
    #        raise ValueError(str(name) + " is a reserved network attribute name and may not be set by this method")
        self.graph[name] = value

    def get_name(self):
        """Get the name of this graph

        :return: The descriptive name for this network.
        :rtype: str

        """
        if 'name' in self.graph:
            return self.graph['name']
        return None

    def set_namespace (self, namespaceMap):
        self.namespaces = namespaceMap

    def show_stats(self):
        """Show the number of nodes and edges."""
        print("Nodes: %d" % self.number_of_nodes())
        print("Edges: %d" % self.number_of_edges())

    def set_edgemap(self, edgemap):
        self.edgemap = edgemap

    def subgraph_new(self, nbunch):

        return_graph = self.subgraph(nbunch[:400])

        for s, t, edge_id, data in return_graph.edges_iter(keys=True, data=True):
            return_graph.edgemap[edge_id] = (s, t)

        return return_graph

    #------------------------------------------
    #       OUTPUT
    #------------------------------------------

    def to_cx(self, md_dict=None):
        """Convert this network to a CX dictionary

        :return: The cx dictionary that represents this network.
        :rtype: dict
        """
        has_single_subnetwork = False
        if self.subnetwork_id and self.view_id:
            has_single_subnetwork = True
        if (self.subnetwork_id and not self.view_id) or (not self.subnetwork_id and self.view_id):
            raise ValueError("subnetwork and view inconsistent. subnetwork id = %s and view id = %s" % (self.subnetwork_id, self.view_id))

        G = self
        cx = []
        cx += ca.number_verification()
        cx += self.generate_metadata(G, self.unclassified_cx) #ca.metadata(metadata_dict=md_dict)

        #always add context first.
        if self.namespaces:
            cx += ca.namespaces(G)

        network_attributes = ca.network_attributes(G, has_single_subnetwork)
        cx += network_attributes

        if has_single_subnetwork:
            cx += ca.subnetworks(G, self.subnetwork_id, self.view_id)
        # - don't output subnetworks if the NdexGraph doesn't know about them.
        # - All operations that add aspects for visual properties, cartesian coordinates,
        #   or otherwise refer to subnetworks must ensure that subnetwork and view ids are set
        # else:
        #     cx += ca.subnetworks(G, 0, 0)
        cx += ca.nodes(G)
        cx += ca.edges(G)
        node_att = ca.node_attributes(G, has_single_subnetwork)
        if(node_att is not None):
            cx += node_att

        edge_att = ca.edge_attributes(G, has_single_subnetwork)
        if(edge_att is not None):
            cx += edge_att

        if self.pos and len(self.pos):
            if has_single_subnetwork:
                cx += ca.cartesian(G, self.view_id)
            else:
                raise ValueError("NdexGraph positions (g.pos) set without setting view and subnetwork ids")

        if len(self.citation_map) > 0:
            cx += ca.citations(G)
        if len(self.node_citation_map) > 0:
            cx += ca.node_citations(G)
        if len(self.edge_citation_map) > 0:
            cx += ca.edge_citations(G)
        if len(self.support_map) > 0:
            cx += ca.supports(G)
        if len(self.node_support_map) > 0:
            cx += ca.node_supports(G)
        if len(self.edge_support_map) > 0:
            cx += ca.edge_supports(G)
        if len(self.function_term_map) > 0:
            cx += ca.function_terms(G)
        if len(self.reified_edges) > 0:
            cx += ca.reified_edges(G)
        if self.provenance:
            cx += ca.provenance(G)

        for fragment in self.unclassified_cx:
            # filter out redundant networkRelations
            if not "networkRelations" in fragment:
                cx += [fragment]

        #cx += self.unclassified_cx
        cx += [self.status]

        return cx

    # Obsolete?
    def add_status(self, status):
        if(len(self.status['status']) == 0):
            self.status['status'].append(status)

    def generate_metadata(self, G, unclassified_cx):
        return_metadata = []
        consistency_group = 1
        if(self.metadata_original is not None):
            for mi in self.metadata_original:
                if(mi.get("consistencyGroup") is not None):
                    if(mi.get("consistencyGroup") > consistency_group):
                        consistency_group = mi.get("consistencyGroup")

            consistency_group += 1 # bump the consistency group up by one

            print("consistency group max: " + str(consistency_group))

        # ========================
        # @context metadata
        # ========================
        if  self.namespaces:
            return_metadata.append(
                {
                    "consistencyGroup": consistency_group,
                    "elementCount": 1,
                    "name": "@context",
                    "properties": [],
                    "version": "1.0"
                }
            )

        #========================
        # Nodes metadata
        #========================
        node_ids = [n[0] for n in G.nodes_iter(data=True)]
        if(len(node_ids) < 1):
            node_ids = [0]
        return_metadata.append(
            {
                "consistencyGroup" : consistency_group,
                "elementCount" : len(node_ids),
                "idCounter": max(node_ids),
                "name" : "nodes",
                "properties" : [ ],
                "version" : "1.0"
            }
        )

        #========================
        # Edges metadata
        #========================
        edge_ids = [e[2]for e in G.edges_iter(data=True, keys=True)]
        if(len(edge_ids) < 1):
            edge_ids = [0]
        return_metadata.append(
            {
                "consistencyGroup" : consistency_group,
                "elementCount" : len(edge_ids),
                "idCounter": max(edge_ids),
                "name" : "edges",
                "properties" : [ ],
                "version" : "1.0"
            }
        )

        #=============================
        # Network Attributes metadata
        #=============================
        if(len(G.graph) > 0):
            return_metadata.append(
                {
                    "consistencyGroup" : consistency_group,
                    "elementCount" : len(G.graph),
                    "name" : "networkAttributes",
                    "properties" : [ ],
                    "version" : "1.0"
                }
            )

        #===========================
        # Node Attributes metadata
        #===========================
        #id_max = 0
        attr_count = 0
        for node_id , attributes in G.nodes_iter(data=True):
            for attribute_name in attributes:
                if attribute_name != "name" and attribute_name != "represents":
                    attr_count += 1



        #
        # for n, nattr in G.nodes(data=True):
        #     if(bool(nattr)):
        #         attr_count += len(nattr.keys())
        #
        #     if(n > id_max):
        #         id_max = n

        if(attr_count > 0):
            return_metadata.append(
                {
                    "consistencyGroup" : consistency_group,
                    "elementCount" : attr_count,
                    #"idCounter": id_max,
                    "name" : "nodeAttributes",
                    "properties" : [ ],
                    "version" : "1.0"
                }
            )

        #===========================
        # Edge Attributes metadata
        #===========================
        #id_max = 0
        attr_count = 0
        for s, t, id, a in G.edges(data=True, keys=True):
            if(bool(a)):
                for attribute_name in a:
                    if attribute_name != "interaction":
                        attr_count += 1
                #attr_count += len(a.keys())

            # if(id > id_max):
            #     id_max = id

        if(attr_count > 0):
            return_metadata.append(
                {
                    "consistencyGroup" : consistency_group,
                    "elementCount" : attr_count,
                    #"idCounter": id_max,
                    "name" : "edgeAttributes",
                    "properties" : [ ],
                    "version" : "1.0"
                }
            )

        #===========================
        # cyViews metadata
        #===========================
        if self.view_id != None:
            return_metadata.append(
                {
                    "elementCount": 1,
                    "name": "cyViews",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )

        #===========================
        # subNetworks metadata
        #===========================
        if self.subnetwork_id != None:
            return_metadata.append(
                {
                    "elementCount": 1,
                    "name": "subNetworks",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )

        #===========================
        # networkRelations metadata
        #===========================
        if self.subnetwork_id != None and self.view_id != None:
            return_metadata.append(
                {
                    "elementCount": 2,
                    "name": "networkRelations",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )

        #===========================
        # citations and supports metadata
        #===========================
        if len(self.support_map) > 0:
            return_metadata.append(
                {
                    "elementCount": len(self.support_map),
                    "name": "supports",
                    "properties": [],
                    "idCounter": max(self.support_map.keys()),
                    "consistencyGroup" : consistency_group
                }
            )

        if len(self.node_support_map) > 0:
            return_metadata.append(
                {
                    "elementCount": len(self.node_support_map),
                    "name": "nodeSupports",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )
        if len(self.edge_support_map) > 0:
            return_metadata.append(
                {
                    "elementCount": len(self.edge_support_map),
                    "name": "edgeSupports",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )

        if len(self.citation_map) > 0:
            return_metadata.append(
                {
                    "elementCount": len(self.citation_map),
                    "name": "citations",
                    "properties": [],
                    "idCounter": max(self.citation_map.keys()),
                    "consistencyGroup" : consistency_group
                }
            )

        if len(self.node_citation_map) > 0:
            return_metadata.append(
                {
                    "elementCount": len(self.node_citation_map),
                    "name": "nodeCitations",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )

        if len(self.edge_citation_map) > 0:
            return_metadata.append(
                {
                    "elementCount": len(self.edge_citation_map),
                    "name": "edgeCitations",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )

        if len(self.function_term_map) > 0:
            return_metadata.append(
                {
                    "elementCount": len(self.function_term_map),
                    "name": "functionTerms",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )

        if len(self.reified_edges) > 0:
            return_metadata.append(
                {
                    "elementCount": len(self.reified_edges),
                    "name": "reifiedEdges",
                    "properties": [],
                    "consistencyGroup" : consistency_group
                }
            )

        #===========================
        # ndexStatus metadata
        #===========================
        return_metadata.append(
            {
                "consistencyGroup": consistency_group,
                "elementCount": 1,
                "name": "ndexStatus",
                "properties": [],
                "version": "1.0"
            }
        )

        #===========================
        # cartesianLayout metadata
        #===========================
        if self.pos and len(self.pos) > 0:
            return_metadata.append(
                {
                    "consistencyGroup": consistency_group,
                    "elementCount": len(self.pos),
                    "name": "cartesianLayout",
                    "properties": [],
                    "version": "1.0"
                }
            )

        #===========================
        # OTHER metadata
        #===========================
        for asp in self.unclassified_cx:
            try:
                aspect_type = asp.iterkeys().next()
                if(aspect_type == "visualProperties"
                   or aspect_type == "cyVisualProperties"
                   or aspect_type == "@context"):
                    return_metadata.append(
                        {
                            "consistencyGroup" : consistency_group,
                            "elementCount":len(asp[aspect_type]),
                            "name":aspect_type,
                            "properties":[]
                         }
                    )
            except Exception as e:
                print(e.message)


        #print {'metaData': return_metadata}

        return [{'metaData': return_metadata}]


    def to_cx_stream(self, md_dict=None):
        """Convert this network to a CX stream

        :return: The CX stream representation of this network.
        :rtype: io.BytesIO

        """
        cx = self.to_cx(md_dict)

        if sys.version_info.major == 3:
            return io.BytesIO(json.dumps(cx).encode('utf-8'))
        else:
            return io.BytesIO(json.dumps(cx))

    def write_to(self, filename):
        """Write this network as a CX file to the specified filename.

        :param filename: The name of the file to write to.
        :type filename: str

        """
        with open(filename, 'w') as outfile:
            json.dump(self.to_cx(), outfile, indent=4)

    def upload_to(self, server, username, password):
        """ Upload this network to the specified server to the account specified by username and password.

        :param server: The NDEx server to upload the network to.
        :type server: str
        :param username: The username of the account to store the network.
        :type username: str
        :param password: The password for the account.
        :type password: str
        :return: The UUID of the network on NDEx.
        :rtype: str

        Example:
            ndexGraph.upload_to('http://test.ndexbio.org', 'myusername', 'mypassword')
        """

        ndex = nc.Ndex(server,username,password)
        return ndex.save_new_network(self.to_cx())

    #------------------------------------------
    #       NODES
    #------------------------------------------

    def add_new_node(self, name=None, attr_dict=None, **attr):
        """Add a cx node, possibly with a particular name, to the graph.

        :param name: The name of the node. (Optional).
        :type name: str
        :param attr_dict: Dictionary of node attributes.  Key/value pairs will update existing data associated with the node.
        :type attr_dict: dict
        :param attr: Set or change attributes using key=value.

        """
        if self.max_node_id == None:
            if self.number_of_nodes() > 0:
                self.max_node_id = max(self.nodes())
            else:
                self.max_node_id = 0
        self.max_node_id += 1
        if name:
            attr['name'] = name
        self.add_node(self.max_node_id, attr_dict, **attr)
        return self.max_node_id

    def add_cx_node(self, id, name=None, represents = None, attr_dict=None):

        if (not attr_dict) and (name or represents):
            attr_dict = {}
        if name:
            attr_dict['name'] = name
        if represents:
            attr_dict['represents'] = represents
        self.add_node(id, attr_dict)

    def get_cx_node (self, id):
        return self.node[id]

    def remove_nodes_from(self, nbunch):
        for n in nbunch:
            self.pos.pop(n, None)
            self.function_term_map.pop(n, None)
        super(MultiDiGraph, self).remove_nodes_from(nbunch)

    def remove_node(self, n):
        self.reified_edges.pop(n,None)

        if(self.function_term_map.get(n) is not None):
            self.function_term_map.pop(n, None)

        self.remove_citation_and_support_node_references(n)

        super(MultiDiGraph, self).remove_node(n)

    def remove_citation_and_support_node_references(self, node_id):

        # remove support to edge references
        if self.node_support_map.has_key(node_id):
            # get the supports that reference the edge
            support_ids = self.node_support_map[node_id]
            # remove the edge entry from the edge_support_map

            #=====================================================
            # Check the "supports" reference map. Decrement the
            # reference value and if it reaches 0 remove from map
            #=====================================================
            supports_array = self.node_support_map.get(node_id)
            for supports_array_id in supports_array:
                decrement_this = self.support_reference_map.get(supports_array_id)
                if(decrement_this is not None):
                    decrement_this -= 1
                    self.support_reference_map[supports_array_id] = decrement_this
                    if(decrement_this == 0):
                        self.support_map.pop(supports_array_id)
                        self.support_reference_map.pop(supports_array_id)

            self.node_support_map.pop(node_id, None)



        # remove support to edge references
        if self.node_citation_map.has_key(node_id):
            #=====================================================
            # Check the "citations" reference map. Decrement the
            # reference value and if it reaches 0 remove from map
            #=====================================================
            citations_array = self.node_citation_map.get(node_id)
            for citations_array_id in citations_array:
                decrement_this = self.citation_reference_map.get(citations_array_id)
                if(decrement_this is not None):
                    decrement_this -= 1
                    self.citation_reference_map[citations_array_id] = decrement_this
                    if(decrement_this == 0):
                        self.citation_map.pop(citations_array_id)
                        self.citation_reference_map.pop(citations_array_id)

            self.node_citation_map.pop(node_id, None)

    def remove_orphan_nodes(self):
        #   remove nodes with no edges
        for node_id in self.nodes():
            #node_name = network.get_node_attribute_value_by_id(node_id)
            degree = self.degree([node_id])[node_id]
            #print node_name + " : " + str()
            if degree is 0:
                #print " -- removing " + str(node_name) + " " + str(node_id)
                self.remove_node(node_id)

    def get_node_ids(self, value, query_key='name'):
        """Returns a list of node ids of all nodes in which query_key has the specified value.

            :param value: The value we want.
            :param query_key: The name of the attribute where we should look for the value.
            :return: A list of node ids.
            :rtype: list

        """
        nodes = [n[0] for n in self.nodes_iter(data=True) if query_key in n[1] and n[1][query_key] == value]
        return nodes


    def set_node_attribute(self, id, attribute_key, attribute_value):
        """Set the value of a particular edge attribute.

            :param id: The edge id we wish to set an attribute on.
            :type id: int
            :param attribute_key: The name of the attribute we wish to set.
            :type attribute_key: string
            :param attribute_value: The value we wish to set the attribute to.
            :type attribute_value: any

        """
        self.node[id][attribute_key] = attribute_value

    def get_node_attribute_value_by_id(self, node_id, query_key='name', error=False):
        """Get the value of a particular node attribute based on the id.

        :param node_id: A node id.
        :type node_id: int
        :param query_key: The name of the attribute whose value we desire.
        :type query_key: str
        :return: The attribute value.
        :rtype: any

        """
        if node_id not in self.node:
            raise ValueError("Your ID is not in the network")
        node_attributes = nx.get_node_attributes(self, query_key)
        if error and len(node_attributes) == 0:
            raise ValueError("That node attribute name does not exist ANYWHERE in the network.")
        return self.node[node_id][query_key] if query_key in self.node[node_id] else None

    def get_node_attribute_values_by_id_list(self, id_list, query_key='name'):
        """Returns a list of attribute values that correspond with the attribute key using the nodes in id_list.

            :param id_list: A list of node ids whose attribute values we wish to retrieve.
            :param query_key: The name of the attribute whose corresponding values should be retrieved.
            :return: A list of attribute values.
            :rtype: list

        """
        for id in id_list:
            if id not in self.node:
                raise ValueError("Your ID list has IDs that are not in the network")
        node_attributes = nx.get_node_attributes(self, query_key)
        if len(node_attributes) == 0:
            raise ValueError("That node attribute name does not exist ANYWHERE in the network.")
        return [self.node[id][query_key] if query_key in self.node[id] else None for id in id_list]

    def get_node_names_by_id_list(self, id_list):
        """Given a list of node ids, return a list of node names.

            :param id_list: A list of node ids whose attribute values we wish to retrieve.
            :type id_list: list
            :return: A list of node names.
            :rtype: list

        """
        return self.get_node_attribute_values_by_id_list(id_list)

    def get_node_name_by_id(self, id):
        """Given a node id, return the name of the node.

        :param id: The cx id of the node.
        :type id: int
        :return: The name of the node.
        :rtype: str

        """
        return self.get_node_attribute_value_by_id(id)

    def get_all_node_attribute_keys(self):
        """Get the unique list of all attribute keys used in at least one node in the network.

            :return: A list of attribute keys.
            :rtype: list

        """
        keys = set()
        for _, attributes in self.nodes_iter(data=True):
            for key, value in attributes.iteritems():
                keys.add(key)
        return list(keys)


    #------------------------------------------
    #       Edges
    #------------------------------------------

    def get_edge_ids_by_node_attribute(self, source_node_value, target_node_value, attribute_key='name'):
        """Returns a list of edge ids of all edges where both the source node and target node have the specified values for attribute_key.

                :param source_node_value: The value we want in the source node.
                :param target_node_value: The value we want in the target node.
                :param attribute_key: The name of the attribute where we should look for the value.
                :return: A list of edge ids.
                :rtype: list
            """
        source_node_ids = self.get_node_ids(source_node_value, attribute_key)
        target_node_ids = self.get_node_ids(target_node_value, attribute_key)
        edge_keys = []
        for s in source_node_ids:
            for t in target_node_ids:
                if s in self and t in self[s]:
                    edge_keys += self[s][t].keys()
        return edge_keys

    def add_edge_between(self, source_node_id, target_node_id, interaction='interacts_with', attr_dict=None, **attr):
        """Add an edge between two nodes in this network specified by source_node_id and target_node_id, optionally specifying the type of interaction.

            :param source_node_id: The node id of the source node.
            :type source_node_id: int
            :param target_node_id: The node id of the target node.
            :type target_node_id: int
            :param interaction: The type of interaction specified by the newly added edge.
            :type interaction: str
            :param attr_dict: Dictionary of node attributes.  Key/value pairs will update existing data associated with the node.
            :type attr_dict: dict
            :param attr: Set or change attributes using key=value.
        """
        if source_node_id not in self.node:
            raise ValueError('source_node_id = %d is not in the network' % source_node_id)
        if target_node_id not in self.node:
            raise ValueError('target_node_id = %d is not in the network' % target_node_id)

        if self.max_edge_id == None:
            if self.number_of_edges() > 0:
                self.max_edge_id = max([x[2] for x in self.edges(keys=True)])
            else:
                self.max_edge_id = 0
        self.max_edge_id += 1
        self.add_edge(source_node_id, target_node_id, self.max_edge_id, interaction=interaction, attr_dict=attr_dict, **attr)
        self.edgemap[self.max_edge_id] = (source_node_id, target_node_id)
        return self.max_edge_id

    def get_node_ids_by_edge_id(self, edge_id):
        if edge_id in self.edgemap:
            s, t = self.edgemap[edge_id]
            return s, t
        else:
            raise Exception("edge id " + str(edge_id) + " not found in network")
        
    def remove_edge_by_id(self, edge_id):
        source_id, target_id = self.get_node_ids_by_edge_id(edge_id)

        # remove edge from edge map
        self.edgemap.pop(edge_id, None)
        pop_these_reified_edges = []

        for n,re in self.reified_edges.iteritems():
            if(re["edge"] == edge_id):
                pop_these_reified_edges.append(n)
                # This causes problems when editing the dictionary while iterating over it --> self.reified_edges.pop(n,None)

        for n in pop_these_reified_edges:
            self.reified_edges.pop(n,None)

        #self.edge_citation_map.pop(edge_id, None)
        #self.edge_support_map.pop(edge_id, None)

        # remove citation and support references to edges
        self.remove_citation_and_support_edge_references(edge_id)

        # networkX remove edge
        self.remove_edge(source_id, target_id, edge_id)

    def remove_citation_and_support_edge_references(self, edge_id):
        citation_ids = None
        support_ids = None

        # remove support to edge references
        if self.edge_support_map.has_key(edge_id):
            # get the supports that reference the edge
            support_ids = self.edge_support_map[edge_id]
            # remove the edge entry from the edge_support_map

            #=====================================================
            # Check the "supports" reference map. Decrement the
            # reference value and if it reaches 0 remove from map
            #=====================================================
            supports_array = self.edge_support_map.get(edge_id)
            for supports_array_id in supports_array:
                decrement_this = self.support_reference_map.get(supports_array_id)
                if(decrement_this is not None):
                    decrement_this -= 1
                    self.support_reference_map[supports_array_id] = decrement_this
                    if(decrement_this == 0):
                        self.support_map.pop(supports_array_id)
                        self.support_reference_map.pop(supports_array_id)

            self.edge_support_map.pop(edge_id)



        # remove support to edge references
        if self.edge_citation_map.has_key(edge_id):
            #=====================================================
            # Check the "citations" reference map. Decrement the
            # reference value and if it reaches 0 remove from map
            #=====================================================
            citations_array = self.edge_citation_map.get(edge_id)
            for citations_array_id in citations_array:
                decrement_this = self.citation_reference_map.get(citations_array_id)
                if(decrement_this is not None):
                    decrement_this -= 1
                    self.citation_reference_map[citations_array_id] = decrement_this
                    if(decrement_this == 0):
                        self.citation_map.pop(citations_array_id)
                        self.citation_reference_map.pop(citations_array_id)

            self.edge_citation_map.pop(edge_id)


            '''
            # eliminate the supports that are still referenced by some node or edge
            for map_support_ids in self.edge_support_map.values():
                for map_support_id in map_support_ids:
                    if map_support_id in support_ids:
                        support_ids.remove(map_support_id)
                        if len(support_ids) == 0:
                            # we have proved that all the potentially orphaned
                            # supports are connected to some other edge
                            break

            for map_support_ids in self.node_support_map.values():
                for map_support_id in map_support_ids:
                    if map_support_id in support_ids:
                        support_ids.remove(map_support_id)
                        if len(support_ids) == 0:
                            # we have proved that all the potentially orphaned
                            # supports are connected to some node
                            break

            # the remaining supports are orphaned and may be removed
            for support_id in support_ids:
                self.support_map.pop(support_id)


        # remove citation to edge references
        if edge_id in self.edge_citation_map:
            # get the citations that reference the edge
            citation_ids = self.edge_citation_map[edge_id]
            # remove the edge entry from the edge_citation_map
            self.edge_citation_map.pop(edge_id)

            # eliminate the citations that are still referenced by some node or edge
            for map_citation_ids in self.edge_citation_map.values():
                for map_citation_id in map_citation_ids:
                    if map_citation_id in citation_ids:
                        citation_ids.remove(map_citation_id)
                        if len(citation_ids) == 0:
                            # we have proved that all the potentially orphaned
                            # citations are connected to some other edge
                            break

            for map_citation_ids in self.node_citation_map.values():
                for map_citation_id in map_citation_ids:
                    if map_citation_id in citation_ids:
                        citation_ids.remove(map_citation_id)
                        if len(citation_ids) == 0:
                            # we have proved that all the potentially orphaned
                            # citations are connected to some node
                            break

            # the remaining citations are orphaned and may be removed
            for citation_id in citation_ids:
                self.citation_map.pop(citation_id)
        '''
        # at this point, all supports that referenced a removed citation
        # have already been removed.


    #TODO Check args
    def get_edge_attribute_value_by_id(self, edge_id, attribute_key):
        """Get the value for attribute of the edge specified by edge_id.

            :param edge_id: The id of the edge.
            :param query_key: The name of the attribute whose value should be retrieved.
            :return: The attribute value. If the value is a list, this returns the entire list.
            :rtype: any

        """
        # edge_keys = {key: (s, t) for s, t, key in self.edges_iter(keys=True)}
        # if edge_id not in edge_keys:
        #     raise ValueError("edge ID Your ID is not in the network")
        # s = edge_keys[edge_id][0]
        # t = edge_keys[edge_id][1]
        # edge_attributes = nx.get_edge_attributes(self, query_key)
        # if len(edge_attributes) == 0:
        #     raise ValueError("That node edge name does not exist ANYWHERE in the network.")
        source_id, target_id = self.get_node_ids_by_edge_id(edge_id)
        return self[source_id][target_id][edge_id][attribute_key] if attribute_key in self[source_id][target_id][edge_id] else None

    #TODO Check args
    def set_edge_attribute(self, edge_id, attribute_key, attribute_value):
        """Set the value of a particular edge attribute.

            :param edge_id: The edge id we wish to set an attribute on.
            :type edge_id: int
            :param attribute_key: The name of the attribute we wish to set.
            :type attribute_key: string
            :param attribute_value: The value we wish to set the attribute to.
            :type attribute_value: any

        """
        source_id, target_id = self.get_node_ids_by_edge_id(edge_id)
        self.edge[source_id][target_id][edge_id][attribute_key] = attribute_value

    def get_edge_ids_by_source_target(self, source_id, target_id):
        edge_ids =[]
        out_edges = self.out_edges(keys=True)
        for edge in out_edges:
            if edge[1] == target_id:
                edge_ids.append(edge[2])
        return edge_ids

    def get_edge_attribute_values_by_id_list(self, edge_id_list, attribute_key):
        """Given a list of edge ids and particular attribute key, return a list of corresponding attribute values.'

            :param edge_id_list: A list of edge ids whose attribute values we wish to retrieve
            :param query_key: The name of the attribute whose corresponding values should be retrieved.
            :return: A list of attribute values corresponding to the edge keys input.
            :rtype: list

        """
        for edge_id in edge_id_list:
            if edge_id not in self.edgemap:
                raise ValueError("edge id list error: edge id " + str(edge_id) + " not found in network")
            
        edge_keys = {id: self.edgemap[id] for id in edge_id_list}
        edge_attributes = nx.get_edge_attributes(self, attribute_key)
        if len(edge_attributes) == 0:
            raise ValueError("the attribute name " + str(attribute_key) + " is not used ANYWHERE in the network.")
        
        return [self[v[0]][v[1]][k][attribute_key] if attribute_key in self[v[0]][v[1]][k] else None for k, v in
                edge_keys.iteritems()]

    def get_all_edge_attribute_keys(self):
        """Get the unique list of all attribute keys used in at least one edge in the network.

        :return: A list of edge attribute keys.
        :rtype: list

        """
        keys = set()
        for _, _, attributes in self.edges_iter(data=True):
            for key, value in attributes.iteritems():
                keys.add(key)
        return list(keys)


    #------------------------------------------
    #       Citations
    #------------------------------------------

    def add_citation(self, identifier=None, title=None, description=None, attributes=None):
        # get the next citation id
        if self.max_citation_id == None:
            if len(self.citation_map) > 0:
                self.max_citation_id = max(self.citation_map.keys())
            else:
                self.max_citation_id = 0
        self.max_citation_id += 1

        citation = {}
        if identifier:
            citation["dc:identifier"] = identifier
        if title:
            citation["dc:title"] = title
        if description:
            citation["description"] = description
        if attributes:
            citation["attributes"] = copy.deepcopy(attributes)
        self.citation_map[self.max_citation_id] = citation
        return self.max_citation_id

    def add_node_citation_ref(self, node_id, citation_id):
        if node_id in self.node_citation_map:
            citation_ids = self.node_citation_map[node_id]
            if citation_id not in citation_ids:
                citation_ids.append(citation_id)
        else:
            citation_ids = [citation_id]
            self.node_citation_map[node_id] = citation_ids

    def add_edge_citation_ref(self, edge_id, citation_id):
        if edge_id in self.edge_citation_map:
            citation_ids = self.edge_citation_map[edge_id]
            if citation_id not in citation_ids:
                citation_ids.append(citation_id)
        else:
            citation_ids = [citation_id]
            self.edge_citation_map[edge_id] = citation_ids
            
    #------------------------------------------
    #       Supports
    #------------------------------------------

    def add_support(self, citation=None, text=None, attributes=None):
        # get the next support id
        if self.max_support_id == None:
            if len(self.citation_map) > 0:
                self.max_support_id = max(self.support_map.keys())
            else:
                self.max_support_id = 0
        self.max_support_id += 1

        support = {}
        if citation:
            support["citation"] = citation
        if text:
            support["text"] = text
        if attributes:
            support["attributes"] = copy.deepcopy(attributes)
        self.support_map[self.max_support_id] = support
        return self.max_support_id
        
    def add_node_support_ref(self, node_id, support_id):
        if node_id in self.node_support_map:
            support_ids = self.node_support_map[node_id]
            if support_id not in support_ids:
                support_ids.append(support_id)
        else:
            support_ids = [support_id]
            self.node_support_map[node_id] = support_ids

    def add_edge_support_ref(self, edge_id, support_id):
        if edge_id in self.edge_support_map:
            support_ids = self.edge_support_map[edge_id]
            if support_id not in support_ids:
                support_ids.append(support_id)
        else:
            support_ids = [support_id]
            self.edge_support_map[edge_id] = support_ids

    #------------------------------------------
    #       Provenance
    #------------------------------------------

    def get_provenance(self):
        return self.provenance

    def set_provenance(self, provenance):
        self.provenance = provenance

    def update_provenance(self, event_type, entity_props=None):
        current_provenance = self.provenance
        if current_provenance:
            new_provenance = make_provenance(event_type, provenance=current_provenance, entity_props=entity_props)
        else:
            new_provenance = make_provenance(event_type,entity_props=entity_props)
        self.set_provenance(new_provenance)

    def set_namespaces(self,namespaces):
        self.namespaces = namespaces

    #------------------------------------------
    #       Datatypes
    #------------------------------------------


def make_provenance(event_type, provenance=None, entity_props=None):
    uri = None
    old_entity = None

    if provenance and "entity" in provenance:
        old_entity = provenance["entity"]
        if uri in old_entity:
            uri = old_entity["uri"]

    t = int(round(time() * 1000))

    event = {
        "startedAtTime": t,
        "endedAtTime": t,
        "eventType": event_type
    }

    if old_entity:
        event["inputs"] = [old_entity]

    entity = {"creationEvent": event}

    if uri:
        entity["uri"] = uri

    if entity_props:
        entity["properties"] = entity_props

    new_provenance = {"entity": entity}

    return new_provenance

class FilterSub:
    """A graph compatible with NDEx"""
    def __init__(self, cx=None, subnet_index=0, subnetwork_id=None):
        self.subnetwork_id = None
        self.view_id = None
        self.max_node_id = None
        self.max_edge_id = None
        self.max_citation_id = None
        self.max_support_id = None
        self.pos = {}
        self.unclassified_cx = []
        self.metadata_original = None
        self.status = {'status': [{'error' : '','success' : True}]}
        self.citation_map = {}
        self.node_citation_map = {}
        self.edge_citation_map = {}
        self.support_map = {}
        self.node_support_map = {}
        self.edge_support_map = {}
        self.function_term_map = {}
        self.cx = cx

        # Maps edge ids to node ids. e.g. { edge1: (source_node, target_node), edge2: (source_node, target_node) }
        self.edgemap = {}

        # If there is no CX to process raise exception
        if cx == None:
            raise RuntimeError("Missing CX. Please provide a valid CX")

        found_subnetwork = False
        for aspect in cx:
            if 'subNetworks' in aspect:
                found_subnetwork = True
                sub_nets = aspect.get('subNetworks')

                if(subnetwork_id is not None):
                    self.subnetwork_id = subnetwork_id
                    for s in sub_nets:
                        if(s.get("@id") == subnetwork_id):
                            sub_nets = [s]
                            break
                else:
                    try:
                        subnetwork = sub_nets[subnet_index]
                    except IndexError:
                        raise RuntimeError("Subnetwork at index %d does not exist " % subnet_index)

                    self.subnetwork_id = subnetwork.get('@id')
                    sub_nets = [subnetwork]
                    break

        if(not found_subnetwork):
            for aspect in cx:
                if 'cySubNetworks' in aspect:
                    found_subnetwork = True
                    sub_nets = aspect.get('cySubNetworks')
                    if(subnetwork_id is not None):
                        self.subnetwork_id = subnetwork_id
                        for s in sub_nets:
                            if(s.get("@id") == subnetwork_id):
                                sub_nets = [s]
                                break
                    else:
                        try:
                            subnetwork = sub_nets[subnet_index]
                        except IndexError:
                            raise RuntimeError("Subnetwork at index %d does not exist " % subnet_index)

                        self.subnetwork_id = subnetwork.get('@id')
                        sub_nets = [subnetwork]
                        break

        self.unclassified_cx = []
        for aspect in cx:
            if 'networkAttributes' in aspect:
                the_list = aspect['networkAttributes']
                the_list[:] = [d for d in the_list if d.get('s') == self.subnetwork_id]

            elif 'nodeAttributes' in aspect:
                the_list = aspect['nodeAttributes']
                the_list[:] = [d for d in the_list if d.get('s') == self.subnetwork_id]

            elif 'edgeAttributes' in aspect:
                the_list = aspect['edgeAttributes']
                the_list[:] = [d for d in the_list if d.get('s') == self.subnetwork_id]

            elif 'cyTableColumn' in aspect:
                the_list = aspect['cyTableColumn']
                the_list[:] = [d for d in the_list if d.get('s') == self.subnetwork_id]

            elif 'cyViews' in aspect:
                the_list = aspect['cyViews']
                the_list[:] = [d for d in the_list if d.get('s') == self.subnetwork_id]

            else:
                self.unclassified_cx.append(aspect)

        #print cx

    def get_cx(self):
        return self.cx