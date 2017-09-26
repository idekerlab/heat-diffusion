from six import string_types, integer_types
from sys import version_info
PY3 = version_info > (3,)


def number_verification():
    return [{'numberVerification': [{'longNumber': 281474976710655}]}]


def metadata(metadata_dict=None, max_node_id=0, max_edge_id=0):
    if (metadata_dict is not None):
        metadata_list = [{'name': k, 'idCounter': v, 'consistencyGroup': 2} for k, v in metadata_dict.items()]
        return [{'metaData': metadata_list}]
    else:
        return [
            {'metaData': [{'name': 'nodes', 'idCounter': max_node_id}, {'name': 'edges', 'idCounter': max_edge_id}]}]


def subnetworks(G, subnetwork_id, view_id):
    result = [{'subNetworks': [{'@id': subnetwork_id,
                                'nodes': G.nodes(),
                                'edges': [e[2] for e in G.edges_iter(keys=True)]}]}]
    result += [{'cyViews': [{'s': subnetwork_id, '@id': view_id}]}]
    result += [{"networkRelations": [{"p": subnetwork_id,
                                      "c": view_id,
                                      "r": "view",
                                      "name": "%s view" % G.get_name()
                                      },
                                     {"c": subnetwork_id,
                                      "r": "subnetwork",
                                      "name": G.get_name(),
                                      "p": 10000 # this is a bogus number provided just to enable CyNDEx import
                                      }]
                }]
    return result


def nodes(G):
    return [
        {'nodes': [{'@id': n[0], 'n': n[1]['name'], 'r': n[1]['represents']}]} if 'name' in n[1] and 'represents' in n[
            1] else
        {'nodes': [{'@id': n[0], 'n': n[1]['name']}]} if 'name' in n[1] and 'represents' not in n[1] else
        {'nodes': [{'@id': n[0], 'r': n[1]['represents']}]} if 'name' not in n[1] and 'represents' in n[1] else
        {'nodes': [{'@id': n[0]}]}
        for n in G.nodes_iter(data=True)]


def edges(G):
    return [
        {'edges': [{'i': e[3]['interaction'], 'k': e[3]['keep'], 's': e[0], '@id': e[2], 't': e[1]}]}
        if 'interaction' in e[3] and 'keep' in e[3] else
        {'edges': [{'i': e[3]['interaction'], 's': e[0], '@id': e[2], 't': e[1]}]}
        if 'interaction' in e[3] and 'keep' not in e[3] else
        {'edges': [{'s': e[0], '@id': e[2], 't': e[1]}]}
        for e in G.edges_iter(data=True, keys=True)]


def network_attributes(G, has_single_subnetwork):
    elements = []
    for attribute in G.graph:
        value = G.graph[attribute]
        element = {'n': attribute, 'v': str(value)}
        if not isinstance(value, string_types):
            d = domain(value)
            if d == "unknown":
                if isinstance(value, dict):
                    d = "dict"

            element["d"] = d
        if has_single_subnetwork:
            element["s"] = G.subnetwork_id
        elements.append(element)
    return [{'networkAttributes': elements}]

    # return [{'networkAttributes': [
    #     {'n': k, 'v': G.graph[k]} if isinstance(G.graph[k], string_types) else
    #     {'n': k, 'v': cv(G.graph[k]), 'd': domain(G.graph[k])}
    #     for k in G.graph]}]


def node_attributes(G, has_single_subnetwork):
    elements = []
    try:
        for node_id, attributes in G.nodes_iter(data=True):
            for attribute_name in attributes:
                if attribute_name != "name" and attribute_name != "represents":
                    attribute_value = attributes[attribute_name]
                    element = {'po': node_id, 'n': attribute_name, 'v': str(attribute_value)}

                    if not isinstance(attribute_value, string_types):
                        element['d'] = domain(attribute_value)

                    if has_single_subnetwork:
                        element['s'] = G.subnetwork_id

                    elements.append(element)
        if len(elements) == 0:
            return None
        else:
            return [{"nodeAttributes": elements}]

    except Exception as e:
        print(e.message)


    # return [{'nodeAttributes': [
    #     {'po': n[0], 'n': k, 'v': n[1][k]} if isinstance(n[1][k], string_types) else
    #     {'po': n[0], 'n': k, 'v': cv(n[1][k]), 'd': domain(n[1][k])}
    #     for k in n[1] if k != 'name' and k != 'represents']} for n in G.nodes_iter(data=True)
    #         if ('name' in n[1] and 'represents' in n[1] and len(n[1]) > 2) or
    #         ('name' in n[1] and 'represents' not in n[1] and len(n[1]) > 1) or
    #         ('name' not in n[1] and 'represents' in n[1] and len(n[1]) > 1) or
    #         ('name' not in n[1] and 'represents' not in n[1] and len(n[1]) > 0)]


def edge_attributes(G, has_single_subnetwork):
    elements = []
    for source, target, edge_id, attributes in G.edges_iter(data=True, keys=True):
        for attribute_name in attributes:
            if attribute_name == 'interaction':
                continue
            attribute_value = attributes[attribute_name]
            element = {'po': edge_id, 'n': attribute_name, 'v': str(attribute_value)}

            if not isinstance(attribute_value, string_types):
                element['d'] = domain(attribute_value)

            if has_single_subnetwork:
                element['s'] = G.subnetwork_id

            elements.append(element)

    if len(elements) == 0:
        return None
    else:
        return [{"edgeAttributes": elements}]

    # return [{'edgeAttributes': [
    #     {'po': e[2], 'n': k, 'v': e[3][k]} if isinstance(e[3][k], string_types) else
    #     {'po': e[2], 'n': k, 'v': cv(e[3][k]), 'd': domain(e[3][k])}
    #     for k in e[3]]} for e in G.edges_iter(data=True, keys=True) if e[3]]


def cartesian(G, id):
    return [{'cartesianLayout': [
        {'node': n, 'view': id, 'x': float(G.pos[n][0]), 'y': float(G.pos[n][1])}
        for n in G.pos
        ]}]


def citations(G):
    citations = []
    for citation_id in G.citation_map:
        citation = G.citation_map[citation_id]
        citation["@id"] = citation_id
        citations.append(citation)
    return [{"citations": citations}]


def node_citations(G):
    node_citations = []
    for node_id in G.node_citation_map:
        citations = G.node_citation_map[node_id]
        node_citations.append({"citations": citations, "po": [node_id]})
    return [{"nodeCitations": node_citations}]


def edge_citations(G):
    edge_citations = []
    for edge_id in G.edge_citation_map:
        citations = G.edge_citation_map[edge_id]
        edge_citations.append({"citations": citations, "po": [edge_id]})
    return [{"edgeCitations": edge_citations}]


def supports(G):
    supports = []
    for support_id in G.support_map:
        support = G.support_map[support_id]
        support["@id"] = support_id
        supports.append(support)
    return [{"supports": supports}]


def node_supports(G):
    node_supports = []
    for node_id in G.node_support_map:
        supports = G.node_support_map[node_id]
        node_supports.append({"supports": supports, "po": [node_id]})
    return [{"nodeSupports": node_supports}]


def edge_supports(G):
    edge_supports = []
    for edge_id in G.edge_support_map:
        supports = G.edge_support_map[edge_id]
        edge_supports.append({"supports": supports, "po": [edge_id]})
    return [{"edgeSupports": edge_supports}]

def function_terms(G):
    function_terms = []
    for po in G.function_term_map:
        function_terms.append(G.function_term_map[po])
    return [{"functionTerms": function_terms}]

def reified_edges(G):
    reified_edges = []
    for n,re in G.reified_edges.iteritems():
        reified_edges.append(re)
    return [{"reifiedEdges": reified_edges}]

def provenance(G):
    if G.get_provenance():
        return [{"provenanceHistory": [G.get_provenance()]}]
    else:
        return []

def namespaces(G):
    if G.namespaces:
        return [{'@context': [G.namespaces]}]
    else :
        return []

# cv stands for convert value. This converts a type to a string representation for CX purposes.
def cv(val):
    return val


def domain(val):
    if type(val) is list:
        if isinstance(val[0], string_types):
            return 'list_of_string'
        elif type(val[0]) is bool:
            return 'list_of_boolean'
        elif isinstance(val[0], integer_types):
            if PY3:
                return 'list_of_integer'
            else:
                if type(val[0]) is int:
                    return 'list_of_integer'
                else:
                    return 'list_of_long'
        elif type(val[0]) is float:
            return 'list_of_double'
        else:
            return 'list_of_unknown'

    if isinstance(val, string_types):
        return 'string'
    elif type(val) is bool:
        return 'boolean'
    elif type(val) is int:
        return 'integer'
    elif isinstance(val, integer_types):
        if PY3:
                return 'integer'
        else:
            if type(val) is int:
                return 'integer'
            else:
                return 'long'
    elif type(val) is float:
        return 'double'
    else:
        return 'unknown'
