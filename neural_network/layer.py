from manim import *
from .legend import Legend

class MemorySquare(Square):

    def __init__(self, fill_opacity, **kwargs):
        super().__init__(fill_opacity=fill_opacity, **kwargs)
        self.base_fill_opacity = fill_opacity

    def hide(self):
        self.set_opacity(0)
        return self

    def reveal(self):
        self.set_fill(opacity=self.base_fill_opacity)
        self.set_stroke(opacity=1)
        return self


class Layer(VMobject):

    def __init__(
        self, neurons: int, is_input: bool = False,
        input_color=GRAY, hidden_color=YELLOW_E, radius: float = 0.05,
        highlight_color=ORANGE, submobjects_size: float = 0.025,
        square_layer: bool = False, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.neurons = neurons
        self.is_input = is_input
        self.color = input_color if is_input else hidden_color
        self.highlight_color = highlight_color
        self.submobjects_size = submobjects_size
        self.dots = VGroup(*[
            Dot(color=self.color, radius=radius, z_index=1000)
            if not square_layer else
            Square(
                stroke_color=self.color, side_length=radius,
                z_index=1000, fill_opacity=1, fill_color=BLUE_B if not is_input else GREY_B
            ) for _ in range(neurons)
        ])
        self.dots.arrange(.5 * UP)
        self.make_memory_objects()
        self.add(self.dots)
        self.add(self.activations, self.gradients, self.optimizer)
        self.hide(self.activations, self.gradients)
        self.maybe_hide_all()

    def hide(self, *args):
        for object_ in args:
            object_.hide()

    def maybe_hide_all(self):
        if self.is_input:
            self.hide(self.activations, self.gradients, self.optimizer)

    def make_square(self, color):
        return MemorySquare(
            color=color,
            side_length=self.submobjects_size,
            fill_opacity=0.5,
            stroke_width=3.5
        )

    def make_memory_objects(self):
        bottom = self.dots.get_bottom()
        y_shift = 0.2 * DOWN
        x_shift = 0.05 * RIGHT
        self.activations = self.make_square(RED).next_to(bottom, y_shift).shift(-x_shift)
        self.gradients = self.make_square(ORANGE).next_to(bottom, y_shift)
        self.optimizer = self.make_square(GREEN).next_to(bottom, y_shift).shift(x_shift)

    def focus_and_relax(self, run_time_focus, run_time_relax):
        focus, relax = NeuronFocusAndRelax(
            self,
            color=self.highlight_color,
            run_time_focus=run_time_focus,
            run_time_relax=run_time_relax,
            rate_func=linear
        )
        return focus, relax

    def add_legend(self, legend: Legend):
        legend.append(self.activations.copy().reveal(), "Activations")
        legend.append(self.gradients.copy().reveal(), "Gradients")
        legend.append(self.optimizer.copy().reveal(), "Optimizer states")


def NeuronFocusAndRelax(
    mobject: Layer, color=ORANGE,
    run_time_focus: int = 0.5, run_time_relax: int = 0.5,
    **kwargs
) -> None:
    dots = mobject.dots
    dots.save_state()
    focus = dots.animate(run_time=run_time_focus, **kwargs).set_color(color=color)
    relax = Restore(dots, run_time=run_time_relax)
    return (focus, relax)
