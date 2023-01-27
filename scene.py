from manim import *
from neural_network import *


class CURVE(Scene):
    def construct(self):
        net = Network([1, 2, 1]).shift(RIGHT)#.scale(2)
        self.add(net)
        self.wait(1)
        self.play(net.forward_animation())
        self.wait(1)
