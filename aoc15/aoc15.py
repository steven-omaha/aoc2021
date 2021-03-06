from __future__ import annotations

from functools import reduce, cached_property
from typing import overload


ADJACENT_INDICES = [-1, 0, 1]


class Grid:
    def __init__(self, cells: list[Cell]):
        self.cells = set(cells)

    def __getitem__(self, position: Position) -> Cell:
        return self._get_cell_by_position(position)

    @cached_property
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

    @cached_property
    def boundary(self) -> Boundary:
        return Boundary(self.start, self.destination)


class Cell:
    def __init__(self, position: Position, value: int):
        self.position = position
        self.value = value
        assert 1 <= self.value <= 9

    def __repr__(self):
        return f"{self.position}: {self.value}"

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            raise NotImplementedError
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: Position) -> bool:
        return (self.x + self.y) < (other.x + other.y)

    def __gt__(self, other: Position) -> bool:
        return not self < other

    def __add__(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)

    def __hash__(self):
        return (self.x, self.y).__hash__()

    def __sub__(self, other: Position) -> int:
        return abs(other.x - self.x) + abs(other.y - self.y)

    def __abs__(self) -> int:
        return self.x + self.y

    @property
    def neighbours(self) -> list[Position]:
        return list(
            self + Position(x, y)
            for x in ADJACENT_INDICES
            for y in ADJACENT_INDICES
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
            cell = self.get_cell_with_minimum_distance_to_destination(
                self.grid, self.adjacent_positions
            )
            self._visit(cell)
            self._join_to_graphs(cell)
            if cell.position == self.grid.destination:
                break
            self._update_adjacent_positions(cell.position)
        self._print_result()

    def _visit(self, cell: Cell):
        self.visited_positions.append(cell.position)
        self.adjacent_positions.remove(cell.position)

    @classmethod
    def get_cell_with_minimum_distance_to_destination(
        cls, grid: Grid, adjacent_positions: set[Position]
    ) -> Cell:
        print("evaluating metrics")
        return reduce(
            lambda cell0, cell1: cell0
            if cls._evaluate_possible_cell_with_metric(cell0, grid)
            < cls._evaluate_possible_cell_with_metric(cell1, grid)
            else cell1,
            map(lambda position: grid[position], adjacent_positions),
        )

    @staticmethod
    def _evaluate_possible_cell_with_metric(cell: Cell, grid: Grid) -> int:
        distance = cell.position - grid.destination
        if distance == 0:
            return 0
        risk = cell.value
        metric = distance + 5 * risk
        print(f"{distance=}, {risk=}, {metric=}")
        return metric

    def __repr__(self):
        return f"{self.visited_positions=}\n{self.last_position=}\n{self.adjacent_positions=}"

    @property
    def last_position(self) -> Position:
        return self.visited_positions[-1]

    def _update_adjacent_positions(self, last_position: Position):
        last_position_neighbours = set(
            [
                neighbour
                for neighbour in last_position.neighbours
                if neighbour in self.grid.boundary
                and neighbour not in self.visited_positions
            ]
        )
        self.adjacent_positions = self.adjacent_positions.union(
            last_position_neighbours
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
        indices = [graph.find_best_cell_to_start_new_graph(cell) for graph in graphs]
        risks = [graph.risk_up_to_index(index) for graph, index in zip(graphs, indices)]

        graph, position, risk = reduce(
            lambda tuple0, tuple1: tuple0 if tuple0[2] < tuple1[2] else tuple1,
            zip(graphs, indices, risks),
        )
        self.graphs.append(Graph([cell], extends_graph=graph, at_idx=position))

    @staticmethod
    def _append_existing_graph(cell: Cell, suitable_graphs: list[Graph]):
        minimum_risk_graph = min(suitable_graphs, key=lambda graph: graph.risk)
        minimum_risk_graph.append(cell)

    def _print_result(self):
        # list is guaranteed to be of length 1 (== only one graph holds the destination)
        graph = [graph for graph in self.graphs if self.grid.destination in graph][0]
        result = graph.combine_parts()
        print(result)
        print()
        print(result.pretty_repr)


class Graph:
    def __init__(
        self,
        elements: list[Cell],
        *,
        extends_graph: Graph | None = None,
        at_idx: int | None = None,
    ):
        assert (extends_graph is None and at_idx is None) or (
            extends_graph is not None and at_idx is not None
        )

        self.elements = elements
        self.extends_graph = extends_graph
        self.at_idx = at_idx

        assert self._is_contiguous

    @property
    def _is_contiguous(self) -> bool:
        if len(self.elements) in [0, 1]:
            return True

        is_contiguous_inner = all(
            map(
                lambda e: e[0].position in e[1].position.neighbours,
                zip(self.elements[:-1], self.elements[1:]),
            )
        )

        if self.extends_graph is None:
            return is_contiguous_inner

        assert self.extends_graph is not None and self.at_idx is not None

        is_contiguous_outer = (
            self.extends_graph[self.at_idx].position
            in self.elements[0].position.neighbours
        )

        return is_contiguous_inner and is_contiguous_outer

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
        rows, min_x, min_y = self._get_empty_board_representation(self.elements)
        for cell in self.elements:
            rows[cell.position.x - min_x][cell.position.y - min_y] = str(cell.value)
        result = "\n".join(["".join(row) for row in rows])
        return result

    @staticmethod
    def _get_empty_board_representation(
        elements: list[Cell],
    ) -> tuple[list[list[str]], int, int]:
        def generate_row():
            return [" "] * len_x

        positions = [cell.position for cell in elements]
        xs = [pos.x for pos in positions]
        ys = [pos.y for pos in positions]
        min_x = min(xs)
        min_y = min(ys)
        max_x = max(xs)
        len_x = max_x - min_x + 1
        rows = [generate_row() for _ in range(len_x)]
        return rows, min_x, min_y

    @overload
    def __getitem__(self, item: int) -> Cell:
        pass

    @overload
    def __getitem__(self, item: slice) -> list[Cell]:
        pass

    def __getitem__(self, item: int | slice) -> Cell | list[Cell]:
        return self.elements[item]

    def append(self, cell: Cell):
        self.elements.append(cell)

    def __len__(self):
        return len(self.elements)

    @property
    def risk(self) -> int:
        return self.risk_up_to_index(len(self))

    def risk_up_to_index(self, idx: int | None = None) -> int:
        if idx is None:
            idx = len(self)
        own_risk = sum([cell.value for cell in self.elements[:idx+1]])

        if self.extends_graph is None:
            return own_risk - self._start_cell_risk

        extended_graph_risk = self.extends_graph.risk_up_to_index(self.at_idx)
        return own_risk + extended_graph_risk

    @property
    def _start_cell_risk(self) -> int:
        return self.elements[0].value

    @property
    def last_cell(self) -> Cell:
        return self.elements[-1]

    @classmethod
    def from_grid(cls, grid: Grid) -> Graph:
        return cls([grid[grid.start]], extends_graph=None, at_idx=None)

    def can_extend_to_cell(self, cell: Cell) -> bool:
        return cell.position in self.last_cell.position.neighbours

    def contains_neighbour_of_cell(self, cell: Cell) -> bool:
        return any([neighbour in self for neighbour in cell.position.neighbours])

    def find_best_cell_to_start_new_graph(self, cell: Cell) -> int:
        for i, element in enumerate(self.elements):
            if cell.position in element.position.neighbours:
                return i
        raise ValueError("Could not find a place to start a new graph.")

    def combine_parts(self, *, max_index: int | None = None) -> Graph:
        if max_index is None:
            max_index = len(self)
        own_elements = self.elements[: max_index + 1]
        if self.extends_graph:
            subgraph = self.extends_graph.combine_parts(max_index=self.at_idx)
            return Graph(
                subgraph.elements + own_elements,
                extends_graph=None,
                at_idx=None,
            )
        else:
            return Graph(own_elements, extends_graph=None, at_idx=None)


def main():
    grid = Grid.from_file("testdata.txt")
    astar = AStar(grid)
    astar.solve()


if __name__ == "__main__":
    main()
