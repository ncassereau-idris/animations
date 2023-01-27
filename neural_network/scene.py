from manim import *
from . import *


class SCENE(Scene):
    def construct(self):
        net = Network([1, 3, None, 3, 1]).scale(2)
        self.add(net)
        #self.wait(1)
        self.play(net.forward_animation())
        #self.wait(1)
