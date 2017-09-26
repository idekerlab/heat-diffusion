import networkx as nx
import random
import math
from operator import index

def aliases_to_node_type(aliases):
    for alias in aliases:
        lower = str.lower(alias)
        if lower.startswith("chebi"):
            return "SmallMolecule"
        if lower.startswith("protein") or lower.startswith("uniprot"):
            return "Protein"
    return "Other"

def _create_simple_graph(networkn):
    g = nx.Graph(networkn)
    return g

def _add_degree_edge_weights(g):
    weights = {}
    for edge in g.edges():
        s = edge[0]
        t = edge[1]
        sd = g.degree(s)
        td = g.degree(t)
        d = min(sd, td)
        if d <= 1:
            weight = 2.0
        elif d <= 2:
            weight = 1.0
        elif d <= 3:
            weight = 0.7
        elif d <= 4:
            weight = 0.5
        else:
            weight = 0.1

        # weight = 1/math.log10((sd + td) * 20)
        props = g[s][t]
        props["weight"] = weight
        #print("sd %s  td %s -> weight: %s" % (sd, td, weight))

# networkx layout source code:
# https://github.com/networkx/networkx/blob/master/networkx/drawing/layout.py
#
def add_ndex_spring_layout_with_attractors(g, node_width, attractor_map, iterations=None, use_degree_edge_weights=False):
    fixed = []
    initial_pos = {}
    g_simple = _create_simple_graph(g)
    next_node_id = max(g_simple.nodes()) + 1

    cc = sorted(nx.connected_components(g_simple), key = len, reverse=True)
    if len(cc) > 1:
        print("%s disconnected subgraphs: adding centerpoint attractor with edges to one of the least connected nodes in each subgraph" % len(cc))
        anchor_node_ids = []
        for c in cc:
            cl = list(c)
            min_degree = min(cl)
            min_index = cl.index(min_degree)
            node_id = cl[min_index]
            anchor_node_ids.append(node_id)
        attractor_id = next_node_id
        g_simple.add_node(next_node_id)
        next_node_id = next_node_id + 1
        fixed.append(attractor_id)
        initial_pos[attractor_id] = (0.5, 0.5)
        for node_id in anchor_node_ids:
            g_simple.add_edge(node_id, attractor_id)



    for attractor in attractor_map:
        attractor_id = next_node_id
        g_simple.add_node(next_node_id)
        next_node_id = next_node_id + 1
        fixed.append(attractor_id)
        initial_pos[attractor_id] = attractor["position"]
        for node_id in attractor["node_ids"]:
            g_simple.add_edge(node_id, attractor_id) # , {"weight":2.5})

    if use_degree_edge_weights:
        _add_degree_edge_weights(g_simple)

    scaled_pos = {}
    scale_factor = 4 * node_width * math.sqrt(g.number_of_nodes())

    for node in g_simple.nodes():
        x_pos = random.random() * scale_factor
        y_pos = random.random() * scale_factor
        scaled_pos[node] = (x_pos, y_pos)

    for node_id in initial_pos:
        position = initial_pos[node_id]
        scaled_pos[node_id] = (scale_factor * position[0], scale_factor * position[1])

    if len(fixed) > 0:
        final_positions = nx.spring_layout(g_simple, fixed=fixed, pos=scaled_pos, iterations=iterations)
        for node_id in fixed:
            final_positions.pop(node_id)
    else:
        final_positions = nx.spring_layout(g_simple, pos=scaled_pos, iterations=iterations)

    g.pos = final_positions


def apply_directed_flow_layout(g, directed_edge_types=None, node_width=25, iterations=50, use_degree_edge_weights=True):
    target_only_node_ids = []
    source_only_node_ids = []
    upstream_top_attractor_position = (0.0, 1.0)
    downstream_top_attractor_position = (1.0, 1.0)
    upstream_bottom_attractor_position = (0.0, 0.0)
    downstream_bottom_attractor_position = (1.0, 0.0)
    attractor_map = []
    random.seed()
    if not g.subnetwork_id and not g.view_id:
        g.subnetwork_id = 0,
        g.view_id = 0

    for node_id in g.nodes():
        out_count = 0
        in_count = 0
        aliases = g.get_node_attribute_value_by_id(node_id, "alias")
        type = g.get_node_attribute_value_by_id(node_id, "type")
        if type is None or type == "Other":
            if aliases:
                type = aliases_to_node_type(aliases)
                g.set_node_attribute(node_id, "type", type)
            else:
                g.set_node_attribute(node_id, "type", "Other")

        for edge in g.out_edges([node_id], keys=True):
            edge_id = edge[2]
            interaction = str(g.get_edge_attribute_value_by_id(edge_id, "interaction"))
            directed = g.get_edge_attribute_value_by_id(edge_id, "directed")
            if directed is None and directed_edge_types is not None:
                if interaction in directed_edge_types:
                    g.set_edge_attribute(edge_id, "directed", True)
                    directed = True

            if directed:
                out_count = out_count + 1

        for edge in g.in_edges([node_id], keys=True):
            edge_id = edge[2]
            interaction = str(g.get_edge_attribute_value_by_id(edge_id, "interaction"))
            directed = g.get_edge_attribute_value_by_id(edge_id, "directed")
            if directed is None and directed_edge_types is not None:
                if interaction in directed_edge_types:
                    g.set_edge_attribute(edge_id, "directed", True)
                    directed = True

            if directed:
                in_count = in_count + 1

        if out_count is 0 and in_count > 0:
            target_only_node_ids.append(node_id)

        if in_count is 0 and out_count > 0:
            source_only_node_ids.append(node_id)

    attractor_map.append({"position": downstream_top_attractor_position, "node_ids": target_only_node_ids})
    attractor_map.append({"position": downstream_bottom_attractor_position, "node_ids": target_only_node_ids})

    attractor_map.append({"position": upstream_top_attractor_position, "node_ids": source_only_node_ids})
    attractor_map.append({"position": upstream_bottom_attractor_position, "node_ids": source_only_node_ids})

    add_ndex_spring_layout_with_attractors(g, node_width, attractor_map, iterations=iterations, use_degree_edge_weights=use_degree_edge_weights)


def _create_edge_tuples(attractor, target):
    return [(a,t) for a in attractor for t in target]

default_directed_edge_types = [
    "controls-phosphorlyation-of",
    "controls-transport-of",
    "controls-state-change-of"
]

def _add_attractor(network, attracted_nodes, attractor_name):
    attractor_list =[]
    attractor_list.append(network.add_new_node(name=attractor_name))
    for attractor in attractor_list:
        for node in attracted_nodes:
            network.add_edge(node, attractor, interaction='in-complex-with')

            #network.add_edge_between(node, attractor, interaction='in-complex-with')
    #edge_tuples = _create_edge_tuples(attractor_list, attracted_nodes)
    #network.add_edges_from(edge_tuples, interaction='in-complex-with')
    return attractor_list[0]

def apply_directed_flow_layout_old(G, directed_edge_types=None):
    target_only_nodes = []
    source_only_nodes = []
    initial_pos = {}
    fixed = []
    upstream_attractor = None
    downstream_attractor = None
    random.seed()

    if not G.subnetwork_id and not G.view_id:
        G.subnetwork_id = 0,
        G.view_id = 0

    for node in G.nodes():
        out_count = 0
        in_count = 0
        #x_pos = random.random() * scale
        #y_pos = random.random() * scale
        #initial_pos[node] = (x_pos, y_pos)
        edge_id = None
        for edge in G.out_edges([node], keys=True):
            edge_id = edge[2]
            interaction = G.get_edge_attribute_value_by_id(edge_id, "interaction")
            directed = G.get_edge_attribute_value_by_id(edge_id, "directed")
            if directed or (directed_edge_types is not None and interaction in directed_edge_types):
                out_count = out_count + 1
        for edge in G.in_edges([node], keys=True):
            edge_id = edge[2]
            interaction = G.get_edge_attribute_value_by_id(edge_id, "interaction")
            directed = G.get_edge_attribute_value_by_id(edge_id, "directed")
            if directed or (directed_edge_types is not None and interaction in directed_edge_types):
                in_count = in_count + 1

        if out_count is 0 and in_count > 0:
            target_only_nodes.append(node)

        if in_count is 0 and out_count > 0:
            source_only_nodes.append(node)

    if len(target_only_nodes) > 0:
        #print(target_only_nodes)
        downstream_attractor = _add_attractor(G, target_only_nodes, "downstream")
        initial_pos[downstream_attractor] = (1.0, 0.5)
        fixed.append(downstream_attractor)

    if len(source_only_nodes) > 0:
        #print(source_only_nodes)
        upstream_attractor = _add_attractor(G, source_only_nodes, "upstream")
        initial_pos[upstream_attractor] = (0.0, 0.5)
        fixed.append(upstream_attractor)

    #print(fixed)

    #node_count = len(G)
    #scale = node_count
    #width = 1.0
    #k = node_count / math.sqrt(node_count)

    n_nodes = G.number_of_nodes()
    n_edges = len(G.edgemap)

    #scale = (n_edges / n_nodes) * math.sqrt(n_nodes + n_edges)
    #scale = 2 * math.sqrt(n_nodes + n_edges)
    node_width = 35
    # node_spacing = 4
    scale = node_width /2
    #k = 1 / node_width

    # if all( abs(pos[n][0]) < 2.01 and abs(pos[n][1]) < 2.01 for n in pos):
    #     pos = {id:pos[id]*scale_factor for id in pos }

    print("scale = %s" % (scale))

    iterations = 100
    G_undirected = G.to_undirected()
    initial_pos = nx.circular_layout(G_undirected)
    initial_pos = {id:initial_pos[id]*scale for id in initial_pos }
    G.pos = nx.spring_layout(G_undirected,
                             pos=initial_pos,
                             fixed=fixed,
                             iterations= iterations)

    G.pos = {id:G.pos[id]*scale for id in G.pos }

    for node_id in G.nodes():
        node_name = G.get_node_attribute_value_by_id(node_id)
        if node_name is None:
            node_name = "Unknown " + str(node_id)

        if node_id in G.pos:
            pos = G.pos[node_id]
            # if pos is not None:
            #     print(node_name + " : " + str(pos))
            # else:
            #     print(node_name + "Null Position")

        else:
            print(node_name + "No Position")

    G.remove_nodes_from([downstream_attractor])
    G.remove_nodes_from([upstream_attractor])

    # print(G.pos)

def _create_edge_tuples(attractor, target):
    return [(a, t) for a in attractor for t in target]

def get_node_ids(network, value, query_key):
    node_ids = []
    for node in network.nodes_iter(data=True):
        data = node[1]
        if query_key in data:
            v = data[query_key]
            if v == value:
                node_ids.append(node[0])

    #node_ids = [n[0] for n in network.nodes_iter(data=True) if query_key in n[1] and n[1][query_key] == value]
    return node_ids

def apply_source_target_layout(G, category_name='st_layout'):
    '''

    :param G: The graph to layout.
    :type G: NdexGraph
    :param category_name: The attribute that specifies the category for the node. Valid categories are
    'Source', 'Target', 'Forward', or 'Reverse'
    :type category_name: str

    '''

    source = get_node_ids(G, 'Source', category_name)
    target = get_node_ids(G, 'Target', category_name)
    forward = get_node_ids(G, 'Forward', category_name)
    reverse = get_node_ids(G, 'Reverse', category_name)

    node_width = 35
    n_nodes = G.number_of_nodes()
    scale = 4 * node_width * math.sqrt(n_nodes)
    print("scale = %s" % (scale))


    initial_pos = nx.circular_layout(G)
    initial_pos = {id:initial_pos[id]*scale for id in initial_pos }

    top = scale
    right = scale
    bottom = 0.0
    left = -1.0 * scale
    middle = 0.0

    fa = []
    ra = []

    # if we have both forward and reverse add attractors
    if len(forward) > 0 and len(reverse) > 0:
        for i in range(1):
            fa_n = G.add_new_node()
            fa.append(fa_n)
        forward_edge_tuples = _create_edge_tuples(fa, forward)
        G.add_edges_from(forward_edge_tuples)

        # attractor positions
        initial_pos[fa[0]] = (right/2, top)

        for i in range(1):
            ra_n = G.add_new_node()
            ra.append(ra_n)
        reverse_edge_tuples = _create_edge_tuples(ra, reverse)
        G.add_edges_from(reverse_edge_tuples)

        initial_pos[ra[0]] = (right/2, bottom)
    else:
        ra_n = G.add_new_node()
        #ra_n2 = G.add_new_node()
        ra.append(ra_n)
        #ra.append(ra_n2)
        initial_pos[ra[0]] = (middle, top/2)
        #initial_pos[ra[1]] = (left, top/2)
        reverse_edge_tuples = _create_edge_tuples(ra, G.nodes())
        G.add_edges_from(reverse_edge_tuples, attr_dict={"weight": 4})


    # source positions
    source_incr = top / (len(source) + 1)
    source_y_value = bottom
    for i in range(len(source)):
        source_y_value += source_incr
        source_id = source[i]

        initial_pos[source_id] = (left, source_y_value)

    # target positions
    target_incr = top / (len(target) + 1)
    target_y_value = bottom
    for i in range(len(target)):
        target_y_value += target_incr
        target_id = target[i]
        initial_pos[target_id] = (right, target_y_value)


    fixed = source + target + fa + ra

    iterations = 100

    G_undirected = G.to_undirected()
    G.pos = nx.spring_layout(G_undirected,
                             pos=initial_pos,
                             fixed=fixed,
                             iterations= iterations)

    #G.pos = {id:G.pos[id]*scale for id in G.pos }

    G.remove_nodes_from(fa)
    G.remove_nodes_from(ra)


    print("done")
