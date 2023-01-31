from manim import *
import typing

from .utils import StartUpdater, fadeInAlphaFactory, DummyFadeOut
from .connections import Connections
from .layer import Layer


class Network(VGroup):

    def __init__(
        self, arch: typing.List[typing.Optional[int]], dashed: bool = True,
        radius: float = 0.05, standard_duration: float = 0.375,
        square_layer: bool = False,
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
        self.square_layer = square_layer
        self.make_network(arch)
        self.make_subobjects()

    def make_network(self, ghost_arch):
        self.layers = [
            Layer(
                neurons,
                is_input=(i == 0),
                input_color=self.input_color,
                hidden_color=self.hidden_layer_color,
                radius=self.radius,
                highlight_color=self.highlight_color,
                square_layer=self.square_layer
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
        self.input = MarkupText(
            text="<i>x</i>"
        )
        self.output = MarkupText(
            text="<i>ŷ</i>"
        )
        self.label = MarkupText(
            text="<i>y</i>"
        )
        self.loss = MarkupText(
            text="<i>ℒ</i>"
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
        self.input.next_to(self.layers[0].dots, LEFT)
        self.output.next_to(self.layers[-1].dots, RIGHT)
        focus, relax = self.focus_relax(0, reverse_sweep=False)
        anim = Succession(
            FadeIn(self.input, shift=0.2 * RIGHT),
            focus,
        )
        for i in range(len(self.arch) - 1):
            relaxation = AnimationGroup(
                relax,
                self.connections[i].forward_animation(self.standard_duration, **kwargs),
                StartUpdater(
                    self.layers[i + 1].activations,
                    fadeInAlphaFactory(self.layers[i + 1].activations, shift=0.2*DOWN, has_fill=True),
                    run_time=0.2
                )
            )
            focus, relax = self.focus_relax(i + 1, reverse_sweep=False)
            next_focus = LaggedStart(relaxation, focus, lag_ratio=0.5)
            anim = Succession(anim, next_focus)
        return Succession(anim, AnimationGroup(
            relax, FadeOut(self.input), FadeIn(self.output, shift=0.2 * RIGHT)
        ))

    def backward_animation(self, **kwargs):
        # Make the loss appear
        self.label.move_to(self.output).align_to(self.output, DOWN).shift(.5*RIGHT)
        self.loss.move_to(self.output)
        loss_anim = Succession(
            FadeIn(self.label, shift=.2*LEFT),
            LaggedStart(
                AnimationGroup(FadeOut(self.output, shift=.2*UP), FadeOut(self.label, shift=.2*UP)),
                FadeIn(self.loss, shift=.2*UP),
                lag_ratio=.4
            )
        )

        # Start backpropagation
        focus, relax = self.focus_relax(-1, reverse_sweep=True)
        back_anim = focus
        for i in range(len(self.arch) - 2, -1, -1):
            relaxation = AnimationGroup(
                relax,
                self.connections[i].backward_animation(self.standard_duration, **kwargs),
                StartUpdater(
                    self.layers[i + 1].gradients,
                    fadeInAlphaFactory(self.layers[i + 1].gradients, shift=0.2*DOWN, has_fill=True),
                    run_time=0.2
                )
            )
            focus, relax = self.focus_relax(i, reverse_sweep=True)
            next_focus = LaggedStart(relaxation, focus, lag_ratio=0.5)
            back_anim = Succession(back_anim, next_focus)
        back_anim = Succession(back_anim, relax)

        return Succession(loss_anim, back_anim, DummyFadeOut(self.loss, shift=.2*UP))
