from manim import *

from .simplified_network import SimplifiedNetwork
from ..tools.frame import Frame

def prepare_scene(
    title: str,
    num_workers: int = 4,
    scale: float = 1,
    zero_optimizer: bool = False
):
    scene_max_width = config.frame_width - 2 * MED_LARGE_BUFF

    networks = VGroup(*[
        SimplifiedNetwork(
            rank=i,
            num_layers=num_workers,
            optimizer_indices=[i+1] if zero_optimizer else None
        ).scale(scale)
        for i in range(num_workers)
    ]).arrange(RIGHT, buff=MED_LARGE_BUFF)

    if networks.get_width() > scene_max_width:
        networks.scale_to_fit_width(scene_max_width)

    comm = Frame(
        title="Communicator",
        grid_rows=num_workers,
        grid_cols=10,
        grid_block_size=0.5,
        grid_block_buffer=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER
    ).scale(2 * scale)
    VGroup(networks, comm).arrange(DOWN, buff=LARGE_BUFF)

    title = Text(title).scale(0.5).to_edge(UL, buff=SMALL_BUFF)

    layer = networks[0].layers[0]
    legend_rows = [
        (layer.parameters, Text("Parameters")),
        (layer.activations, Text("Activations")),
        (layer.gradients, Text("Gradients")),
        (layer.optimizer, Text("Optimizer states"))
    ]
    
    text_scale = Text("a").get_height()
    legend = (
        VGroup(*[
            VGroup(
                square.copy().scale_to_fit_height(text_scale),
                text
            ).arrange(RIGHT)
            for square, text in legend_rows
        ])
        .arrange(DOWN, aligned_edge=LEFT)
        .scale_to_fit_height(config.frame_height / 10)
        .to_edge(DR, buff=SMALL_BUFF)
    )

    return networks, comm, title, legend
