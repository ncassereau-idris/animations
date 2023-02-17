from manim import *

class CaptionScene(Scene):

    def caption_fade_in(self, text: str) -> FadeIn:
        self.caption = self.make_caption(text=text)
        return FadeIn(self.caption, shift=MED_LARGE_BUFF * DOWN)

    def caption_fade_out(self) -> FadeOut:
        fadeout = FadeOut(self.caption, shift=MED_LARGE_BUFF * DOWN)
        self.caption = None
        return fadeout

    def caption_replace(self, new_text: str) -> AnimationGroup:
        fadeout = self.caption_fade_out()
        fadein = self.caption_fade_in(text=new_text)
        return AnimationGroup(fadeout, fadein)

    @staticmethod
    def make_caption(text: str) -> MarkupText:
        return MarkupText(text=text, z_index=10000).scale(0.5).to_edge(DOWN)

    @staticmethod
    def italic_text(text: str) -> MarkupText:
        return MarkupText(text=f"<i>{text}</i>")

    def construct(self):
        raise NotImplementedError()