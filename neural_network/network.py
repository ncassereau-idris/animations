from manim import *
from .connection_animation import LineAnim

class Network(VGroup):
    def __init__(self, arch, radius=0.05, **kwargs):
        super().__init__(**kwargs)
        self.arch = arch
        self.radius = radius
        self.input_color = GREY
        self.hidden_layer_color = BLUE
        self.highlight_color = YELLOW_E
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
                comms.add(DashedLine(
                    start=start.get_center(),
                    end=end.get_center(),
                    color=WHITE,
                    z_index=500,
                    dash_length=0.025,
                    stroke_width=3
                ))
        return comms

    def comms_animation(self, idx, **kwargs):
        group = [
            LineAnim(line, color=self.highlight_color, run_time=.5, **kwargs)
            for line in self.comms[idx]
        ]
        return AnimationGroup(*group)
    
    def forward_animation(self, **kwargs):
        L = []

        def indicate(layer, **kwargs):
            return Indicate(
                layer,
                scale_factor=1,
                color=self.highlight_color,
                rate_func=there_and_back_with_pause,
                run_time=0.5,
                **kwargs
            )

        for i in range(len(self.arch) - 1):
            L.append(indicate(self.layers[i]))
            L.append(self.comms_animation(i, **kwargs))
        L.append(indicate(self.layers[-1]))
        return LaggedStart(*L, lag_ratio=0.5)
