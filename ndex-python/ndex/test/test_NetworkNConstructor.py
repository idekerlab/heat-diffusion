
import unittest
from os import path
import json
import ndex.beta.layouts as layouts
from ndex.networkn import NdexGraph


HERE = path.abspath(path.dirname(__file__))

class NetworkNConstructorTests(unittest.TestCase):

    def test1(self):
        with open(path.join(HERE, 'tiny_corpus.cx'),'r') as cx_file:
            cx = json.load(cx_file)
            G = NdexGraph(cx=cx)
            self.assertEqual(len(G.edgemap),37 )
            self.assertEqual(len(G.node), 37)
            self.assertEqual(G.provenance['entity']['properties'][0]['name'], 'edge count')
            self.assertEqual(G.provenance['entity']['properties'][0]['value'], '37')
            self.assertEqual(len(G.support_map), 15)
            self.assertEqual(len(G.citation_map), 1)
            self.assertEqual(len(G.function_term_map),35)
            self.assertEqual(len(G.node_citation_map),0)
            self.assertEqual(len(G.node_support_map), 0)
            self.assertEqual(len(G.node_citation_map),0)
            self.assertEqual(len(G.reified_edges), 2)
            self.assertEqual(len(G.edge_citation_map),37)
            self.assertEqual(len(G.edge_support_map),37)
            self.assertEqual(len(G.namespaces),39)

    def test2(self):
        with open (path.join(HERE,'filtered.cx'),'r') as cx_file:
            cx=json.load(cx_file)
            g = NdexGraph(cx)
            layouts.apply_directed_flow_layout(g)
            self.assertEqual(g.node[80]['diffusion_input'], 1.0)


if __name__ == '__main__':
    unittest.main()