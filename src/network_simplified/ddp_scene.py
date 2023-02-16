from manim import *

from .prepare_scene import prepare_scene


class DDPScene(Scene):

    def construct(self):
        num_workers = 4
        networks, comm, title = prepare_scene(
            title="Distributed Data Parallel",
            num_workers=num_workers
        )
        self.add(networks, comm, title)

        