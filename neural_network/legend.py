from manim import *


class Legend(VMobject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbols = []
        self.texts = []
        self.legends = []
        self.legends_object = None

    def append(self, symbol, text):
        symbol.scale_to_fit_width(0.5)
        self.symbols.append(symbol)
        self.texts.append(Text(text))

    def build(self, location=UR):
        self.symbols_grp = VGroup(*self.symbols).arrange(DOWN)
        self.texts_grp = VGroup(*self.texts).arrange(DOWN)
        self.symbols_grp.scale_to_fit_width(0.1)
        self.texts_grp.scale_to_fit_height(self.symbols_grp.get_height())
        both = VGroup(self.symbols_grp, self.texts_grp).arrange(RIGHT)
        both.scale_to_fit_width(2)

        # the buffer of 0.35 is right in between MED_SMALL_BUFF and MED_LARGE_BUFF
        self.frame = RoundedRectangle(
            corner_radius=0.2,
            height=both.get_height() + 0.35,
            width=both.get_width() + 0.35,
            stroke_width=DEFAULT_STROKE_WIDTH / 2
        )
        self.frame.to_edge(location, buff=SMALL_BUFF)
        both.move_to(self.frame.get_center())
        self.add(self.frame, both)
