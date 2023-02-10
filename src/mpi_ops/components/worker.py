from manim import *
from typing import List, Optional
from manim.utils.color import Colors

DEFAULT_COLOR_LIST = [GREEN, BLUE, RED, YELLOW]

class Worker(VMobject):

    def __init__(
        self,
        rank: float = 0,
        num_blocks: int = 4,
        frame_height: Optional[float] = None,
        frame_width: Optional[float] = None,
        colors: List[Colors] = DEFAULT_COLOR_LIST,
        **kwargs: Any
        ) -> None:
        super().__init__(**kwargs)
        self.rank = rank
        self.num_blocks = num_blocks
        self.frame_height = frame_height
        self.frame_width = frame_width

        self.colors = list(self.make_colors(num_blocks, colors))
        self.data_squares = self.make_data(num_blocks, self.colors)
        self.title = self.make_title()
        self.content = VGroup(self.data_squares, self.title)
        self.frame = self.make_frame(
            corner_radius=0.3,
            height=frame_height,
            width=frame_width,
            stroke_width=DEFAULT_STROKE_WIDTH
        )

        self.add(self.data_squares, self.title, self.frame)

    def make_frame(
        self,
        height: Optional[float] = None,
        width: Optional[float] = None, **kwargs
    ) -> RoundedRectangle:
        if height is None:
            height = self.content.get_height() + 2 * MED_LARGE_BUFF
        if width is None:
            width = self.content.get_width() + 2 * MED_LARGE_BUFF
        frame = RoundedRectangle(height=height, width=width, **kwargs)
        frame.move_to(self.content.get_center())
        return frame

    def make_title(self):
        title = Text(
            text=f"GPU {self.rank}"
        )
        title.next_to(self.data_squares, direction=UP, buff=MED_LARGE_BUFF)
        return title

    @staticmethod
    def make_colors(num_blocks, colors):
        for i, color in enumerate(colors):
            repeat_color = num_blocks // len(colors)
            if i < (num_blocks % len(colors)):
                repeat_color += 1
            for _ in range(repeat_color):
                yield color

    @staticmethod
    def make_data(num_blocks, colors):
        data = [
            Square(color=colors[i], side_length=0.5, fill_opacity=0.5)
            for i in range(num_blocks)
        ]
        return VGroup(*data).arrange(RIGHT)
