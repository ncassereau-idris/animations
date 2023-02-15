from manim import *

from .worker import Worker
from ..tools.frame import Frame

class MPIAllGatherScene(Scene):

    def construct(self):
        num_workers = 4
        cols = 8
        scale = 0.35

        workers = VGroup(*[
            Worker(
                rank=i,
                rows=1,
                cols=cols,
                max_rows=num_workers,
                max_cols=cols,
                colors=[TEAL, GREEN, YELLOW, BLUE, RED, LIGHT_BROWN, WHITE, LIGHT_PINK]
            ).scale(scale)
            for i in range(num_workers)
        ]).arrange(RIGHT, buff=LARGE_BUFF)
        
        comm = Frame(
            title="Communicator",
            grid_rows=num_workers,
            grid_cols=cols,
            grid_block_size=0.5,
            grid_block_buffer=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER
        ).scale(0.75)
        VGroup(workers, comm).arrange(DOWN, buff=LARGE_BUFF)
        
        mpi_ops_title = Text("MPI_Allgather").scale(0.5).to_edge(UL, buff=SMALL_BUFF)
        comm_data = comm.place_new_content(VGroup(*[
            workers[i].data.copy()
            for i in range(len(workers))
        ]).arrange(DOWN, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * scale))
        self.add(workers, comm, mpi_ops_title)

        anim = [
            LaggedStart(*[
                ReplacementTransform(workers[work_idx].data[i], comm_data[work_idx][i])
                for i in (
                    range(len(workers[work_idx].data))
                    if work_idx >= len(workers) // 2 else
                    range(len(workers[work_idx].data) - 1, -1, -1)
                )
            ], lag_ratio=0.025)
            for work_idx in range(len(workers))
        ]

        self.play(LaggedStart(*anim, lag_ratio=0.5), run_time=5)
        self.wait(1)

        for i, worker in enumerate(workers):
            worker.data = comm_data.copy()
            if i < len(workers) - 1:
                self.play(ReplacementTransform(comm_data.copy(), worker.data))
            else:
                self.play(comm_data.animate.move_to(worker.data))

        self.wait(1)
