from manim import *
import numpy as np

class LineAnim(Animation):
    
    def __init__(self, mobject, color=ORANGE, alpha_between=0.3, alpha_eps=1e-6, rate_func=None, **kwargs):
        super().__init__(mobject, **kwargs)
        self.start = mobject.start
        self.end = mobject.end
        self.color = color
        self.alpha_between = alpha_between
        self.alpha_eps = alpha_eps
        self.rate_func = rate_func
        
    def begin(self):
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

    def get_coord(self, alpha):
        return alpha * self.end + (1 - alpha) * self.start

    def get_alphas(self, alpha):
        alpha1 = alpha * (1 + self.alpha_between)
        alpha2 = alpha1 - self.alpha_between
        return alpha1, alpha2

    def get_points_pair(self, alpha):
        return self.get_coord(alpha - self.alpha_eps), self.get_coord(alpha + self.alpha_eps)

    def interpolate_mobject(self, alpha):
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
        
    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        self.all_group.set_opacity(0)
        self.mobject.set_opacity(1., family=False)
        scene.remove(self.all_group)
        scene.add(self.mobject)
       
        
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

  
class CURVE(Scene):
    def construct(self):
        net = Network([1, 2, 1]).shift(RIGHT)#.scale(2)
        self.add(net)
        self.wait(1)
        self.play(net.forward_animation())
        self.wait(1)
        
        
    def tmp(self):
        p1 = Dot([-2, 0, 0], radius=0.1, color=BLUE)
        p2 = Dot([2, 1, 0], radius=0.1, color=RED)
        p3 = Dot([2, -1, 0], radius=0.1, color=RED)
        line = Line(start=p1, end=p2, color=WHITE)
        self.add(p1, p2, p3, line)
        self.wait(1)
        #self.play(LineAnim(line, rate_func=smooth, run_time=3.))
        self.play(Succession(Indicate(p1), LineAnim(line, rate_func=smooth, run_time=1.), Indicate(p2)))
        self.wait(1)