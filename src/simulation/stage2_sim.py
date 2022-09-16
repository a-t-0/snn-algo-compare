"""Simulates the SNN graphs and returns a deep copy of the graph per
timestep."""

import networkx as nx

from src.helper import (
    add_stage_completion_to_graph,
    get_sim_duration,
    old_graph_to_new_graph_properties,
)
from src.simulation.run_on_networkx import (
    add_nx_neurons_to_networkx_graph,
    run_snn_on_networkx,
)
from src.simulation.verify_graph_is_snn import (
    assert_no_duplicate_edges_exist,
    assert_synaptic_edgeweight_type_is_correct,
    verify_networkx_snn_spec,
)


def sim_graphs(
    stage_1_graphs: dict,
    run_config: dict,
) -> None:
    """Simulates the snn graphs and makes a deep copy for each timestep.

    :param stage_1_graphs: dict:
    :param run_config: dict:
    """
    for graph_name, snn_graph in stage_1_graphs.items():
        if graph_name != "input_graph":

            # TODO: add lava neurons if run config demands lava.
            convert_graph_snn_to_nx_snn(snn_graph)

            stage_1_graphs[graph_name].graph[
                "sim_duration"
            ] = get_sim_duration(snn_graph, run_config)

            # TODO: compute actual inhibition and mval
            run_snn_on_networkx(
                snn_graph, get_sim_duration(snn_graph, run_config)
            )
        print(f"Stage 2, adding:{graph_name}")
        add_stage_completion_to_graph(stage_1_graphs[graph_name], 2)


def convert_graph_snn_to_nx_snn(G: nx.DiGraph):
    """Converts the SNN graph specfification to a networkx SNN that can be ran.

    :param G: nx.DiGraph:
    """
    # Assert each edge has a weight.
    for edge in G.edges:
        assert_synaptic_edgeweight_type_is_correct(G, edge)

    # Assert no duplicate edges exist.
    assert_no_duplicate_edges_exist(G)

    # Store node properties in nx LIF neuron object under nx_LIF key of node.
    # get_graph_behaviour(G, sim_time)
    old_graph_to_new_graph_properties(G)

    # Assert all neuron properties are specified.
    verify_networkx_snn_spec(G, t=0)

    # Generate networkx network.
    add_nx_neurons_to_networkx_graph(G, t=0)

    # TODO: add lava neurons if run config demands lava.
    # Generate lava network.
    # add_lava_neurons_to_networkx_graph(G)

    # Verify the simulations produce identical static
    # neuron properties.
    print("")
    # compare_static_snn_properties(self, G)
