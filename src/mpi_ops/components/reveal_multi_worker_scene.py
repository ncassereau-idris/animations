from manim import *

from .worker import Worker

config.frame_width = 32

class RevealMultiWorkerScene(MovingCameraScene):

    def construct(self):
        num_workers = 4
        workers = VGroup(*[
            Worker(rank=i, num_blocks=8).scale(0.75)
            for i in range(num_workers)
        ]).arrange(RIGHT, buff=3)
        self.add(workers)
        self.camera.frame.save_state()
        self.camera.frame.move_to(workers[0].get_center()).set(
            width=workers[0].get_width() + 2 * LARGE_BUFF
        )
        self.play(Restore(self.camera.frame), run_time=5)
