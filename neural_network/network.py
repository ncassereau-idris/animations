from manim import *
from .connection_animation import LineAnim

class Network(VGroup):
    def __init__(self, arch, radius=0.1, **kwargs):
        super().__init__(**kwargs)
        self.arch = arch
        self.radius = radius
        self.input_color = GREY
        self.hidden_layer_color = BLUE
        self.make()

    def make(self):
        self.layers = VGroup(*[
            self.make_layer(neurons, i==0) for i, neurons in enumerate(self.arch)
        ]).arrange(RIGHT)
        self.comms = VGroup(*[
            self.make_comms(i) for i in range(len(self.arch) - 1)
        ])
        self.add(self.layers, self.comms)
        
    def make_layer(self, neurons, is_input=False):
        color = self.input_color if is_input else self.hidden_layer_color
        return VGroup(*[
            Dot(color=color, radius=self.radius, z_index=1000)
            for _ in range(neurons)
        ]).arrange(UP)

    def make_comms(self, layer_idx):
        layer = self.layers[layer_idx]
        layer_next = self.layers[layer_idx + 1]
        comms = VGroup()
        for start in layer:
            for end in layer_next:
                comms.add(Line(
                    start=start.get_center(),
                    end=end.get_center(),
                    color=WHITE,
                    z_index=500
                ).set(start_dot=start, end_dot=end))
        return comms

    def comms_animation(self, idx):
        group = [
            LineAnim(line, rate_func=smooth, run_time=1.)
            for line in self.comms[idx]
        ]
        return AnimationGroup(*group)
    
    def forward_animation(self):
        L = []
        for i in range(len(self.arch) - 1):
            L.append(Indicate(self.layers[i]))
            L.append(self.comms_animation(i))
        L.append(Indicate(self.layers[-1]))
        return Succession(*L)