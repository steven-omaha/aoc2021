import numpy as np


class Draws:
    def __init__(self, data: list[int]):
        self.data = data
        self._next_draw_index = 0

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self):
        current_number = str(self.data[self._next_draw_index])
        draw_line = ", ".join([str(item) for item in self.data]) + "\n"
        index = draw_line.find(current_number)
        number_spaces = index + len(current_number) - 1
        arrow_line_1 = " " * number_spaces + "^\n"
        arrow_line_2 = " " * number_spaces + "|"
        return draw_line + arrow_line_1 + arrow_line_2

    def next(self) -> int:
        result = self.data[self._next_draw_index]
        self._next_draw_index += 1
        return result


class Field:
    def __init__(self, data: list[list[int]]):
        self._data = np.asarray(data)
        self._active = -np.ones_like(self._data, dtype=int)

    def __repr__(self):
        format_string = " ".join(5 * ["{:>2}"])
        lines = [format_string.format(*line) for line in self._data]
        return "\n".join(lines)

    @property
    def marked_fields(self) -> str:
        format_string = " ".join(5 * ["{:>2}"])
        lines = [format_string.format(*line) for line in self._active]
        return "\n".join(lines).replace("-1", " .")

    def mark(self, value: int) -> None:
        try:
            idxs = np.argwhere(self._data == value)[0]
        except IndexError:
            return
        self._active[idxs[0], idxs[1]] = value

    @property
    def has_won(self) -> bool:
        for row in self._active:
            if -1 not in row:
                return True
        for column in self._active.T:
            if -1 not in column:
                return True
        return False

    @property
    def board_sum(self) -> int:
        return np.sum(self._data) - np.sum(self._active)


def load_data(filename):
    fields = []
    with open(filename) as fd:
        draws = [int(item) for item in fd.readline().strip().split(",")]
        while _ := fd.readline():
            lines = []
            for _ in range(5):
                lines.append(
                    [
                        int(item)
                        for item in fd.readline().strip().split(" ")
                        if item != ""
                    ]
                )
            fields.append(lines)

    return Draws(draws), [Field(field) for field in fields]


def get_winner(draws, fields):
    for i in range(len(draws)):
        print(f"turn: {i}")
        new_fields = []
        value = draws.next()
        print(f"value: {value}")
        for field in fields:
            field.mark(value)
            if not field.has_won:
                new_fields.append(field)
        print(len(new_fields))
        if len(new_fields) == 1:
            return value * new_fields[0].board_sum
        fields = new_fields


def iterate(draws, fields):
    field = fields[0]
    for i in range(len(draws)):
        value = draws.next()
        print(value)
        field.mark(value)
        print(field.marked_fields)
        print()
        input()


draws, fields = load_data("testdata.txt")
print(get_winner(draws, fields))
