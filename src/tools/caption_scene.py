from manim import *

from typing import Optional

class CaptionScene(Scene):

    def caption_fade_in(self, text: str) -> FadeIn:
        self.caption = self.make_caption(text=text)
        return FadeIn(self.caption, shift=MED_LARGE_BUFF * DOWN)

    def caption_fade_out(self) -> FadeOut:
        fadeout = FadeOut(self.caption, shift=MED_LARGE_BUFF * DOWN)
        self.caption = None
        return fadeout

    def caption_replace(
        self, 
        new_text: str,
        wait_time: Optional[float] = None
    ) -> AnimationGroup:
        fadeout = self.caption_fade_out()
        fadein = self.caption_fade_in(text=new_text)
        anim = AnimationGroup(fadeout, fadein, run_time=1)
        if wait_time is not None:
            anim = Succession(
                Wait(run_time=wait_time / 2),
                anim,
                Wait(run_time=wait_time / 2)
            )
        return anim

    def play_caption_replace(
        self, 
        new_text: str,
        wait_time: Optional[float] = None
    ) -> None:
        self.play(self.caption_replace(new_text=new_text, wait_time=wait_time))

    @staticmethod
    def make_caption(text: str) -> MarkupText:
        return MarkupText(text=text, z_index=10000).scale(0.5).to_edge(DOWN)

    @staticmethod
    def italic_text(text: str) -> MarkupText:
        return MarkupText(text=f"<i>{text}</i>")

    def construct(self):
        raise NotImplementedError()