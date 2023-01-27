from manim import *
import numpy as np

class Disperse(Animation):

    def __init__(self, mobject, dot_radius=.05, dot_number=100, **kwargs):
        super().__init__(mobject, **kwargs)
        self.dot_radius = dot_radius
        self.dot_number = dot_number
        
    def begin(self):
        dots = VGroup(*[
            Dot(radius=self.dot_radius).move_to(self.mobject.point_from_proportion(p))
            for p in np.linspace(0, 1, self.dot_number)
        ])
        for dot in dots:
            dot.initial_position = dot.get_center()
            dot.shift_vector = 2 * (dot.get_center() - self.mobject.get_center())
        dots.set_opacity(0.)
        self.mobject.add(dots)
        self.dots = dots
        super().begin()
        
    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        scene.remove(self.dots)
        
    def interpolate_mobject(self, alpha):
        if alpha <= 0.5:
            self.mobject.set_opacity(1-2*alpha, family=False)
            self.dots.set_opacity(2 * alpha)
        else:
            self.mobject.set_opacity(0)
            self.dots.set_opacity(2*(1-alpha))
            for dot in self.dots:
                dot.move_to(dot.initial_position + dot.shift_vector * 2 * (alpha - 0.5))
        
        
class AZE(Scene):
    def construct(self):
        s = Square(color=BLUE, fill_opacity=1.)
        self.add(s)
        self.play(Disperse(s, run_time=2))
        self.wait()