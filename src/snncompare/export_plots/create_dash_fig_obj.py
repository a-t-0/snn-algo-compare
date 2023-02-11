"""Generates a graph in dash."""


from typing import List, Tuple

import networkx as nx
import numpy as np
import plotly.graph_objs as go
from typeguard import typechecked

from snncompare.export_plots.Plot_config import Plot_config


# Build image from incoming graph and positioning parameters
# pylint: disable=R0914
@typechecked
def create_svg_with_dash(
    graph: nx.DiGraph, plot_config: Plot_config
) -> go.Figure:
    """Creates an .svg plot of the incoming networkx graph."""
    pixel_width: int = int(plot_config.base_pixel_width * xy_max(G=graph)[0])
    pixel_height: int = int(plot_config.base_pixel_height * xy_max(G=graph)[1])
    recursive_edge_radius = plot_config.recursive_edge_radius

    # Create nodes
    node_trace = go.Scatter(
        x=list(graph.nodes[n]["pos"][0] for n in graph.nodes()),
        y=list(graph.nodes[n]["pos"][1] for n in graph.nodes()),
        text=list(graph.nodes[n]["label"] for n in graph.nodes())
        if plot_config.show_node_labels
        else None,
        mode="markers+text",
        # hoverinfo="none",
        marker=dict(
            size=plot_config.node_size,
            color=list(graph.nodes[n]["colour"] for n in graph.nodes())
            if plot_config.show_node_colours
            else None,
        ),
        textfont={"size": plot_config.neuron_text_size},
    )

    # Create figure
    fig = go.Figure(
        data=[node_trace],
        layout=go.Layout(
            height=pixel_height,  # height of image in pixels.
            width=pixel_width,  # Width of image in pixels.
            annotations=get_annotations(
                G=graph,
                pixel_height=pixel_height,
                pixel_width=pixel_width,
                plot_config=plot_config,
                recursive_edge_radius=plot_config.recursive_edge_radius,
            ),
            xaxis=go.layout.XAxis(
                tickmode="array",
                tickvals=list(graph.graph["x_tics"].keys()),
                ticktext=list(graph.graph["x_tics"].values()),
                tickfont={"size": plot_config.x_tick_size},
                tickangle=-45,
            ),
            yaxis=go.layout.YAxis(
                tickmode="array",
                tickvals=list(graph.graph["y_tics"].keys()),
                ticktext=list(graph.graph["y_tics"].values()),
                tickfont={"size": plot_config.y_tick_size},
                tickangle=0,
            ),
        ),
    )

    add_recursive_edges(
        G=graph,
        fig=fig,
        plot_config=plot_config,
        radius=recursive_edge_radius,
    )
    return fig


@typechecked
def get_annotations(
    G: nx.DiGraph,
    pixel_height: int,
    pixel_width: int,
    plot_config: Plot_config,
    recursive_edge_radius: float,
) -> List[go.layout.Annotation]:
    """Returns the annotations for this graph."""
    annotations: List[go.layout.Annotation] = []
    annotations.extend(get_regular_edge_arrows(G=G, plot_config=plot_config))
    annotations.extend(
        get_regular_and_recursive_edge_labels(
            G=G,
            pixel_height=pixel_height,
            pixel_width=pixel_width,
            plot_config=plot_config,
            radius=recursive_edge_radius,
        )
    )

    return annotations


@typechecked
def xy_max(
    *,
    G: nx.DiGraph,
) -> Tuple[float, float]:
    """Computes the max x- and y-positions found in the nodes."""
    positions: List[Tuple[float, float]] = []
    for node_name in G.nodes():
        positions.append(G.nodes[node_name]["pos"])

    x = max(list(map(lambda a: a[0], positions)))
    y = max(list(map(lambda a: a[1], positions)))
    return x, y


@typechecked
def add_recursive_edges(
    *, G: nx.DiGraph, fig: go.Figure, plot_config: Plot_config, radius: float
) -> None:
    """Adds a circle, representing a recursive edge, above a node.

    The circle line/edge colour is updated along with the node colour.
    """
    for node_name in G.nodes:
        x, y = G.nodes[node_name]["pos"]
        # Add circles
        fig.add_shape(
            type="circle",
            xref="x",
            yref="y",
            x0=x - radius,
            y0=y,
            x1=x + radius,
            y1=y + radius,
            line_color=G.nodes[node_name]["colour"]
            if plot_config.show_edge_colours
            else None,
            opacity=G.nodes[node_name]["opacity"]
            if plot_config.show_edge_opacity
            else None,
            line=go.layout.shape.Line(width=plot_config.edge_width),
        )


# pylint: disable = W0621
@typechecked
def get_regular_edge_arrows(
    *, G: nx.DiGraph, plot_config: Plot_config
) -> List[go.layout.Annotation]:
    """Returns the annotation dictionaries representing the directed edge
    arrows."""
    annotations: List[go.layout.Annotation] = []
    for edge in G.edges:
        left_x, left_y, right_x, right_y = get_edge_xys(G=G, edge=edge)
        print(f'G.edges[edge]["opacity"]={G.edges[edge]["opacity"]}')
        if edge[0] != edge[1]:
            annotations.append(
                go.layout.Annotation(
                    ax=left_x,
                    ay=left_y,
                    axref="x",
                    ayref="y",
                    opacity=G.edges[edge]["opacity"]
                    if plot_config.show_edge_opacity
                    else None,
                    x=right_x,
                    y=right_y,
                    xref="x",
                    yref="y",
                    arrowwidth=plot_config.edge_width,  # Width of arrow.
                    arrowcolor=G.nodes[edge[0]]["colour"]
                    if plot_config.show_edge_colours
                    else None,
                    arrowsize=0.8,  # (1 gives head 3x wider than arrow line)
                    showarrow=True,
                    arrowhead=1,  # the arrowshape (index).
                )
            )
    return annotations


# pylint: disable = W0621
@typechecked
def get_edge_xys(
    *, G: nx.DiGraph, edge: Tuple[str, str]
) -> Tuple[float, float, float, float,]:
    """Returns the left x and y values of an edge, followed by the right x y
    values of an edge."""
    # Get coordinates
    left_node_name = edge[0]
    right_node_name = edge[1]
    left_x = G.nodes[left_node_name]["pos"][0]
    left_y = G.nodes[left_node_name]["pos"][1]
    right_x = G.nodes[right_node_name]["pos"][0]
    right_y = G.nodes[right_node_name]["pos"][1]
    return (
        left_x,
        left_y,
        right_x,
        right_y,
    )


# pylint: disable = W0621
@typechecked
def get_regular_and_recursive_edge_labels(
    *,
    G: nx.DiGraph,
    pixel_height: int,
    pixel_width: int,
    plot_config: Plot_config,
    radius: float,
) -> List[go.layout.Annotation]:
    """Returns the annotation dictionaries representing the labels of the
    directed edge arrows.

    Returns the annotation dictionaries representing the labels of the
    recursive edge circles above the nodes. Note, only place 0.25 radius above
    pos, because recursive edge circles are actually ovals.

    with height: 1 * radius, width:2 * radius, and you want to place the
    recursive edge label in the center of the oval.
    """
    annotations = []
    if plot_config.show_edge_labels:
        for edge in G.edges:
            if edge[0] != edge[1]:  # For non recursive edges
                mid_x, mid_y = get_edge_mid_point(G=G, edge=edge)
                annotations.append(
                    go.layout.Annotation(
                        x=mid_x,
                        y=mid_y,
                        xref="x",
                        yref="y",
                        text=G.edges[edge]["label"],
                        font={"size": plot_config.neuron_text_size},
                        align="center",
                        showarrow=False,
                        yanchor="bottom",
                        textangle=get_stretched_edge_angle(
                            G=G,
                            edge=edge,
                            pixel_height=pixel_height,
                            pixel_width=pixel_width,
                        ),
                    )
                )
            else:  # Recursive edge.
                x, y = G.nodes[edge[0]]["pos"]
                annotations.append(
                    go.layout.Annotation(
                        x=x,
                        y=y + 0.25 * radius,
                        xref="x",
                        yref="y",
                        text=G.edges[edge]["label"],
                        font={"size": plot_config.neuron_text_size},
                        align="center",
                        showarrow=False,
                        yanchor="bottom",
                    )
                )
    return annotations


@typechecked
def get_edge_mid_point(
    edge: Tuple[str, str],
    G: nx.DiGraph,
) -> Tuple[float, float]:
    """Returns the mid point of an edge."""
    left_x, left_y, right_x, right_y = get_edge_xys(G=G, edge=edge)
    mid_x = (right_x + left_x) / 2
    mid_y = (right_y + left_y) / 2
    return mid_x, mid_y


@typechecked
def get_stretched_edge_angle(
    *,
    edge: Tuple[str, str],
    G: nx.DiGraph,
    pixel_height: int,
    pixel_width: int,
) -> float:
    """Returns the ccw+ angle of the edge (w.r.t.

    the horizontal), and adjusts for stretching of the image.
    """
    left_x, left_y, right_x, right_y = get_edge_xys(G=G, edge=edge)

    # Compute dx and change dx to accommodate the stretching of the image.
    dx = (right_x - left_x) * (
        1 - ((pixel_height - pixel_width) / pixel_height)
    )
    dy = right_y - left_y
    angle = np.arctan2(dy, dx)
    return float(-np.rad2deg(angle))


def get_pure_edge_angle(
    G: nx.DiGraph, edge: Tuple[str, str]
) -> Tuple[int, int]:
    """Returns the ccw+ mid point of an edge."""
    left_x, left_y, right_x, right_y = get_edge_xys(G=G, edge=edge)
    dx = right_x - left_x
    dy = right_y - left_y
    angle = np.arctan2(dy, dx)
    # return -np.rad2deg((angle) % (2 * np.pi))
    return -np.rad2deg(angle)