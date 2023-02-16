from manim import *

from typing import List, Generator
from manim.utils.color import Colors

DEFAULT_REDUCED_COLOR_LIST = [GREEN, BLUE, RED, YELLOW]
DEFAULT_LONG_COLOR_LIST = [TEAL, GREEN, YELLOW, BLUE, RED, LIGHT_BROWN, WHITE, LIGHT_PINK]

class ColorsColumnRotation:

    def __init__(
        self,
        colors: List[Colors], 
        cols: int,
        consecutive: bool = False # if fewer colors than columns, should it be cyclical or consecutive ?
    ):
        self.colors = colors
        self.consecutive = consecutive
        self.cols = cols
        self.iterator = None

    def make_colors_row_cyclic(self) -> Generator[Colors, None, None]:
        for i in range(self.cols):
            yield self.colors[i % len(self.colors)]

    def make_colors_row_consecutive(self) -> Generator[Colors, None, None]:
        for i, color in enumerate(self.colors):
            q, r = divmod(self.cols, len(self.colors))
            if i < r:
                q += 1
            for _ in range(q):
                yield color

    def infinite_loop(self, gen_factory):
        while True:
            generator = gen_factory()
            yield from generator

    def __iter__(self):
        if self.consecutive:
            return iter(self.infinite_loop(self.make_colors_row_consecutive))
        else:
            return iter(self.infinite_loop(self.make_colors_row_cyclic))

    def restart(self):
        if self.iterator is not None:
            del self.iterator
        self.iterator = iter(self)

    def next(self):
        if self.iterator is None:
            self.restart()
        return next(self.iterator)
