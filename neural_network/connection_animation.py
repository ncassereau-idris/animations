from manim import *
import typing
import numpy as np


def LineAnim(mobject: Line, *args, **kwargs) -> Animation:
    if isinstance(mobject, DashedLine):
        return DashedLineAnim(mobject, *args, **kwargs)
    elif isinstance(mobject, Line):
        return FullLineAnim(mobject, *args, **kwargs)


class FullLineAnim(Animation):
    
    def __init__(
        self, mobject: Line, color=ORANGE,
        alpha_between: float = 0.3, alpha_eps:float = 1e-6,
        **kwargs
    ) -> None:
        super().__init__(mobject, **kwargs)
        self.start = mobject.get_start()
        self.end = mobject.get_end()
        self.color = color
        self.alpha_between = alpha_between
        self.alpha_eps = alpha_eps
        self.rate_func = smooth
        
    def begin(self) -> None:
        self.mobject.set_opacity(0, family=False)
        self.l1 = Line(self.start, self.end, color=self.mobject.color)
        self.l2 = Line(self.start, self.end, color=self.color)
        self.l3 = Line(self.start, self.end, color=self.mobject.color)
        self.first_group = VGroup(self.l1, self.l2)
        self.last_group = VGroup(self.l2, self.l3)
        self.all_group = VGroup(self.l1, self.l2, self.l3)
        self.all_group.set_opacity(1)
        self.mobject.add(self.all_group)
        super().begin()

    def get_coord(self, alpha: float) -> np.ndarray:
        return alpha * self.end + (1 - alpha) * self.start

    def get_alphas(self, alpha: float) -> typing.Tuple[float]:
        alpha1 = alpha * (1 + self.alpha_between)
        alpha2 = alpha1 - self.alpha_between
        return alpha1, alpha2

    def get_points_pair(self, alpha: float) -> typing.Tuple[np.ndarray]:
        return (
            self.get_coord(alpha - self.alpha_eps),
            self.get_coord(alpha + self.alpha_eps)
        )

    def interpolate_mobject(self, alpha: float) -> None:
        if self.rate_func is not None:
            alpha = self.rate_func(alpha)
        alpha1, alpha2 = self.get_alphas(alpha)
        if alpha2 <= 0:
            point1, point1_eps = self.get_points_pair(alpha1)
            self.l2.put_start_and_end_on(self.start, point1)
            self.l1.put_start_and_end_on(point1_eps, self.end)
            self.first_group.set_opacity(1)
            self.l3.set_opacity(0)
        elif alpha1 >= 1:
            point2, point2_eps = self.get_points_pair(alpha2)
            self.l3.put_start_and_end_on(self.start, point2)
            self.l2.put_start_and_end_on(point2_eps, self.end)
            self.last_group.set_opacity(1)
            self.l1.set_opacity(0)
        else:
            point1, point1_eps = self.get_points_pair(alpha1)
            point2, point2_eps = self.get_points_pair(alpha2)
            self.l3.put_start_and_end_on(self.start, point2)
            self.l2.put_start_and_end_on(point2_eps, point1)
            self.l1.put_start_and_end_on(point1_eps, self.end)
            self.all_group.set_opacity(1.0)

        self.mobject.set_opacity(0, family=False)
        
    def clean_up_from_scene(self, scene: Scene) -> None:
        super().clean_up_from_scene(scene)
        self.all_group.set_opacity(0)
        self.mobject.set_opacity(1., family=False)
        scene.remove(self.all_group)
        scene.add(self.mobject)


class DashedLineAnim(Animation):

    def __init__(self, mobject: DashedLine, color=ORANGE, **kwargs):
        super().__init__(mobject, **kwargs)
        self.color = color
        self.mobject = mobject
        self.base_color = mobject.color
        self.num_dashes = len(mobject.submobjects)
        self.step = 1 / self.num_dashes
        self.rate_func = linear
        self.base_stroke = mobject.stroke_width
        self.stroke = 2 * self.base_stroke

    def begin(self) -> None:
        super().begin()

    def clean_up_from_scene(self, scene: Scene) -> None:
        self.mobject.set_color(self.base_color)
        super().clean_up_from_scene(scene)

    def interpolate_mobject(self, alpha: float) -> None:
        alpha = self.rate_func(alpha)
        highlighted_index = int(alpha // self.step)
        for i in range(self.num_dashes):
            color = self.color if i == highlighted_index else self.base_color
            stroke = self.stroke if i == highlighted_index else self.base_stroke
            self.mobject.submobjects[i].set_color(color)
            self.mobject.submobjects[i].set(stroke_width=stroke)
