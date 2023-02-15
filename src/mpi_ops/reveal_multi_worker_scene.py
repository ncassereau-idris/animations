from manim import *

from ..tools.frame import Frame
from .worker import Worker

class RevealMultiWorkerScene(MovingCameraScene):

    def construct(self):
        num_workers = 4
        cols = 2

        workers = VGroup(*[
            Worker(
                rank=i,
                rows=1,
                cols=cols,
                max_rows=1,
                max_cols=cols * num_workers,
            ).scale(0.35)
            for i in range(num_workers)
        ]).arrange(RIGHT, buff=LARGE_BUFF)

        comm = Frame(
            title="Communicator",
            grid_rows=num_workers,
            grid_cols=cols,
            grid_block_size=0.5,
            grid_block_buffer=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
            horizontal_padding=3*LARGE_BUFF
        )
        VGroup(workers, comm).arrange(DOWN, buff=LARGE_BUFF)
        self.add(workers, comm)
        self.camera.frame.save_state()
        self.camera.frame.move_to(workers[0].get_center()).set(
            width=workers[0].get_width() + LARGE_BUFF
        )
        self.wait(3)
        self.play(Restore(self.camera.frame), run_time=5)

        self.wait(10)
