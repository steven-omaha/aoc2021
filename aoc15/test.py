import pytest
from aoc15 import Cell, Graph, Position


class TestGraph:
    def test_contiguous_single_graph(self):
        cell0 = Cell(Position(0, 0), 1)
        cell1 = Cell(Position(0, 1), 1)
        Graph([cell0, cell1])

        cell2 = Cell(Position(0, 2), 1)
        with pytest.raises(AssertionError):
            Graph([cell0, cell2])

    def test_contiguous_multiple_graphs(self):
        cell00 = Cell(Position(0, 0), 1)
        cell01 = Cell(Position(0, 1), 1)
        graph0 = Graph([cell00, cell01])

        cell10 = Cell(Position(1, 0), 1)
        cell20 = Cell(Position(2, 0), 1)
        Graph([cell10, cell20], extends_graph=graph0, at_idx=0)

        cell30 = Cell(Position(3, 0), 1)
        with pytest.raises(AssertionError):
            Graph([cell20, cell30], extends_graph=graph0, at_idx=0)


class TestPosition:
    def test_neighbours(self):
        pos = Position(1, 1)
        assert Position(1, 0) in pos.neighbours
        assert Position(1, 2) in pos.neighbours
        assert Position(0, 1) in pos.neighbours
        assert Position(2, 1) in pos.neighbours
        assert Position(1, 1) not in pos.neighbours
        assert Position(0, 0) not in pos.neighbours
        assert Position(2, 0) not in pos.neighbours
        assert Position(2, 2) not in pos.neighbours
        assert Position(0, 2) not in pos.neighbours
