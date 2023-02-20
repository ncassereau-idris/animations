from manim import *
import math

from .worker import Worker
from ..tools.frame import Frame
from ..tools.colors import DEFAULT_LONG_COLOR_LIST

def prepare_scene(title: str, num_workers: int = 4, cols: int = 8, scale: float = 0.35):
    scene_max_width = config.frame_width - 2 * MED_LARGE_BUFF

    workers = VGroup(*[
        Worker(
            rank=i,
            rows=1,
            cols=cols,
            max_rows=num_workers,
            max_cols=math.ceil(cols / num_workers) * num_workers,
            colors=DEFAULT_LONG_COLOR_LIST
        ).scale(scale)
        for i in range(num_workers)
    ]).arrange(RIGHT, buff=LARGE_BUFF)
    
    if workers.get_width() > scene_max_width:
        workers.scale_to_fit_width(scene_max_width)

    comm = Frame(
        title="Communicator",
        grid_rows=num_workers,
        grid_cols=cols,
        grid_block_size=0.5,
        grid_block_buffer=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER
    ).scale(2 * scale)
    VGroup(workers, comm).arrange(DOWN, buff=LARGE_BUFF)

    for worker in workers:
        worker.remove(worker.data)

    mpi_ops_title = Text(title).scale(0.5).to_edge(UL, buff=SMALL_BUFF)
    comm.data = VGroup(*[
        workers[i].data.copy()
        for i in range(len(workers))
    ]).arrange(DOWN, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * scale)

    return workers, comm, mpi_ops_title
