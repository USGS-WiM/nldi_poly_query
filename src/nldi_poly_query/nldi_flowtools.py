from .poly_query import Poly_Query


def poly_query(p_list, get_flowlines, downstream_dist):

    results = Poly_Query(p_list, get_flowlines, downstream_dist)
    results = results.serialize()
    return results