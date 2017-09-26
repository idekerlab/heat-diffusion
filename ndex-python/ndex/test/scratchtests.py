from ndex.networkn import NdexGraph, FilterSub
import ndex

from ndex.client import Ndex
import networkx as nx
import os
import json
import inspect
import io

def test_create_from_edge_list():
    G = NdexGraph()
    edge_list = [('A', 'B'), ('B', 'C')]

    G.create_from_edge_list(edge_list, interaction=['A-B', 'B-C'])

    G.set_name('create_from_edge_list')

    network_id = G.upload_to("http://dev.ndexbio.org", "scratch", "scratch")
    print(network_id)

    #ndex = Ndex("http://dev.ndexbio.org", "scratch", "scratch")
    #ndex.make_network_public(network_id)
    #ndex.make_network_private(network_id)

#def test_cartesian():
 #   G = NdexGraph(server="http://test.ndexbio.org",
  #                username='scratch', password='scratch',
   #               uuid='aa6e7426-3f14-11e6-a7fa-028f28cd6a5b')
    #G.write_to('cartesian2.cx')

def test_layout():
    nx_G = nx.complete_graph(11)
    # nx_G.remove_node(0)
    # nx_G.remove_node(1)
    G = NdexGraph()
    G.add_new_node('1')
    G.add_new_node('2')
    G.add_new_node('3')
    G.add_new_node('4')
    G.add_new_node('5')
    G.add_new_node('6')

    G.add_edge_between(1, 3)
    G.add_edge_between(1, 4)
    G.add_edge_between(2, 3)
    G.add_edge_between(2, 4)

    G.add_edge_between(3, 5)
    G.add_edge_between(3, 6)
    G.add_edge_between(4, 5)
    G.add_edge_between(4, 6, interaction='AAABBBCCC') #attr_dict={'interaction':'testing'})

    initial_pos = {
        1: (0.0, 1.0),
        2: (0.0, 0.0),
        # 3: (0.5, 0.5),
        # 4: (0.5, 0.5),
        5: (1.0, 1.0),
        6: (1.0, 0.0),
    }

    fixed = [1,2,5,6]

    # G.add_new_node('3')
    # G.add_new_node('4')
    # G.add_new_node('5')
    G.pos = nx.spring_layout(G.to_undirected(), pos=initial_pos, fixed=fixed)
    print(G.pos)
    G.set_name('spring_layout undirected')
    #G.upload_to('http://dev.ndexbio.org','scratch','scratch')


def test_filter_sub():
    repo_directory = '/Users/aarongary/Development/DataSets/NDEx/server2/data/'
    print inspect.getfile(FilterSub)
    read_this_aspect = os.path.join(repo_directory, 'NCI_Style.cx') #'Diffusion1.cx') #'subnetwork_ex1.cx')

    with open(read_this_aspect, 'rt') as fid:
        data = json.load(fid)
        if(data is not None):
            my_filter_sub = FilterSub(data, subnet_index=0)
            ndexGraph = NdexGraph(my_filter_sub.get_cx())
            print ndexGraph.to_cx()


def scratch_test():
    G = NdexGraph()
    G.add_new_node('1')
    G.add_new_node('2')
    G.add_edge_between(1,2)

    G.set_name('scratch-test1 - jing')
    print(G.graph())
    #G.upload_to('http://dev.ndexbio.org', 'scratch', 'scratch')

def test_data_to_type():
    NdexGraph.data_to_type('true','boolean')

def test_cx_string_building():
    cx_str = '[{"numberVerification": [{"longNumber": 281474976710655}]}, {"metaData": [{"idCounter": 4, "name": "nodes"}, {"idCounter": 4, "name": "edges"}]}, {"networkAttributes": [{"v": "indra_assembled", "n": "name"}, {"v": "", "n": "description"}]}, {"nodeAttributes": [{"v": "proteinfamily", "po": 0, "n": "type"}, {"v": "MEK", "po": 0, "n": "BE"}, {"v": "proteinfamily", "po": 1, "n": "type"}, {"v": "C26360", "po": 1, "n": "NCIT"}, {"v": "ERK", "po": 1, "n": "BE"}]}, {"edgeAttributes": [{"v": "Phosphorylation(MEK(), ERK())", "po": 2, "n": "INDRA statement"}, {"v": "Modification", "po": 2, "n": "type"}, {"v": "positive", "po": 2, "n": "polarity"}, {"v": "1.00", "po": 2, "n": "Belief score"}, {"v": "MEK phosphorylates ERK.", "po": 2, "n": "Text"}]}, {"edges": [{"i": "Phosphorylation", "s": 0, "@id": 2, "t": 1}]}, {"edgeSupports": [{"supports": [3], "po": [2]}]}, {"citations": []}, {"nodes": [{"@id": 0, "n": "MEK"}, {"@id": 1, "n": "ERK"}]}, {"supports": [{"text": "MEK phosphorylates ERK.", "@id": 3}]}, {"edgeCitations": []},{"status": [{"error": "","success": true}]}]'
    stream = io.BytesIO(cx_str)
    nd = ndex.client.Ndex('http://preview.ndexbio.org',
                                 username='scratch',
                                 password='scratch')

    network_id = nd.save_cx_stream_as_new_network(stream)

if __name__ == "__main__":
    test_layout()

