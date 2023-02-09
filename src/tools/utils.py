from manim import *
import numpy as np

dummy = Dot().shift(1e10 * RIGHT)

class StartUpdater(Animation):

    def __init__(self, mobject, interpolation, run_time=1, **kwargs):
        super().__init__(mobject, run_time=0, **kwargs)
        self.mobject_ = mobject
        self.interpolation = interpolation
        self.duration = run_time
        self.started = False

    def make_updater(self):
        dt_sum = 0

        def updater(mob, dt):
            nonlocal dt_sum
            dt_sum += dt
            alpha = dt_sum / self.duration
            if alpha >= 1:
                mob.remove_updater(updater)
                alpha = 1
            self.interpolation(mob, alpha)

        return updater

    def interpolate_mobject(self, alpha: float) -> None:
        if not self.started:
            self.mobject_.add_updater(self.make_updater())
            self.started = True


def fadeInAlphaFactory(mob, shift=None, has_fill=False):
    fill_color = mob.fill_color
    stroke_color = mob.stroke_color
    base_position = mob.get_center()

    def updater(mob, alpha):
        alpha = np.clip(alpha, 0, 1)
        if has_fill and hasattr(mob, "base_fill_opacity"):
            mob.set_fill(
                color=fill_color,
                opacity=alpha * mob.base_fill_opacity
            )
            mob.set_stroke(
                color=stroke_color,
                opacity=alpha
            )
        else:
            mob.set_opacity(alpha)
        if shift is not None:
            mob.move_to(base_position - shift * (1 - alpha))

    return updater


def fadeOutAlphaFactory(mob, shift=None, has_fill=False):
    if shift is not None:
        shift = -shift
    f = fadeInAlphaFactory(mob, shift=shift, has_fill=has_fill)
    return lambda mob, alpha: f(mob, 1 - alpha)

class DummyFadeOut(Animation):

    def __init__(self, mobject, shift=None, **kwargs):
        super().__init__(dummy, **kwargs)
        self.mobject_ = mobject
        self.shift = shift
        self.base_position = mobject.get_center()

    def interpolate_mobject(self, alpha: float) -> None:
        self.mobject_.set_opacity(1 - alpha)
        if self.shift is not None:
            self.mobject_.move_to(self.base_position + alpha * self.shift)


class FadeInAndRotating(Rotating, FadeIn):

    def __init__(
        self, mobject: Mobject, fadeInAlpha: float = 0.25,
        fadeOutAlpha: float = 0.25, rotate_rate_func=smooth,
        fade_rate_func=linear, **kwargs: Any
    ) -> None:
        self.fadeInAlpha = fadeInAlpha
        self.fadeOutAlpha = fadeOutAlpha
        self.rotate_rate_func = rotate_rate_func
        self.fade_rate_func = fade_rate_func
        Rotating.__init__(self, mobject, **kwargs)
        FadeIn.__init__(self, mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        self.mobject.become(self.starting_mobject)
        if alpha < self.fadeInAlpha:
            FadeIn.interpolate_mobject(
                self,
                self.fade_rate_func(alpha / self.fadeInAlpha)
            )
        elif alpha > 1 - self.fadeOutAlpha:
            FadeOut.interpolate_mobject(
                self,
                self.fade_rate_func((1 - alpha) / self.fadeOutAlpha)
            )
        else:
            FadeIn.interpolate_mobject(self, 1)

        self.mobject.rotate(
            self.rotate_rate_func(alpha) * self.radians,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )
