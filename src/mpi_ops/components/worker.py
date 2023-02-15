from manim import *
from typing import List, Optional
from manim.utils.color import Colors
from ...tools.frame import Frame

DEFAULT_COLOR_LIST = [GREEN, BLUE, RED, YELLOW]

class Worker(Frame):

    def __init__(
        self,
        rank: float = 0,
        rows: int = 1,
        cols: int = 1,
        blocks_side_length: float = 0.5,
        colors: List[Colors] = DEFAULT_COLOR_LIST,
        blocks_buffer: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        max_rows: Optional[int] = None,
        max_cols: Optional[int] = None,
        **kwargs: Any
    ) -> None:
        self.rank = rank
        self.rows = rows
        self.cols = cols
        self.colors = colors
        self.blocks_side_length = blocks_side_length
        self.blocks_buffer = blocks_buffer
        self.max_rows = max_rows or rows
        self.max_cols = max_cols or cols

        super().__init__(
            title=f"GPU {self.rank}",
            grid_rows=max_rows,
            grid_cols=max_cols,
            grid_block_size=blocks_side_length,
            grid_block_buffer=blocks_buffer,
            **kwargs
        )

        self.colors = list(self.make_colors())
        self._data = None
        self.data = self.make_data(rows * cols, self.colors)
        self.add(self.data, self.title, self.frame)

    def make_colors(self):
        for _ in range(self.rows):
            for i, color in enumerate(self.colors):
                q, r = divmod(self.cols, len(self.colors))
                if i < r:
                    q += 1
                for _ in range(q):
                    yield color

    def make_data(self, num_blocks, colors):
        data = [
            Square(color=colors[i], side_length=0.5, fill_opacity=0.5)
            for i in range(num_blocks)
        ]
        grp = VGroup(*data)
        return grp.arrange_in_grid(rows=self.rows, cols=self.cols)

    def get_data(self):
        return self._data

    def set_data(self, value: VMobject):
        self._data = self.place_new_content(value)

    def del_data(self):
        del self._data
    
    data = property(get_data, set_data, del_data)
