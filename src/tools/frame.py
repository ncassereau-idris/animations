from __future__ import annotations

from manim import *

from typing import Optional, Any

class Frame(VMobject):

    def __init__(
        self, 
        title: str,
        content_width: Optional[float] = None,
        content_height: Optional[float] = None,
        grid_rows: Optional[int] = None,
        grid_cols: Optional[int] = None,
        grid_block_size: Optional[float] = None,
        grid_block_buffer: Optional[float] = None,
        title_content_buffer: float = MED_LARGE_BUFF,
        vertical_padding: float = MED_LARGE_BUFF,
        horizontal_padding: float = LARGE_BUFF,
        min_width: Optional[float] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.title = Text(title)
        self.content_width = content_width or Frame.compute_grid_size(
            grid_cols, grid_block_size, grid_block_buffer
        )
        self.content_height = content_height or Frame.compute_grid_size(
            grid_rows, grid_block_size, grid_block_buffer
        )
        self.title_content_buffer = title_content_buffer
        self.vertical_padding = vertical_padding
        self.horizontal_padding = horizontal_padding
        self.min_width = min_width

        self.frame = self.make_frame()
        self.place_title()
        self.add(self.frame, self.title)
        self._data = None

    def scale(self, scale_factor: float, **kwargs) -> Frame:
        self.title_content_buffer *= scale_factor
        return super().scale(scale_factor, **kwargs)

    def make_frame(self) -> RoundedRectangle:
        height = (
            self.title.get_height()
            + self.content_height
            + self.title_content_buffer
            + 2 * self.vertical_padding
        )
        width = max(self.title.get_width(), self.content_width) + 2 * self.horizontal_padding
        if self.min_width is not None:
            width = max(width, self.min_width)
        frame = RoundedRectangle(
            corner_radius=0.3,
            height=height,
            width=width
        )
        return frame

    def place_title(self) -> None:
        self.title.move_to(
            self.frame.get_top() + self.vertical_padding * DOWN,
            aligned_edge=UP
        )

    @staticmethod
    def compute_grid_size(
        n_blocks: int,
        block_size: float,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER
    ) -> float:
        return n_blocks * block_size + (n_blocks - 1) * buff

    def place_new_content(self, value: VMobject) -> VMobject:
        value.move_to(
            self.title.get_bottom() + self.title_content_buffer * DOWN,
            aligned_edge=UP
        )
        return value

    def get_data(self) -> VMobject:
        return self._data

    def set_data(self, value: VMobject) -> None:
        self._data = self.place_new_content(value)

    def del_data(self) -> None:
        del self._data
    
    data = property(get_data, set_data, del_data)