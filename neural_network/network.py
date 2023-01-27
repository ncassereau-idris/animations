from manim import *
from .connection_animation import LineAnim

class Network(VGroup):
    def __init__(self, arch, radius=0.1, **kwargs):
        super().__init__(**kwargs)
        self.arch = arch
        self.radius = radius
        self.make()

    def make(self):
        self.layers = VGroup(*[
            self.make_layer(neurons) for neurons in self.arch
        ]).arrange(RIGHT)
        self.comms = VGroup(*[
            self.make_comms(i) for i in range(len(self.arch) - 1)
        ])
        self.add(self.layers, self.comms)
        
    def make_layer(self, neurons):
        return VGroup(*[Dot(color=GREY, radius=self.radius) for _ in range(neurons)]).arrange(UP)

    def make_comms(self, layer_idx):
        layer = self.layers[layer_idx]
        layer_next = self.layers[layer_idx + 1]
        comms = VGroup()
        for start in layer:
            for end in layer_next:
                comms.add(Line(start=start.get_center(), end=end.get_center(), color=WHITE))
        return comms

    def comms_animation(self, idx):
        group = [LineAnim(line, rate_func=smooth, run_time=1.) for line in self.comms[idx]]
        return AnimationGroup(*group)
    
    def forward_animation(self):
        L = []
        for i in range(len(self.arch) - 1):
            L.append(Indicate(self.layers[i]))
            L.append(self.comms_animation(i))
        L.append(Indicate(self.layers[-1]))
        return Succession(*L)