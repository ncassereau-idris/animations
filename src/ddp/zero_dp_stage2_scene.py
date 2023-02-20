from manim import *

from .prepare_scene import prepare_scene
from ..tools.caption_scene import CaptionScene

class ZeroDPStage2Scene(CaptionScene):

    def construct(self):
        num_workers = 4
        scale = 0.35

        networks, comm, title, legend = prepare_scene(
            title="ZeRO - Stage 2",
            num_workers=num_workers,
            scale=scale,
            zero_optimizer=True
        )
        self.add(networks, comm, title, legend)

        # Make blocks fade in for smooth starting point
        for network in networks:
            network.scene_init()
        self.wait(1)

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
            ).scale(2 * scale)
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
        self.wait(1)
        for i in range(len(networks[0].layers) - 1, -1, -1):
            layer_anim = []
            for network in networks:
                layer = network.layers[i]
                layer_anim.append(AnimationGroup(
                    Restore(layer.frame),
                    FadeOut(layer.activations, shift=SMALL_BUFF * RIGHT),
                    FadeIn(layer.gradients, shift=SMALL_BUFF * RIGHT)
                ))
            self.play_caption_replace(f"Backward layer {i + 1}: gradients computation")
            self.play(AnimationGroup(*layer_anim))

            comm.data = VGroup(*[
                network.layers[i].gradients.copy()
                for network in networks
            ]).arrange(DOWN, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * scale)
            anim = []
            for j, network in enumerate(networks):
                anim.append(ReplacementTransform(
                    network.layers[i].gradients, comm.data[j]
                ))
            self.play_caption_replace(f"Backward layer {i + 1}: gather gradients")
            self.play(LaggedStart(*anim, lag_ratio=0.1))

            anim = []
            for j in range(1, len(comm.data)):
                anim.append(FadeOut(
                    comm.data[j],
                    shift=comm.data[0].get_center() - comm.data[j].get_center()
                ))
            self.play_caption_replace(f"Backward layer {i + 1}: reduce gradients")
            self.play(AnimationGroup(*anim))

            layer = networks[i].layers[i]
            self.play_caption_replace(f"Backward layer {i + 1}: store gradients for update")
            self.play(ReplacementTransform(
                comm.data[0],
                layer.gradients.move_to(layer.gradients_ghost)
            ))

        anim = []
        for network in networks:
            anim.append(FadeOut(network.x))
            anim.append(FadeOut(network.y))
        self.play(AnimationGroup(*anim))

        self.play_caption_replace("Workers update parameters for their assigned layers", wait_time=1)
        anim = []
        for network in networks:
            for layer in network.layers:
                if layer.show_optimizer:
                    anim.append(FadeOut(
                        layer.gradients,
                        shift=layer.parameters.get_center() - layer.gradients.get_center()
                    ))
                    anim.append(FadeOut(
                        layer.optimizer.copy(),
                        shift=layer.parameters.get_center() - layer.optimizer.get_center()
                    ))
                    anim.append(Indicate(layer.parameters))
                else:
                    anim.append(FadeOut(layer.parameters))
        self.play(AnimationGroup(*anim), run_time=2)

        self.next_section("parameters all gather")
        self.play_caption_replace("Gather parameters from all workers", wait_time=1)
        comm.data = VGroup(*[
            layer.parameters.copy()
            for network in networks
            for layer in network.layers
            if layer.show_optimizer
        ]).arrange(RIGHT, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * scale)

        anim = []
        idx = 0
        for network in networks:
            for layer in network.layers:
                if layer.show_optimizer:
                    anim.append(ReplacementTransform(
                        layer.parameters,
                        comm.data[idx]
                    ))
                    idx += 1
        self.play(*anim, run_time=2)
        self.wait(1)

        for i, network in enumerate(networks):
            anim_network = []
            for j, layer in enumerate(network.layers):
                target = layer.parameters.move_to(layer.parameters_ghost)
                source = comm.data[j]
                if i < len(networks) - 1:
                    source = source.copy()
                anim_network.append(ReplacementTransform(source, target))
            self.play(AnimationGroup(*anim_network))

        self.play(self.caption_fade_out())
        self.wait(2)
