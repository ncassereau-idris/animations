from manim import *

from .prepare_scene import prepare_scene

class MPIAllGatherScene(Scene):

    def construct(self):
        num_workers = 4
        cols = 8

        workers, comm, mpi_ops_title = prepare_scene(
            title="MPI_Allgather",
            num_workers=num_workers,
            cols=cols
        )
        self.add(workers, comm, mpi_ops_title)

        # Make blocks fade in for smooth starting point
        self.play(AnimationGroup(*[worker.scene_init() for worker in workers]))

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

        self.wait(1)
        # Make blocks fade out for smooth ending
        self.play(AnimationGroup(*[worker.scene_cleanup() for worker in workers]))
        self.wait(2)
