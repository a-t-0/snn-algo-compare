"""Returns the results for the MDSA algorithm. The results are composed of a
list of nodes that is generated by the Alipour algorithm on the original input
graph, a list of nodes that are selected for the following graphs:
snn_algo_graph adapted_snn_graph rad_snn_algo_graph rad_adapted_snn_graph.

, and a boolean per graph to indicate whether the graphs as computed by Alipour
and the SNN match.

These results are returned in the form of a dict.
"""
from pprint import pprint
from typing import List

import networkx as nx

from src.process_results.get_alipour_nodes import get_alipour_nodes


def get_mdsa_snn_results(m_val: int, stage_2_graphs: dict) -> dict:
    """Returns the nodes and counts per node that were computed by the SNN
    algorithm."""
    results = {}

    # Get Alipour count.
    # Compute the count for each node according to Alipour et al.'s algorithm.
    alipour_counter_marks = get_alipour_nodes(
        stage_2_graphs["input_graph"],
        m_val,
        stage_2_graphs["input_graph"].graph["alg_props"],
    )

    # Compute SNN results
    for graph_name, graph in stage_2_graphs.items():
        if isinstance(graph, List):
            latest_snn_graph = graph[-1]
        print(f"graph_name={graph_name}")
        if graph_name == "snn_algo_graph":
            results["snn_algo_result"] = get_snn_results(
                alipour_counter_marks,
                stage_2_graphs["input_graph"],
                m_val,
                redundant=False,
                snn_graph=latest_snn_graph,
            )
        elif graph_name == "adapted_snn_graph":
            results["adapted_snn_algo_result"] = get_snn_results(
                alipour_counter_marks,
                stage_2_graphs["input_graph"],
                m_val,
                redundant=True,
                snn_graph=latest_snn_graph,
            )
        elif graph_name == "rad_snn_algo_graph":
            results["rad_snn_algo_graph"] = get_snn_results(
                alipour_counter_marks,
                stage_2_graphs["input_graph"],
                m_val,
                redundant=False,
                snn_graph=latest_snn_graph,
            )
        elif graph_name == "rad_adapted_snn_graph":
            results["rad_adapted_snn_graph"] = get_snn_results(
                alipour_counter_marks,
                stage_2_graphs["input_graph"],
                m_val,
                redundant=True,
                snn_graph=latest_snn_graph,
            )
    pprint(results)
    return results


def get_snn_results(
    alipour_counter_marks, input_graph, m_val, redundant, snn_graph
):
    """Returns the marks per node that are selected by the snn simulation.

    If the simulation is ran with adaptation in the form of redundancy,
    the code automatically selects the working node, and returns its
    count in the list.
    """

    snn_counter_marks = {}
    if not redundant:
        snn_counter_marks = get_nx_LIF_count_without_redundancy(
            input_graph, snn_graph, m_val
        )
    else:
        snn_counter_marks = get_nx_LIF_count_with_redundancy(
            input_graph, snn_graph, m_val
        )

    # Compare the two performances.
    if alipour_counter_marks == snn_counter_marks:
        snn_counter_marks["passed"] = True
    else:
        snn_counter_marks["passed"] = False
    return snn_counter_marks


def get_nx_LIF_count_without_redundancy(
    input_graph: nx.DiGraph, nx_SNN_G: nx.DiGraph, m_val: int
):
    """Creates a dictionary with the node name and the the current as node
    count.

    # TODO: build support for Lava NX neuron.

    :param G: The original graph on which the MDSA algorithm is ran.
    :param nx_SNN_G:
    :param m: The amount of approximation iterations used in the MDSA
    approximation.
    """
    # Initialise the node counts
    node_counts = {}

    # TODO: verify nx simulator is used, throw error otherwise.
    for node_index in range(0, len(input_graph)):
        node_counts[f"counter_{node_index}_{m_val}"] = nx_SNN_G.nodes[
            f"counter_{node_index}_{m_val}"
        ]["nx_LIF"].u.get()
    return node_counts


def get_nx_LIF_count_with_redundancy(
    input_graph: nx.DiGraph, adapted_nx_snn_graph: nx.DiGraph, m_val: int
):
    """Creates a dictionary with the node name and the the current as node
    count.

    # TODO: build support for Lava NX neuron.

    :param G: The original graph on which the MDSA algorithm is ran.
    :param nx_SNN_G:
    :param m: The amount of approximation iterations used in the MDSA
    approximation.
    """
    # Initialise the node counts
    node_counts = {}

    # TODO: verify nx simulator is used, throw error otherwise.
    for node_index in range(0, len(input_graph)):
        # Check if counterneuron died, if yes, read out redundant neuron.
        if counter_neuron_died(
            adapted_nx_snn_graph, f"counter_{node_index}_{m_val}"
        ):
            prefix = "red_"
        else:
            prefix = ""

        node_counts[
            f"counter_{node_index}_{m_val}"
        ] = adapted_nx_snn_graph.nodes[
            f"{prefix}counter_{node_index}_{m_val}"
        ][
            "nx_LIF"
        ].u.get()
    return node_counts


def counter_neuron_died(snn_graph: nx.DiGraph, counter_neuron_name):
    """Returns True if the counter neuron died, and False otherwise. This
    method assumes the chip is able to probe a particular neuron to determine
    if it is affected by radiation or not, after the algorithm is completed.

    Alternatively, a majority voting amongst 3 or more redundant neurons
    may be used to read out the algorithm results.
    """

    # Determine whether the graph has rad_death property:
    if graph_has_dead_neurons(snn_graph):
        return snn_graph.nodes[counter_neuron_name]["rad_death"]
    return False


def graph_has_dead_neurons(snn_graph: nx.DiGraph):
    """Checks whether the "rad_death" key is in any of the nodes of the graph,
    and if it is, verifies it is in all of the nodes."""
    rad_death_found = False
    for nodename in snn_graph.nodes:
        if "rad_death" in snn_graph.nodes[nodename].keys():
            rad_death_found = True

    if rad_death_found:
        for nodename in snn_graph.nodes:
            if "rad_death" not in snn_graph.nodes[nodename].keys():
                raise Exception(
                    "Error, rad_death key not set in all nodes of"
                    + "graph, yet it was set for at least one node in graph:"
                    + f"{snn_graph}"
                )

        return True
    return False
