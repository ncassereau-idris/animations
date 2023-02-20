from manim import *

from .prepare_scene import prepare_scene

class MPIAllReduceSimplifiedScene(Scene): # Allgather then local reduce

    def construct(self):
        num_workers = 4
        cols = 8

        workers, comm, mpi_ops_title = prepare_scene(
            title="MPI_Allreduce (simplified)",
            num_workers=num_workers,
            cols=cols
        )
        self.add(workers, comm, mpi_ops_title)

        # Make blocks fade in for smooth starting point
        self.play(AnimationGroup(*[worker.scene_init() for worker in workers]))
        self.wait(1)

        self.next_section("all gather")
        # All gather
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

        self.next_section("local reduce")
        # Local reduce
        reduce_anims = []
        for worker in workers:
            reduce_worker_anims = []
            for col in range(len(worker.data[0])):
                reduce_col_anims = []
                for row in range(1, len(worker.data)):
                    reduce_col_anims.append(
                        worker.data[row][col].animate.move_to(worker.data[0][col])
                    )
                reduce_worker_anims.append(
                    AnimationGroup(*reduce_col_anims)
                )
            reduce_anims.append(AnimationGroup(*reduce_worker_anims))
        reduce_anims = AnimationGroup(*reduce_anims)
        self.play(reduce_anims, run_time=5)
        self.wait(1)
        # Make blocks fade out for smooth ending
        self.play(AnimationGroup(*[worker.scene_cleanup() for worker in workers]))
        self.wait(2)
            