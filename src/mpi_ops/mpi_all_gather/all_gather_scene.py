from manim import *

from ..components.worker import Worker
from ..components.communicator import Communicator

config.frame_width = 32

class MPIAllGatherScene(MovingCameraScene):

    def construct(self):
        num_workers = 4
        width = Worker(num_blocks=8).get_width()

        workers = VGroup(*[
            Worker(rank=i, num_blocks=2, frame_width=width).scale(0.75)
            for i in range(num_workers)
        ]).arrange(RIGHT, buff=3)
        comm = Communicator(
            height=config.frame_height * 2/ 3,
            width=config.frame_width * 2 / 3
        )
        VGroup(workers, comm).arrange(DOWN, buff=3 * LARGE_BUFF)
        self.add(workers, comm)
        self.camera.frame.save_state()
        self.camera.frame.move_to(workers[0].get_center()).set(
            width=workers[0].get_width() + LARGE_BUFF
        )
        self.wait(3)
        self.play(Restore(self.camera.frame), run_time=5)
        self.wait(2)
