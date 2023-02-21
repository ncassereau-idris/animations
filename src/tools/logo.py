from manim import *

from pathlib import Path

def make_logo() -> ImageMobject:
    path = Path(__file__).parent.parent / 'assets' / 'LOGO_CNRS_2019_BLANC.gif'
    return ImageMobject(path)


def add_logo(scene: Scene) -> None:
    logo = make_logo()
    scene.add(logo)
    logo_size = 0.10

    def updater(mob: Mobject, dt: float):
        if isinstance(scene, MovingCameraScene):
            scene_width = scene.camera.frame.get_width()
            mob.scale_to_fit_width(
                scene_width * logo_size
            ).move_to(
                scene.camera.frame.point_from_proportion(0.5),
            ).shift(
                (mob.get_width() / 2  + scene_width * 0.01) * RIGHT,
                (mob.get_height() / 2 + scene_width * 0.01) * UP
            )
        else:
            scene_width = scene.camera.frame_width
            mob.scale_to_fit_width(scene_width * logo_size)
            mob.to_edge(DL, buff=scene_width * 0.01)

    logo.add_updater(updater)
