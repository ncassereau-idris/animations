from manim import *
import typing
from .connection_animation import LineAnim, NeuronFocusAndRelax


class Layer(VGroup):

    def __init__(
        self, neurons: int, color=GRAY, radius: float = 0.05,
        highlight_color=ORANGE, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.neurons = neurons
        self.color = color
        self.highlight_color = highlight_color
        self.add(*[
            Dot(color=color, radius=radius, z_index=1000)
            for _ in range(neurons)
        ])
        self.arrange(.5 * UP)

    def focus_and_relax(self, run_time_focus, run_time_relax):
        return NeuronFocusAndRelax(
            self,
            color=self.highlight_color,
            run_time_focus=run_time_focus,
            run_time_relax=run_time_relax,
            rate_func=linear
        )


class Connections(VGroup):

    def __init__(
        self, layer1, layer2, color=ORANGE, dashed: bool = True, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.dashed = dashed
        self.layer1 = layer1
        self.layer2 = layer2
        self.color = color
        lines = [
            self.make_line(start, end, dashed=dashed)
            for start in layer1
            for end in layer2
        ]
        self.add(*lines)

    def make_line(self, start: Dot, end: Dot, dashed: bool = False):
        if dashed:
            return DashedLine(
                start=start.get_center(),
                end=end.get_center(),
                color=WHITE,
                z_index=500,
                dash_length=0.025,
                stroke_width=3
            )
        else:
            return Line(
                start=start.get_center(),
                end=end.get_center(),
                color=WHITE,
                z_index=500
            )

    @property
    def length(self):
        return Line(
            self.layer1.get_center(),
            self.layer2.get_center()
        ).get_length()

    def forward_animation(self, duration, **kwargs):
        length = self.length
        group = [
            LineAnim(
                line,
                color=self.color,
                run_time=duration * length,
                **kwargs
            ) for line in self
        ]
        return AnimationGroup(*group)

    def backward_animation(self, duration, **kwargs):
        return self.forward_animation(duration, reverse=True, **kwargs)


class Network(VGroup):

    def __init__(
        self, arch: typing.List[typing.Optional[int]], dashed: bool = True,
        radius: float = 0.05, standard_duration: float = 0.375,
        **kwargs
    ):
        super().__init__(**kwargs)
        # arch contains ghost layers to artificially stretch the network
        self.arch = [i for i in arch if i is not None]
        self.radius = radius
        self.dashed = dashed
        self.input_color = GREY
        self.hidden_layer_color = BLUE
        self.highlight_color = YELLOW_E
        self.standard_duration = standard_duration
        self.make_network(arch)
        self.make_subobjects()

    def make_network(self, ghost_arch):
        self.layers = [
            Layer(
                neurons,
                color=self.input_color if i == 0 else self.hidden_layer_color,
                radius=self.radius,
                highlight_color=self.highlight_color
            )
            if neurons is not None else Dot()
            for i, neurons in enumerate(ghost_arch)
        ]
        VGroup(*self.layers).arrange(RIGHT)

        self.layers = VGroup(*[
            self.layers[i]
            for i in range(len(ghost_arch))
            if ghost_arch[i] is not None
        ])

        self.connections = VGroup(*[
            Connections(
                self.layers[i],
                self.layers[i+1],
                dashed=self.dashed,
                color=self.highlight_color,
            ) for i in range(len(self.arch) - 1)
        ])
        self.add(self.layers, self.connections)

    def make_subobjects(self):
        self.input = Square(
            color=RED, side_length=0.5, fill_opacity=0.5
        )
        self.output = Square(
            color=GREEN, side_length=0.5, fill_opacity=0.5
        )

    def animation_duration(self, idx):
        if idx < len(self.layers) - 1:
            l = self.connections[idx].length
        else:
            l = self.connections[0].length
        return self.standard_duration * l / 2

    def focus_relax(self, idx, reverse_sweep: bool = False):
        if (not reverse_sweep and idx == 0) or (reverse_sweep and idx == -1):
            layer = self.layers[idx]
            t1, t2 = 0, 0
        else:
            layer = self.layers[idx]
            t1, t2 = idx - 1, idx
            if reverse_sweep: # switch focus and relax time
                t1, t2 = t2, t1
        return layer.focus_and_relax(
            self.animation_duration(t1),
            self.animation_duration(t2)
        )

    def forward_animation(self, **kwargs):
        self.input.next_to(self.layers[0], LEFT)
        self.output.next_to(self.layers[-1], RIGHT)
        focus, relax = self.focus_relax(0, reverse_sweep=False)
        anim = Succession(
            FadeIn(self.input, shift=0.2 * RIGHT),
            focus,
        )
        for i in range(len(self.arch) - 1):
            relaxation = AnimationGroup(
                relax,
                self.connections[i].forward_animation(self.standard_duration, **kwargs)
            )
            focus, relax = self.focus_relax(i + 1, reverse_sweep=False)
            next_focus = LaggedStart(relaxation, focus, lag_ratio=0.5)
            anim = Succession(anim, next_focus)
        return Succession(anim, AnimationGroup(
            relax, FadeOut(self.input), FadeIn(self.output, shift=0.2 * RIGHT)
        ))

    def backward_animation(self, **kwargs):
        focus, relax = self.focus_relax(-1, reverse_sweep=True)
        anim = focus
        for i in range(len(self.arch) - 2, -1, -1):
            relaxation = AnimationGroup(
                relax,
                self.connections[i].backward_animation(self.standard_duration, **kwargs)
            )
            focus, relax = self.focus_relax(i, reverse_sweep=True)
            next_focus = LaggedStart(relaxation, focus, lag_ratio=0.5)
            anim = Succession(anim, next_focus)
        return Succession(anim, AnimationGroup(relax, FadeOut(self.output)))
    