from manim import *


class StartUpdater(Animation):

    def __init__(self, mobject, interpolation, run_time=1, **kwargs):
        super().__init__(mobject, run_time=0, **kwargs)
        self.mobject = mobject
        self.interpolation = interpolation
        self.duration = run_time

    def make_updater(self):
        dt_sum = 0

        def updater(mob, dt):
            nonlocal dt_sum
            dt_sum += dt
            alpha = dt_sum / self.duration
            if alpha >= 1:
                mob.remove_updater(updater)
            self.interpolation(mob, alpha)

        return updater


    def begin(self) -> None:
        super().begin()
        self.mobject.add_updater(self.make_updater())

    def interpolate_mobject(self, alpha: float) -> None:
        pass

    def clean_up_from_scene(self, scene: Scene) -> None:
        super().clean_up_from_scene(scene)


def fadeInAlphaFactory(mob, shift=None):
    fill_color = mob.fill_color
    stroke_color = mob.stroke_color
    base_position = mob.get_center()

    def updater(mob, alpha):
        alpha = np.clip(alpha, 0, 1)
        mob.set_fill(
            color=fill_color,
            opacity=alpha * mob.base_fill_opacity
        )
        mob.set_stroke(
            color=stroke_color,
            opacity=alpha
        )
        if shift is not None:
            mob.move_to(base_position - shift * (1 - alpha))

    return updater


def fadeOutAlphaFactory(mob, shift=None):
    f = fadeInAlphaFactory(mob, shift=shift)
    return lambda mob, alpha: f(mob, 1 - alpha)
