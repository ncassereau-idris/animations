from manim import *

class Communicator(VMobject):

    def __init__(self, height: float, width: float, **kwargs) -> None:
        super().__init__(**kwargs)
        self.frame_height = height
        self.frame_width = width
        self.frame = self.make_frame()
        self.text = Text(text="Communicator")
        self.text.next_to(self.frame.get_top(), DOWN)
        self.add(self.frame, self.text)

    def make_frame(self):
        frame = RoundedRectangle(
            height=self.frame_height,
            width=self.frame_width,
            corner_radius=0.5
        )
        return frame
