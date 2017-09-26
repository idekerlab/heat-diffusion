
from ndex.networkn import NdexGraph
import sys


def test_types():
    G = NdexGraph()
    n = G.add_new_node('Node with Types')
    n1 = G.add_new_node('A')
    n2 = G.add_new_node('B')
    G.add_edge_between(n, n1)
    G.add_edge_between(n, n2)
    G.set_name('Test Types')

    G.node[n]['string'] = 'mystring'
    G.node[n]['bool'] = True
    G.node[n]['int'] = 5
    G.node[n]['double'] = 2.5

    #  Python3 doesn't support Long (you cannot have a = 5L);
    #  If we need an integer being a long in Python 2 and still be compatible with Python 3,
    #  we need to define up a long variable to be the same as the int class under Python 3,
    #  and it can then be used explicitly to make sure the integer is a long.
    #
    #  it is taken from http: //python3porting.com/noconv.html
    if sys.version_info.major == 3:
        long = int

    # long(5) will be 5L in Python 2 and just int 5 (which is long) in Python 3
    G.node[n]['long'] = long(5)


    G.node[n]['string_list'] = ['mystring','myotherstring']
    G.node[n]['bool_list'] = [False, True]
    G.node[n]['int_list'] = [5, -20]
    G.node[n]['double_list'] = [2.5, 3.7]

    # long(5), long(75) will be 5L, 75L in Python 2 and just int 5, 75 (which is long) in Python 3
    G.node[n]['long_list'] = [long(5), long(75)]

    G.write_to('temp_test_type.cx')

    # G.upload_to('http://test.ndexbio.org', 'scratch', 'scratch')

def test_metadata():
    G = NdexGraph(server="http://dev.ndexbio.org", uuid="317332f7-ade8-11e6-913c-06832d634f41")
    print(G.metadata_original)

if __name__ == "__main__":
    test_types()
    test_metadata()