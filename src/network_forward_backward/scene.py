from manim import *
from .neural_network.network import Network
from src.tools.legend import Legend

config.pixel_height = 1080
config.pixel_width = 1920
config.frame_width = 16
config.frame_height = config.frame_width * config.pixel_height / config.pixel_width

class ForwardBackwardScene(Scene):
    def construct(self):
        legend = Legend()
        net = Network([1, 1, 1, 1], standard_duration=0.175, square_layer=True, radius=0.1).scale(6)
        net.add_legend(legend)
        legend.build(location=UR)
        self.add(net, legend)
        self.wait(1)
        self.play(net.forward_animation())
        self.wait(1)
        self.play(net.loss_animation())
        self.wait(1)
        self.play(net.backward_animation())
        self.wait(1)
