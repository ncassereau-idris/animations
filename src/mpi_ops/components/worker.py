from manim import *

class Worker(VMobject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dot = Dot(color=GREEN)
        self.add(self.dot)
