from manim import *

from .prepare_scene import prepare_scene
from ..tools.caption_scene import CaptionScene


class DDPScene(CaptionScene):

    def construct(self):
        num_workers = 4
        scale = 0.35

        networks, comm, title = prepare_scene(
            title="Distributed Data Parallel",
            num_workers=num_workers,
            scale=scale
        )
        self.add(networks, comm, title)

        self.next_section("forward")
        x = self.italic_text("x")
        y = self.italic_text("y")
        anim = []
        for network in networks:
            network.x = x.copy()
            network.y = y.copy()
            VGroup(network.x, network.y).arrange(RIGHT).move_to(
                network.frame.get_top() + UP * SMALL_BUFF,
                aligned_edge=DOWN
            ).scale(0.7)
            network.y.align_to(network.x, UP)
            anim.extend([
                FadeIn(network.x, shift=SMALL_BUFF * DOWN),
                FadeIn(network.y, shift=SMALL_BUFF * DOWN)
            ])

        self.play(
            self.caption_fade_in("Forward: storage of activations"),
            AnimationGroup(*anim)
        )

        anim = []
        for network in networks:
            network_anim = []
            for layer in network.layers:
                layer.frame.save_state()
                network_anim.append(AnimationGroup(
                    layer.frame.animate.set_color(YELLOW),
                    FadeIn(layer.activations, shift=SMALL_BUFF * RIGHT)
                ))
            anim.append(LaggedStart(*network_anim, lag_ratio=0.5))
        self.play(AnimationGroup(*anim))

        self.next_section("backward")
        self.play(self.caption_replace(
            "Backward: storage of gradients, suppression of activations"
        ))
        anim = []
        for network in networks:
            network_anim = []
            for layer in network.layers[::-1]:
                network_anim.append(AnimationGroup(
                    Restore(layer.frame),
                    FadeOut(layer.activations, shift=SMALL_BUFF * RIGHT),
                    FadeIn(layer.gradients, shift=SMALL_BUFF * RIGHT)
                ))
            anim.append(LaggedStart(*network_anim, lag_ratio=0.5))
        self.play(AnimationGroup(*anim))

        anim = []
        for network in networks:
            anim.append(FadeOut(network.x))
            anim.append(FadeOut(network.y))
        self.play(AnimationGroup(*anim))

        self.next_section("gradients all reduce")
        self.play(self.caption_replace("Gather gradients"))
        comm.data = VGroup(*[
            VGroup(*[
                layer.gradients.copy()
                for layer in network.layers
            ]).arrange(RIGHT, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * scale)
            for network in networks
        ]).arrange(DOWN, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * scale)

        anim = []
        for i, network in enumerate(networks):
            anim_network = []
            for j, layer in enumerate(network.layers):
                anim_network.append(ReplacementTransform(
                    layer.gradients, comm.data[i][j]
                ))
            anim.append(AnimationGroup(*anim_network))
        self.play(LaggedStart(*anim, lag_ratio=0.1), run_time=3)

        self.play(self.caption_replace("Reduce gradients"))
        anim = []
        for i in range(1, len(comm.data)):
            for j in range(len(comm.data[i])):
                anim.append(FadeOut(
                    comm.data[i][j],
                    shift=comm.data[0][j].get_center() - comm.data[i][j].get_center()
                ))
        self.play(AnimationGroup(*anim))

        self.play(self.caption_replace("Broadcast reduced gradients"))
        for i, network in enumerate(networks):
            anim_network = []
            for j, layer in enumerate(network.layers):
                target = layer.gradients.move_to(layer.gradients_ghost)
                source = comm.data[0][j]
                if i < len(networks) - 1:
                    source = source.copy()
                anim_network.append(ReplacementTransform(source, target))
            self.play(AnimationGroup(*anim_network))

        self.wait(0.5)
        self.play(self.caption_replace("Update parameters"))
        anim = []
        for network in networks:
            for layer in network.layers:
                anim.append(FadeOut(
                    layer.gradients,
                    shift=layer.parameters.get_center() - layer.gradients.get_center()
                ))
                anim.append(FadeOut(
                    layer.optimizer.copy(),
                    shift=layer.parameters.get_center() - layer.optimizer.get_center()
                ))
                anim.append(Indicate(layer.parameters))
        self.play(AnimationGroup(*anim), run_time=2)

        self.play(self.caption_fade_out())
        self.wait(3)
