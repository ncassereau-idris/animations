from manim import *
from itertools import chain

from .prepare_scene import prepare_scene
from ..tools.caption_scene import CaptionScene

class MPIAllReduceScene(CaptionScene): # All to all then reduce then all gather

    def construct(self):
        lagged_animation_all_to_all = True
        num_workers = 4
        cols = 8
        scale = 0.35

        workers, comm, mpi_ops_title = prepare_scene(
            title="MPI_Allreduce",
            num_workers=num_workers,
            cols=cols,
            scale=scale
        )
        self.add(workers, comm, mpi_ops_title)

        self.next_section("all to all")
        self.play(self.caption_fade_in("MPI_Alltoall"))
        anim = [
            LaggedStart(*[
                ReplacementTransform(workers[work_idx].data[i], comm.data[work_idx][i])
                # do it in the reverse order if on the right side of the screen
                for i in (
                    range(len(workers[work_idx].data))
                    if work_idx >= len(workers) // 2 else
                    range(len(workers[work_idx].data) - 1, -1, -1)
                )
            ], lag_ratio=0.025)
            for work_idx in range(len(workers))
        ]

        self.play(LaggedStart(*anim, lag_ratio=0.5), run_time=5)
        self.wait(1)

        cols_per_worker, r = divmod(cols, num_workers)
        anim = []
        for i, worker in enumerate(workers):
            
            start = cols_per_worker * i + min(i, r)
            stop = start + cols_per_worker
            if i < r:
                stop += 1

            data = []
            for j in range(num_workers):
                row = []
                for k in range(start, stop):
                    row.append(comm.data[j][k])
                data.append(VGroup(*row))

            worker.data = VGroup(*data).copy()
            data = list(chain(*zip(*data)))
            target = list(chain(*zip(*worker.data)))

            anim.append(LaggedStart(*[
                ReplacementTransform(data[j], target[j])
                for j in range(len(data))
            ], lag_ratio=0.025 if lagged_animation_all_to_all else 0))

        self.play(LaggedStart(*anim, lag_ratio=0.5), run_time=5)
        self.wait(1)

        self.next_section("local reduce")
        self.play(self.caption_replace("Local reduction"))
        reduce_anims = []
        for worker in workers:
            reduce_worker_anims = []
            new_worker_data = []
            for col in range(len(worker.data[0])):
                reduce_col_anims = []
                filled_square = Square(
                    side_length=worker.data[0][col].get_width(),
                    fill_opacity=1,
                    color=worker.data[0][col].color
                ).move_to(worker.data[0][col].get_center())
                new_worker_data.append(filled_square)
                for row in range(len(worker.data)):
                    reduce_col_anims.append(FadeOut(
                        worker.data[row][col],
                        shift=filled_square.get_center() - worker.data[row][col].get_center()
                    ))
                reduce_worker_anims.append(AnimationGroup(*reduce_col_anims, FadeIn(filled_square)))
            reduce_anims.append(LaggedStart(*reduce_worker_anims, lag_ratio=0.05))
            worker.data = VGroup(*new_worker_data)
        reduce_anims = AnimationGroup(*reduce_anims)
        self.play(reduce_anims, run_time=5)
        self.wait(2)

        self.next_section("all gather")
        self.play(self.caption_replace("MPI_Allgather"))
        comm.data = VGroup(*[
            workers[i].data.copy()
            for i in range(len(workers))
        ]).arrange(RIGHT, buff=DEFAULT_MOBJECT_TO_MOBJECT_BUFFER * scale)
        anim = [
            LaggedStart(*[
                ReplacementTransform(workers[work_idx].data[i], comm.data[work_idx][i])
                for i in (
                    range(len(workers[work_idx].data))
                    if work_idx >= len(workers) // 2 else
                    range(len(workers[work_idx].data) - 1, -1, -1)
                )
            ], lag_ratio=0.025)
            for work_idx in range(len(workers))
        ]

        self.play(LaggedStart(*anim, lag_ratio=0.5), run_time=5)
        self.wait(1)

        for i, worker in enumerate(workers):
            worker.data = comm.data.copy()
            if i < len(workers) - 1:
                self.play(ReplacementTransform(comm.data.copy(), worker.data))
            else:
                self.play(ReplacementTransform(comm.data, worker.data))

        self.play(self.caption_fade_out())
        self.wait(1)
