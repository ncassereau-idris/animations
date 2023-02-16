from manim import *

from .simplified_network import SimplifiedNetwork
from ..tools.frame import Frame

def prepare_scene(
    title: str,
    num_workers: int = 4,
):
    scene_max_width = config.frame_width - 2 * MED_LARGE_BUFF

    networks = VGroup(*[
        SimplifiedNetwork(rank=i, num_layers=num_workers)
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
    ).scale(0.75)
    VGroup(networks, comm).arrange(DOWN, buff=LARGE_BUFF)

    title = Text(title).scale(0.5).to_edge(UL, buff=SMALL_BUFF)

    return networks, comm, title
