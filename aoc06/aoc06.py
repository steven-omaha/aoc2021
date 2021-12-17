import numpy as np
import numpy.typing as npt

SIZE = 1000000000


def iterate_np(
    generation: npt.NDArray[int], fish_count: int, number_generations: int
) -> npt.NDArray:
    for iteration in range(number_generations):
        print(iteration, fish_count)
        next_generation = np.zeros(SIZE, dtype=np.int8)
        new_spawn: list[int] = []
        for f in range(fish_count):
            fish = generation[f]
            if fish == 0:
                next_generation[f] = 6
                new_spawn.append(8)
            else:
                next_generation[f] = fish - 1
        new_fish_count = fish_count + len(new_spawn)
        next_generation[fish_count:new_fish_count] = np.asarray(
            new_spawn, dtype=np.int8
        )
        generation = next_generation
        fish_count = new_fish_count
    return generation


def iterate(generation: list[int], limit: int = 1) -> list[int]:
    if limit == 0:
        return generation
    for iteration in range(limit):
        print(iteration, len(generation))
        next_generation = []
        new_spawn = []
        for fish in generation:
            if fish == 0:
                next_generation.append(6)
                new_spawn.append(8)
            else:
                next_generation.append(fish - 1)
        generation = next_generation + new_spawn
        print(iteration)
    return generation


with open("testdata.txt") as fd:
    data = fd.read()

data = np.asarray([int(value) for value in data.split(",")], dtype=np.int8)
# result = iterate_np(data, len(data), 256)
result = iterate(list(data), 256)
print(len(result))
