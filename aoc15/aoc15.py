from __future__ import annotations

from functools import cache, reduce


ADJACENT_INDICIES = [-1, 0, 1]


class Grid:
    def __init__(self, cells: list[Cell]):
        self.cells = set(cells)

    def __getitem__(self, position: Position) -> Cell:
        return self._get_cell_by_position(position)

    @property
    @cache
    def destination(self) -> Position:
        return reduce(
            lambda pos0, pos1: pos1 if pos1 > pos0 else pos0,
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
        return f"{self.position}: {self.value}"

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
    def neighbours(self) -> list[Position]:
        return list(
            self + Position(x, y)
            for x in ADJACENT_INDICIES
            for y in ADJACENT_INDICIES
            if not abs(x) == abs(y)
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
            self._join_to_graphs(cell)
            if cell.position == grid.destination:
                break
            self._update_adjacent_positions(cell.position)
        self._print_result()

    def _visit(self, cell: Cell):
        self.visited_positions.append(cell.position)
        self.adjacent_positions.remove(cell.position)

    def _find_adjacent_graph_with_minimum_risk(self, position: Position) -> Graph:
        adjacent_graphs = filter(
            lambda graph: position in graph.last_position.neighbours, self.graphs
        )
        return reduce(lambda g1, g2: min(g1.risk, g2.risk), adjacent_graphs)

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
        return f"{self.visited_positions=}\n{self.last_position=}\n{self.adjacent_positions=}"

    @property
    def last_position(self) -> Position:
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

    def _join_to_graphs(self, cell: Cell):
        suitable_graphs = [
            graph for graph in self.graphs if graph.can_extend_to_cell(cell)
        ]
        if suitable_graphs:
            self._append_existing_graph(cell, suitable_graphs)
        else:
            self._create_new_graph(cell)

    def _create_new_graph(self, cell):
        graphs = [
            graph for graph in self.graphs if graph.contains_neighbour_of_cell(cell)
        ]
        indices = [graph.find_insertion_index(cell) for graph in graphs]
        risks = [graph.risk_up_to_index(index) for graph, index in zip(graphs, indices)]

        graph, position, risk = reduce(
            lambda tuple0, tuple1: tuple0 if tuple0[2] < tuple1[2] else tuple1,
            zip(graphs, indices, risks),
        )
        self.graphs.append(Graph([cell], extends=graph, at=position))

    @staticmethod
    def _append_existing_graph(cell: Cell, suitable_graphs: list[Graph]):
        minimum_risk_graph = min(
            [graph for graph in suitable_graphs], key=lambda g: g.risk
        )
        minimum_risk_graph.append(cell)

    def _print_result(self):
        graph = [graph for graph in self.graphs if self.grid.destination in graph][0]
        print(graph)


class Graph:
    def __init__(self, elements: list[Cell], *, extends: Graph | None, at: int | None):
        self.elements: list[Cell] = elements
        self.extends: Graph | None = extends
        self.at: int | None = at

    def __contains__(self, element: Cell | Position):
        if isinstance(element, Cell):
            return element in self.elements
        return element in [cell.position for cell in self.elements]

    def __repr__(self):
        graph = " ->\n ".join([str(cell) for cell in self[: len(self)]])
        risk = self.risk
        return f"{graph}\n{risk=}"

    @property
    def pretty_repr(self):
        # TODO
        result = ""

    def __getitem__(self, item: int | slice) -> list[Cell]:
        result = self.elements[item]
        if self.extends:
            result = self.extends[: (self.at + 1)] + result
        return result

    def append(self, cell: Cell):
        self.elements.append(cell)

    def __len__(self):
        if self.extends:
            return len(self.elements) + len(self.extends)
        return len(self.elements)

    @property
    def total_elements(self) -> list[Cell]:
        return self[: len(self)]

    @property
    def risk(self) -> int:
        return self.risk_up_to_index(len(self))

    def risk_up_to_index(self, idx: int | None = None) -> int:
        if idx is None:
            idx = len(self)
        own_risk = sum([cell.value for cell in self.elements[:idx]])
        other_risk = 0
        if self.extends:
            other_risk = self.extends.risk_up_to_index(self.at + 1)
        else:  # graph that contains the start, which is not be counted
            own_risk -= self.elements[0].value
        return own_risk + other_risk

    @property
    def last_cell(self) -> Cell:
        return self.elements[-1]

    @classmethod
    def from_grid(cls, grid: Grid) -> Graph:
        return cls([grid[grid.start]], extends=None, at=None)

    def can_extend_to_cell(self, cell: Cell) -> bool:
        return cell.position in self.last_cell.position.neighbours

    def contains_neighbour_of_cell(self, cell: Cell) -> bool:
        return any([neighbour in self for neighbour in cell.position.neighbours])

    def find_insertion_index(self, cell: Cell) -> int:
        for i, element in enumerate(self.elements):
            if cell.position in element.position.neighbours:
                return i
        raise ValueError("Could not find a place to start a new graph.")


grid = Grid.from_file("testdata.txt")
astar = AStar(grid)

# print(astar)
# print()
astar.solve()
# print(astar)
