from __future__ import annotations

from functools import cache, reduce


ADJACENT_INDICIES = [-1, 0, 1]


class Grid:
    def __init__(self, cells: list[Cell]):
        self.cells = set(cells)
        self.adjacent_cells: set[Cell] = set()
        self.visited_cells: set[Cell] = set()

    def __getitem__(self, position: Position) -> Cell:
        return self._get_cell_by_position(position)

    @property
    @cache
    def destination(self) -> Position:
        return reduce(
            lambda c0, c1: c1 if c1 > c0 else c0,
            map(lambda cell: cell.position, self.cells),
        )

    @property
    def start(self) -> Position:
        return Position(0, 0)

    def _get_cell_by_position(self, position: Position) -> Cell:
        for cell in self.cells:
            if cell.position == position:
                return cell
        raise IndexError("Cell not found.")

    @classmethod
    def from_file(cls, filename) -> Grid:
        with open(filename) as fd:
            lines = fd.readlines()
        cells = [
            Cell(Position(line_idx, column_idx), int(digit))
            for line_idx, line in enumerate(lines)
            for column_idx, digit in enumerate(line.strip())
        ]
        return Grid(cells)

    @property
    @cache
    def boundary(self) -> Boundary:
        return Boundary(self.start, self.destination)


class Cell:
    def __init__(self, position: Position, value: int):
        self.position = position
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __sub__(self, other_position: Position) -> int:
        return abs(other_position - self.position) + self.value

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        return self.position.__hash__()


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other: Position) -> bool:
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: Position) -> bool:
        return (self.x + self.y) < (other.x + other.y)

    def __add__(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __sub__(self, other: Position) -> Position:
        return Position(other.x - self.x, other.y - self.y)

    def __abs__(self) -> int:
        return self.x + self.y

    @property
    def neighbours(self):
        return (
            self + Position(x, y)
            for x in ADJACENT_INDICIES
            for y in ADJACENT_INDICIES
            if not x == y
        )


class Boundary:
    def __init__(self, corner1: Position, corner2: Position):
        self.corner1 = corner1
        self.corner2 = corner2
        if self.corner1 > self.corner2:
            self.corner1, self.corner2 = self.corner2, self.corner1

    def __contains__(self, item: Position):
        return (
            self.corner1.x <= item.x <= self.corner2.x
            and self.corner1.y <= item.y <= self.corner2.y
        )


class AStar:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.visited_positions: list[Position] = [grid.start]
        self.adjacent_positions: set[Position] = set()
        self._update_adjacent_positions(grid.start)
        self.graphs: list[Graph] = [Graph.from_grid(grid)]

    def solve(self):
        while True:
            cell = self.next_cell
            self._visit(cell)

            if cell.position == grid.destination:
                break
            self._update_adjacent_positions(cell.position)

    def _visit(self, cell: Cell):
        self.visited_positions.append(cell.position)
        self.adjacent_positions.remove(cell.position)

    def _find_adjacent_graph_with_minimum_risk(self, position: Position) -> Graph:
        adjacent_graphs = filter(
            lambda graph: position in graph, self.graphs
        )

    @property
    def next_cell(self) -> Cell:
        # cell with minimum distance to destination
        return reduce(
            lambda cell0, cell1: cell1
            if (cell1 - self.grid.destination) < (cell0 - self.grid.destination)
            else cell0,
            map(lambda position: self.grid[position], self.adjacent_positions),
        )

    def __repr__(self):
        return (
            f"{self.visited_positions=}\n{self.last_position=}\n{self.adjacent_positions=}"
        )

    @property
    def last_position(self):
        return self.visited_positions[-1]

    def _update_adjacent_positions(self, last_position: Position):
        self.adjacent_positions = self.adjacent_positions.union(
            set(
                [
                    neighbour
                    for neighbour in last_position.neighbours
                    if neighbour in self.grid.boundary
                    and neighbour not in self.visited_positions
                ]
            )
        )


class Graph:
    def __init__(self, elements: list[Position], *, extends: Graph | None, at: int | None):
        self.elements = elements
        self.extends = extends
        self.at = at

    def __contains__(self, position: Position):
        return position in self.elements

    def append(self, position: Position):
        self.elements.append(position)

    def __len__(self):
        return len(self.elements)

    @property
    def last_position(self) -> Position:
        return self.elements[-1]

    @classmethod
    def from_grid(cls, grid: Grid) -> Graph:
        return cls([grid.start], extends=None, at=None)


grid = Grid.from_file("testdata.txt")
astar = AStar(grid)

print(astar)
print()
astar.solve()
print(astar)
