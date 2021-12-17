from __future__ import annotations

import numpy as np


class Grid:
    @classmethod
    def from_lines(cls, lines: list[Line]) -> Grid:
        instance = Grid()
        for line in lines:
            print(line.spanning_fields)
            for fields in line.spanning_fields:
                instance.grid[fields[0], fields[1]] += 1
        return instance

    def __init__(self, x=1000, y=1000):
        self.grid = np.zeros((x, y), dtype=int)


class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    @classmethod
    def from_str(cls, line: str) -> Line:
        (x1, y1), (x2, y2) = [item.strip().split(",") for item in line.split("->")]
        return Line(int(x1), int(y1), int(x2), int(y2))

    @property
    def spanning_fields_parallel(self) -> list[tuple[int, int]]:
        result = []
        if self.x1 != self.x2:
            result.extend(list(zip(self.x_array, len(self.x_array) * [self.y1])))
        else:
            result.extend(list(zip(len(self.y_array) * [self.x1], self.y_array)))
        return result

    @staticmethod
    def vec_array(z1, z2) -> list[int]:
        if z2 > z1:
            return list(range(z1, z2 + 1))
        return list(range(z2, z1 + 1))[::-1]

    @property
    def x_array(self) -> list[int]:
        return self.vec_array(self.x1, self.x2)

    @property
    def y_array(self) -> list[int]:
        return self.vec_array(self.y1, self.y2)

    @property
    def is_diagonal(self) -> bool:
        return self.x1 != self.x2 and self.y1 != self.y2

    @property
    def spanning_fields_diagonal(self) -> list[tuple[int, int]]:
        result = []
        for x, y in zip(self.x_array, self.y_array):
            result.append((x, y))
        return result

    @property
    def spanning_fields(self) -> list[tuple[int, int]]:
        if self.is_diagonal:
            return self.spanning_fields_diagonal
        return self.spanning_fields_parallel


def read_data(filename: str) -> list[Line]:
    with open(filename) as fd:
        lines = fd.readlines()
    return [Line.from_str(line) for line in lines]


lines = read_data("data.txt")
grid = Grid.from_lines(lines)
idxs = np.argwhere(grid.grid > 1)
print(len(idxs))
print(grid.grid.T)
