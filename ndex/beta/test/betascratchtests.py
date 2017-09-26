from ndex.networkn import NdexGraph
import ndex.beta.toolbox as toolbox


def test_load():
    G = NdexGraph()
    toolbox.load(G, 'loadexample.txt', edge_attributes=['strength'], header=True)
    print G.node
    print G.edge
    # G.write_to('loadexample.cx')
    # network_id = G.upload_to('http://public.ndexbio.org', 'scratch', 'scratch')
    # print network_id

def test_annotate():
    G = NdexGraph()
    G.add_new_node('A')
    G.add_new_node('B')
    G.add_new_node('C')
    G.add_new_node('D')
    toolbox.annotate(G,'small_annotate.txt')

def test_complex_layout():
    G = NdexGraph()
    s1 = G.add_new_node('S1', st_layout='Source')
    s2 = G.add_new_node('S2', st_layout='Source')
    s3 = G.add_new_node('S3', st_layout='Source')
    t1 = G.add_new_node('T1', st_layout='Target')
    t2 = G.add_new_node('T2', st_layout='Target')
    f1 = G.add_new_node('F1', st_layout='Forward')
    f2 = G.add_new_node('F2', st_layout='Forward')
    f3 = G.add_new_node('F3', st_layout='Forward')
    f4 = G.add_new_node('F4', st_layout='Forward')
    f5 = G.add_new_node('F5', st_layout='Forward')
    r1 = G.add_new_node('R1', st_layout='Reverse')
    r2 = G.add_new_node('R2', st_layout='Reverse')
    r3 = G.add_new_node('R3', st_layout='Reverse')
    b = G.add_new_node('B1', st_layout='Both')


    G.add_edge_between(r3,r2)
    G.add_edge_between(r2,r1)
    G.add_edge_between(r1,s1)
    G.add_edge_between(r3,b)

    G.add_edge_between(s2, f3)
    G.add_edge_between(s3, f1)
    G.add_edge_between(f1, f2)
    G.add_edge_between(f2, t1)
    G.add_edge_between(f1, b)
    G.add_edge_between(f3, f4)
    G.add_edge_between(f4, f5)
    G.add_edge_between(f5, t2)

    G.add_edge_between(b, t1)
    G.add_edge_between(b, s2)
    G.add_edge_between(b, r1)

    G.add_edge_between(t1,r3)

    toolbox.apply_source_target_layout(G)

    template_id = 'd1856d17-4937-11e6-a5c7-06603eb7f303'
    toolbox.apply_template(G, template_id)
    G.set_name('experiment1')
    G.upload_to('http://public.ndexbio.org', 'scratch', 'scratch')

def test_template():
    template_id = 'f35fbfd3-4918-11e6-a5c7-06603eb7f303'

    G = NdexGraph()
    G.add_new_node('1', color='green')
    G.add_new_node('2', color='red')
    G.add_new_node('3', color='green')
    G.add_new_node('4', color='green')
    G.add_new_node('5', color='green')
    G.add_new_node('6', color='red')
    G.add_edge_between(1, 2)
    G.add_edge_between(2, 3)
    G.add_edge_between(3, 4)
    G.add_edge_between(4, 5)
    G.add_edge_between(5, 6)

    toolbox.apply_template(G, template_id)

    G.set_name('template apply')
    G.upload_to('http://public.ndexbio.org', 'scratch', 'scratch')

def test_complex_layout_create():
    G = NdexGraph()
    s = G.add_new_node('Source', type='Source')
    t = G.add_new_node('Target', type='Target')
    f = G.add_new_node('Forward', type='Forward')
    r = G.add_new_node('Reverse', type='Reverse')
    b = G.add_new_node('Both', type='Both')

    G.add_edge_between(s, f)
    G.add_edge_between(f, t)
    G.add_edge_between(t, r)
    G.add_edge_between(r, s)

    G.add_edge_between(s, b)
    G.add_edge_between(b, t)
    G.add_edge_between(t, b)
    G.add_edge_between(b, s)

    G.set_name('layout template')
    G.upload_to('http://public.ndexbio.org', 'scratch', 'scratch')

def test_st_layout_full():
    G = NdexGraph()
    toolbox.load(G, 'st_layout_network2.txt', header=True)
    toolbox.annotate(G, 'st_layout_annotate2.txt')
    toolbox.apply_source_target_layout(G)
    template_id = 'd1856d17-4937-11e6-a5c7-06603eb7f303'
    toolbox.apply_template(G, template_id, 'http://public.ndexbio.org', 'scratch', 'scratch')
    G.set_name('test_st_layout_wtf1')
    # G.write_to('temp.cx')
    G.upload_to('http://dev2.ndexbio.org', 'scratch', 'scratch')

if __name__ == "__main__":
    test_st_layout_full()