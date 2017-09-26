from enum import Enum

class PathScoring():
    def __init__(self):
        self.mystr = ""

    def cross_country_scoring(self, A, B):
        A_scores = self.cx_edges_to_tuples(A, "A")
        B_scores = self.cx_edges_to_tuples(B, "B")

        average_finish = self.calculate_average_position(A_scores, B_scores)

        a_team_totals = 0.0
        b_team_totals = 0.0

        #=================================
        # DETERMINE TEAM TOTALS
        #=================================
        for k in average_finish.keys():
            for s in average_finish[k]:
                if s[:1] == "A":
                    a_team_totals += k
                else:
                    b_team_totals += k

        #print a_team_totals
        #print b_team_totals

        if a_team_totals > b_team_totals:
            return 1
        elif a_team_totals < b_team_totals:
            return -1
        else:
            return 0

    def calculate_average_position(self, A_scores, B_scores):
        '''

        Calculates the finish positions based on edge types

        :param A: Alternating nodes and edges i.e. [N1, E1, N2, E2, N3]
        :type A: Array
        :param B: Alternating nodes and edges i.e. [N1, E1, N2, E2, N3]
        :type B: Array
        :return: Finish positions
        :rtype: dict
        '''
        scores = A_scores + B_scores

        sorted_scores = sorted(scores, lambda x,y: 1 if x[1] > y[1] else -1 if x[1] < y[1] else 0)

        res = {}
        prev = None
        for i,(k,v) in enumerate(sorted_scores):
            if v!=prev:  # NEXT PLACE
                place,prev = i+1,v
            res[k] = place

        simple_finish_results = {}
        for k in res.keys():
            if simple_finish_results.get(res[k]) is None:
                simple_finish_results[res[k]] = [k]
            else:
                simple_finish_results[res[k]].append(k)

        average_finish = {}
        #==============================================
        # COMPUTE THE AVERAGE FINISH POSITION FOR TIES
        #==============================================
        for k in simple_finish_results.keys():
            position_average = float(sum(range(k, k + len(simple_finish_results[k])))) / float(len(simple_finish_results[k]))
            average_finish[position_average] = simple_finish_results[k]

        return average_finish

    def cx_edges_to_tuples(self, p, prefix):
        '''

        Converts edge types to integer value.  Edge types are ranked by the EdgeRanking class
        :param p:
        :type p:
        :param prefix:
        :type prefix:
        :return:
        :rtype:
        '''
        edge_ranking = EdgeRanking()
        path_tuples = []
        for i, multi_edges in enumerate(p):
            if i % 2 != 0:  # Odd elements are edges
                if len(multi_edges) > 0:
                    top_edge = None
                    tmp_multi_edges = None
                    if type(multi_edges) is dict:
                        tmp_multi_edges = self.convert_edge_dict_to_array(multi_edges)
                    else:
                        tmp_multi_edges = multi_edges

                    for edge in tmp_multi_edges:
                        if top_edge is None:
                            top_edge = edge
                        else:
                            if edge_ranking.edge_type_rank[edge.get("interaction")] < edge_ranking.edge_type_rank[top_edge.get("interaction")]:
                                top_edge = edge

                    path_tuples.append((prefix + str(i), edge_ranking.edge_type_rank[top_edge.get("interaction")]))

        return path_tuples

    #==============================================
    # helper function to convert the raw edge dict
    # to an array which is the format used in
    # path scoring
    #==============================================
    def convert_edge_dict_to_array(self, edge):
        tmp_edge_list = []
        for e in edge.keys():

            tmp_edge_list.append(edge[e])

        return tmp_edge_list



class EdgeRanking:
    def __init__(self):
        self.edge_types = []

        self.edge_class_rank = {
            EdgeEnum.specific_protein_protein: [  # 1
                "controls-transport-of",
                "controls-phosphorylation-of",
                "Phosphorylation",
                "Dephosphorylation",
                "controls-transport-of-chemical",
                "consumption-controled-by",
                "controls-production-of",
                "Ubiquitination",
                "Deubiquitination",
                "ActivityActivity"
            ],
            EdgeEnum.unspecified_activation_inhibition: [  # 2
                "Activation",
                "Inhibition"
            ],
            EdgeEnum.unspecified_state_control: [  # 3
                "controls-state-change-of",
                "chemical-affects"
            ],
            EdgeEnum.unspecified_direct: [  # 4
                "reacts-with",
                "used-to-produce"
            ],
            EdgeEnum.transcriptional_control: [  # 5
                "controls-expression-of",
                "Acetylation",
                "Deacetylation",
                "Sumoylation",
                "Ribosylation",
                "Deribosylation"
            ],
            EdgeEnum.proteins_catalysis_lsmr: [  # 6
                "catalysis-precedes"
            ],
            EdgeEnum.specific_protein_protein_undirected: [  # 7
                "in-complex-with",
                "Complex"
            ],
            EdgeEnum.non_specific_protein_protein_undirected: [  # 8
                "interacts-with"
            ],
            EdgeEnum.unspecified_topological:[  # 9
                "neighbor-of"
            ]
        }

        #===============================================
        # Generates a dict based on edge_class_rank
        # with edge types as key and rank int as value
        #===============================================
        self.edge_type_rank = {}

        for key in self.edge_class_rank.keys():
            for et in self.edge_class_rank[key]:
                self.edge_type_rank[et] = key.value

    def build_edge_type_list(self, edge_class_type_array):
        for ect in edge_class_type_array:
            if(type(ect) is EdgeEnum):
                for et in self.edge_class_rank[ect]:
                    if(et not in self.edge_types):
                        self.edge_types.append(et)

    def print_edge_types(self):
        for et in self.edge_types:
            print et

#==================================
# Enum Classes
#==================================
class EdgeEnum(Enum):
    specific_protein_protein = 1
    unspecified_activation_inhibition = 2
    unspecified_state_control = 3
    unspecified_direct = 4
    transcriptional_control = 5
    proteins_catalysis_lsmr = 6  # linked small molecule reactions
    specific_protein_protein_undirected = 7
    non_specific_protein_protein_undirected = 8
    unspecified_topological = 9

    def edge_count(self):
        return 9
