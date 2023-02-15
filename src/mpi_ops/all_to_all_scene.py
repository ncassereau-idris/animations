from manim import *

from .prepare_scene import prepare_scene

class MPIAllToAllScene(Scene):

    def construct(self):
        num_workers = 4
        cols = 10

        workers, comm, mpi_ops_title, comm_data = prepare_scene(
            title="MPI_Alltoall",
            num_workers=num_workers,
            cols=cols
        )
        self.add(workers, comm, mpi_ops_title)

        anim = [
            LaggedStart(*[
                ReplacementTransform(workers[work_idx].data[i], comm_data[work_idx][i])
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
            
            data = []
            start = cols_per_worker * i + min(i, r)
            stop = start + cols_per_worker
            if i < r:
                stop += 1

            for k in range(start, stop):
                for j in range(num_workers):
                    data.append(comm_data[j][k])
            data = VGroup(*data)
            target = worker.place_new_content(
                data.copy().arrange(RIGHT, worker.blocks_buffer)
            )

            anim.append(LaggedStart(*[
                Transform(data[j], target[j])
                for j in range(len(data))
            ], lag_ratio=0.025))

        self.play(LaggedStart(*anim, lag_ratio=0.5), run_time=5)
        self.wait(1)
