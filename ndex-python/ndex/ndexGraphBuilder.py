import networkn


class ndexGraphBuilder:
    def __init__(self):
        self.ndexGraph = networkn.NdexGraph()
        self.nodeIdCounter = 0
        self.sidTable = {}  # external id to nodeIt mapping table
        self.edgeIdCounter = 0

    def addNamespaces(self, namespaces):
        self.ndexGraph.set_namespace(namespaces)

    def addNode(self,ext_id, name= None, represents=None, attributes=None ):
        """Add a cx node, possibly with a particular name, to the graph.

        :param ext_id: external id for this node
        :type ext_id str
        :param name: The name of the node. (Optional).
        :type name: str
        :param attr_dict: Dictionary of node attributes.  Key/value pairs will update existing data associated with the node.
        :type attr_dict: dict
        :param attr: Set or change attributes using key=value.

        """
        nodeId = self.sidTable.get(ext_id)
        if  not nodeId :
            nodeId = self.nodeIdCounter
            self.nodeIdCounter +=1
            self.sidTable[ext_id]=nodeId
            self.ndexGraph.add_cx_node(nodeId, name,represents, attributes)
        else : # need to check if all node
             n = self.ndexGraph.node[nodeId]
             if name :
                 if n['name'] != name:
                     raise RuntimeError("Node name mismatches between '"+ name + "' and '" + n['name'] +
                                                                                 "' in node '" + ext_id + "'")
             if represents:
                 if n['represents'] != represents:
                     raise RuntimeError("Node represents mismatches between '"+ represents + "' and '" + n['represents'] +

                                                                                 "' in node '" + ext_id + "'")
             if attributes:
                 for key, value in attributes.iteritems():
                     if n.get(key) and n.get(key) != value:
                         raise RuntimeError("Node attribute " + key + " mismatches between '" +
                                            n.get(key) + "' and '" + value + "'")


        return nodeId

    def addEdge(self, src_id, tgt_id, interaction=None, attributes=None):
        id = self.edgeIdCounter
        if interaction:
            self.ndexGraph.add_edge(src_id, tgt_id, key=id, attr_dict= attributes,interaction=interaction)
        else:
            self.ndexGraph.add_edge(src_id, tgt_id, key=id, attr_dict = attributes)

        self.edgeIdCounter +=1
        return id




    def getNdexGraph(self):
        return self.ndexGraph
