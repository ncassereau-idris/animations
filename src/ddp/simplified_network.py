from manim import *
from manim.utils.color import Colors
from typing import Optional

from ..tools.frame import Frame

class SimplifiedLayer(VMobject):

    def __init__(self, layer_idx: int, optimizer: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.layer_idx = layer_idx

        self.frame = Frame(
            title=f"Layer {self.layer_idx}",
            grid_rows=4,
            grid_cols=1,
            grid_block_size=0.5,
            grid_block_buffer=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
            horizontal_padding=MED_SMALL_BUFF
        )

        self.show_optimizer = optimizer

        self.activations = self.make_square(RED)
        self.gradients = self.make_square(ORANGE)
        self.parameters = self.make_square(BLUE)
        self.optimizer = self.make_square(GREEN)

        self.activations_ghost = self.activations.copy().set_opacity(0)
        self.gradients_ghost = self.gradients.copy().set_opacity(0)
        self.parameters_ghost = self.parameters.copy().set_opacity(0)
        self.optimizer_ghost = self.optimizer.copy().set_opacity(0)
        
        self.frame.data = VGroup(
            self.parameters_ghost,
            self.activations_ghost,
            self.gradients_ghost,
            self.optimizer_ghost
        ).arrange(DOWN)

        self.activations.move_to(self.activations_ghost)
        self.gradients.move_to(self.gradients_ghost)
        self.parameters.move_to(self.parameters_ghost)
        self.optimizer.move_to(self.optimizer_ghost)

        self.add(self.frame, self.frame.data, self.parameters, self.activations, self.gradients)
        if optimizer:
            self.add(self.optimizer)
        self.scale_factor = 1

    def scale(self, scale_factor: float, **kwargs):
        self.scale_factor *= scale_factor
        return super().scale(scale_factor, **kwargs)

    @staticmethod
    def make_square(color: Colors) -> Square:
        return Square(
            side_length=0.5,
            color=color,
            fill_opacity=0.5,
            stroke_width=2
        )


class SimplifiedNetwork(VMobject):

    def __init__(
        self,
        rank: int = 0,
        num_layers: int = 4,
        optimizer_indices: Optional[list[int]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.rank = rank
        self.num_layers = num_layers

        self.layers = VGroup(*[
            SimplifiedLayer(
                i,
                optimizer=optimizer_indices is not None and i in optimizer_indices
            ) for i in range(1, self.num_layers + 1)
        ]).arrange(RIGHT, buff=MED_SMALL_BUFF)

        self.frame = Frame(
            title=f"GPU {self.rank}",
            content_height=self.layers.get_height(),
            content_width=self.layers.get_width()
        )
        self.frame.data = self.layers
        self.add(self.frame, self.frame.data)
