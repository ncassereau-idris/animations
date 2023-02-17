from manim import *

from .prepare_scene import prepare_scene


class DDPScene(Scene):

    @staticmethod
    def make_text(text: str) -> MarkupText:
        return MarkupText(text=text).scale(0.5).to_edge(DOWN)

    def construct(self):
        num_workers = 4
        scale = 0.35

        networks, comm, title = prepare_scene(
            title="Distributed Data Parallel",
            num_workers=num_workers,
            scale=scale
        )
        self.add(networks, comm, title)
        for network in networks:
            for layer in network.layers:
                layer.remove(layer.gradients, layer.activations)

        self.next_section("forward")
        x = MarkupText(text="<i>x</i>")
        y = MarkupText(text="<i>y</i>")
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
        self.caption = self.make_text("Forward: storage of activations")
        self.next_caption = self.make_text("Backward: storage of gradients, suppression of activations")
        self.play(
            FadeIn(self.caption, shift=MED_LARGE_BUFF * DOWN),
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
        self.play(
            FadeOut(self.caption, shift=MED_LARGE_BUFF * DOWN),
            FadeIn(self.next_caption, shift=MED_LARGE_BUFF * DOWN)
        )
        self.caption = self.next_caption
        self.next_caption = self.make_text("Gather gradients")
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
        self.play(
            FadeOut(self.caption, shift=MED_LARGE_BUFF * DOWN),
            FadeIn(self.next_caption, shift=MED_LARGE_BUFF * DOWN)
        )
        self.caption = self.next_caption
        self.next_caption = self.make_text("Reduce gradients")

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

        self.play(
            FadeOut(self.caption, shift=MED_LARGE_BUFF * DOWN),
            FadeIn(self.next_caption, shift=MED_LARGE_BUFF * DOWN)
        )
        self.caption = self.next_caption
        self.next_caption = self.make_text("Broadcast reduced gradients")
        anim = []
        for i in range(1, len(comm.data)):
            for j in range(len(comm.data[i])):
                anim.append(FadeOut(
                    comm.data[i][j],
                    shift=comm.data[0][j].get_center() - comm.data[i][j].get_center()
                ))
        self.play(AnimationGroup(*anim))

        self.play(
            FadeOut(self.caption, shift=MED_LARGE_BUFF * DOWN),
            FadeIn(self.next_caption, shift=MED_LARGE_BUFF * DOWN)
        )
        self.caption = self.next_caption
        self.next_caption = self.make_text("Update parameters")

        for i, network in enumerate(networks):
            anim_network = []
            for j, layer in enumerate(network.layers):
                target = layer.gradients.move_to(layer.gradients_ghost)
                source = comm.data[0][j]
                if i < len(networks) - 1:
                    source = source.copy()
                anim_network.append(ReplacementTransform(source, target))
            self.play(AnimationGroup(*anim_network))

        self.play(
            FadeOut(self.caption, shift=MED_LARGE_BUFF * DOWN),
            FadeIn(self.next_caption, shift=MED_LARGE_BUFF * DOWN)
        )
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

        self.play(FadeOut(self.next_caption, shift=MED_LARGE_BUFF * DOWN))
        self.wait(3)
