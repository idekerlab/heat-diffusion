import pandas as pd
import networkx as nx
from ndex.networkn import NdexGraph
import csv



def load(G, filename, source=1, target=2, edge_attributes=None, sep='\t', header=False):
    '''Load NdexGraph from file.

        :param filename: The name of the file to load. Could include an absolute or relative path.
        :param source: The source node column. (An integer; start counting at 1.)
        :param target: The target node column. (An integer; start counting at 1.)
        :param edge_attributes: A list of names for other columns which are edge attributes.
        :param sep: The cell separator, often a tab (\t), but possibly a comma or other character.
        :param header: Whether the first row should be interpreted as column headers.
    '''
    G.clear()
    if edge_attributes != None:
        if not header and not all(type(i) is int for i in edge_attributes):
            raise ValueError(
                "If there is no header, all edge_attributes must be either a list of integers or None.")
    header = 0 if header else None
    df = pd.read_csv(filename, sep=sep, header=header)
    if type(source) is int:
        source = source - 1
        source_index = df.columns.values[source]
    else:
        if header == False:
            raise ValueError("If a string is used for source or target, then there must be a header.")
        source_index = source
    if type(target) is int:
        target = target - 1
        target_index = df.columns.values[target]
    else:
        if header == False:
            raise ValueError("If a string is used for source or target, then there must be a header.")
        target_index = target
    if edge_attributes is None:
        edge_attributes = []
    edge_attributes = [c - 1 if type(c) is int else c for c in edge_attributes]

    nodes = pd.concat([df.ix[:, source_index], df.ix[:, target_index]],
                      ignore_index=True).drop_duplicates().reset_index(drop=True)
    nodes.apply(lambda x: G.add_new_node(name=x))
    # Map node names to ids
    n_id = {data['name']: n for n, data in G.nodes_iter(data=True)}
    edges = df[[source_index, target_index]]
    edges.apply(lambda x: G.add_edge_between(n_id[x[0]], n_id[x[1]]), axis=1)
    e_id = {}
    for s, t, key in G.edges_iter(keys=True):
        if s not in e_id:
            e_id[s] = {}
        e_id[s][t] = key

    for edge_attribute in edge_attributes:
        source_header = df.columns.values[source]
        target_header = df.columns.values[target]
        if type(edge_attribute) is int:
            edge_attribute = edge_attribute - 1
            value_index = df.columns.values[edge_attribute]
        else:
            value_index = edge_attribute
        edge_col = df[[source_index, target_index, value_index]]
        if header is not None:
            name = value_index
        else:
            name = "Column %d" % value_index
        edge_col.apply(
            lambda x: nx.set_edge_attributes(G, name, {
                (n_id[x[source_header]], n_id[x[target_header]], e_id[n_id[x[source_header]]][n_id[x[target_header]]]):
                    x[value_index]}),
            axis=1)


def annotate(G, filename):
    with open(filename, 'rb') as tsvfile:
        dialect = csv.Sniffer().sniff(tsvfile.read(1024))
        tsvfile.seek(0)
        reader = csv.reader(tsvfile, dialect)
        header = reader.next()
        query_key = header[0]
        header = header[1:]
        # Trackes values that have been annotated to ensure that the same value
        # is never annotated twice. If an annotation happens twice, an exception
        # is thrown.
        annotated = {}
        for row in reader:
            query_value = row[0]
            row = row[1:]
            nodes = G.get_node_ids(query_value, query_key)
            for n in nodes:
                if n not in annotated:
                    annotated[n] = {}
                for i in range(len(header)):
                    key = header[i]
                    if key in annotated[n]:
                        # This would not be expected to occur,
                        # but could if the same node were specified twice in the same file.
                        raise ValueError("ERROR: Attempting to annotate the same node attribute twice.")
                    G.node[n][key] = row[i]
                    annotated[n][key] = True


def apply_template(G, template_id, server='http://public.ndexbio.org', username=None, password=None):
    T = NdexGraph(uuid=template_id, server=server, username=username, password=password)
    apply_network_as_template(G, T)


def apply_network_as_template(G, T):
    G.subnetwork_id = T.subnetwork_id
    G.view_id = T.view_id

    vp = []
    for cx in T.unclassified_cx:
        if 'visualProperties' in cx:
            vp.append(cx)
        if 'networkRelations' in cx:
            vp.append(cx)

    G.unclassified_cx = [cx for cx in G.unclassified_cx if
                         'visualProperties' not in cx and 'networkRelations' not in cx]
    G.unclassified_cx = G.unclassified_cx + vp


def _create_edge_tuples(attractor, target):
    return [(a, t) for a in attractor for t in target]


def apply_source_target_layout(G, category_name='st_layout'):
    '''

    :param G: The graph to layout.
    :type G: NdexGraph
    :param category_name: The attribute that specifies the category for the node. Valid categories are
    'Source', 'Target', 'Forward', or 'Reverse'
    :type category_name: str

    '''
    source = G.get_node_ids('Source', category_name)
    target = G.get_node_ids('Target', category_name)
    forward = G.get_node_ids('Forward', category_name)
    reverse = G.get_node_ids('Reverse', category_name)

    print(G.node)
    fa = []
    for i in range(1):
        fa_n = G.add_new_node()
        fa.append(fa_n)
    forward_edge_tuples = _create_edge_tuples(fa, forward)
    G.add_edges_from(forward_edge_tuples)
    # for f in forward:
    #     G.add_edge(fa[0], f)

    ra = []
    for i in range(1):
        ra_n = G.add_new_node()
        ra.append(ra_n)
    reverse_edge_tuples = _create_edge_tuples(ra, reverse)
    G.add_edges_from(reverse_edge_tuples)
    # for r in reverse:
    #     G.add_edge(ra[0], r)

    initial_pos = {}
    source_incr = 1.0 / (len(source) + 1)
    source_y_value = 0
    for i in range(len(source)):
        source_y_value += source_incr
        initial_pos[source[i]] = (0.0, source_y_value)

    target_incr = 1.0 / (len(target) + 1)
    target_y_value = 0
    for i in range(len(target)):
        target_y_value += target_incr
        initial_pos[target[i]] = (1.0, target_y_value)

    initial_pos[fa[0]] = (0.5, 1)
    initial_pos[ra[0]] = (0.5, 0)

    fixed = source + target + fa + ra

    G.pos = nx.spring_layout(G.to_undirected(), pos=initial_pos, fixed=fixed)
    G.remove_nodes_from(fa)
    G.remove_nodes_from(ra)



