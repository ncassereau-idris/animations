from manim import *
import typing
from .connection_animation import LineAnim, NeuronFocusAndRelax

class Network(VGroup):

    def __init__(
        self, arch: typing.List[typing.Optional[int]],
        radius: float = 0.05, standard_duration: float = 0.375,
        **kwargs
    ):
        super().__init__(**kwargs)
        # arch contains ghost layers to artificially stretch the network
        self.arch = [i for i in arch if i is not None]
        self.radius = radius
        self.input_color = GREY
        self.hidden_layer_color = BLUE
        self.highlight_color = YELLOW_E
        self.standard_duration = standard_duration
        self.make(arch)

    def make(self, ghost_arch):
        self.layers = [
            self.make_layer(neurons, i==0)
            if neurons is not None else Dot()
            for i, neurons in enumerate(ghost_arch)
        ]
        VGroup(*self.layers).arrange(RIGHT)

        self.layers = VGroup(*[
            self.layers[i]
            for i in range(len(ghost_arch))
            if ghost_arch[i] is not None
        ])

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

    def length(self, idx): # length between layer idx and idx+1
        if idx < len(self.layers) - 1:
            return Line(
                self.layers[idx].get_center(),
                self.layers[idx+1].get_center()
            ).get_length()
        else:
            return self.length(0) # by convention last relax is as long as first one

    def animation_duration(self, idx):
        return self.standard_duration * self.length(idx) / 2

    def comms_animation(self, idx, length, **kwargs):
        group = [
            LineAnim(
                line,
                color=self.highlight_color,
                run_time=self.standard_duration * length,
                **kwargs
            ) for line in self.comms[idx]
        ]
        return AnimationGroup(*group)

    def focus_relax(self, idx):
        if idx == 0:
            layer = self.layers[0]
            t1, t2 = 0, 0
        else:
            layer = self.layers[idx]
            t1, t2 = idx - 1, idx
        return NeuronFocusAndRelax(
            layer,
            color=self.highlight_color,
            run_time_focus=self.animation_duration(t1),
            run_time_relax=self.animation_duration(t2)
        )

    def forward_animation(self, **kwargs):
        focus, relax = self.focus_relax(0)
        anim = focus
        for i in range(len(self.arch) - 1):
            relaxation = AnimationGroup(
                relax,
                self.comms_animation(i, self.length(i), **kwargs)
            )
            focus, relax = self.focus_relax(i + 1)
            next_focus = LaggedStart(relaxation, focus, lag_ratio=0.4)
            anim = Succession(anim, next_focus)
        return Succession(anim, relax)
