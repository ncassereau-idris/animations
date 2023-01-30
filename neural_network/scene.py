from manim import *
from . import *

config["pixel_height"] = 1080
config["pixel_width"] = 1920

class SCENE(Scene):
    def construct(self):
        net = Network([1, 3, None, 3, 1], standard_duration=0.125).scale(6)
        self.add(net)
        self.wait(1)
        self.play(net.forward_animation())
        self.wait(1)
        self.play(net.backward_animation())
