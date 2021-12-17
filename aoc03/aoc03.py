import numpy as np


def to_chars(line):
    return [char for char in line]


def complement(bin_str):
    return "".join(["0" if char == "1" else "1" for char in bin_str])


def part_one(matrix):
    col_sums = np.sum(matrix, axis=0)
    threshold = matrix.shape[0] // 2
    gamma_str = "".join(["1" if col_sum >= threshold else "0" for col_sum in col_sums])
    gamma = int(gamma_str, 2)
    epsilon = int(complement(gamma_str), 2)
    print(f"power: {gamma * epsilon}")


def recursive(x, pos=0, condition=None):
    def get_line_idxs(value):
        return np.asarray([i for i in range(x.shape[0]) if x[i, pos] == value])

    if x.shape[0] == 1:
        return "".join(map(str, x[0, :]))
    value = np.sum(x[:, pos])
    threshold = x.shape[0] / 2
    if condition(value, threshold):
        line_idxs = get_line_idxs(1)
    else:
        line_idxs = get_line_idxs(0)
    return recursive(x[line_idxs, :], pos + 1, condition)


def condition_oxygen(value, threshold):
    return value >= threshold


def condition_co2(value, threshold):
    return value < threshold


def part_two(matrix):
    oxygen = int(recursive(matrix, condition=condition_oxygen), 2)
    co2 = int(recursive(matrix, condition=condition_co2), 2)
    print(f"life support: {oxygen*co2}")


with open("data.txt") as fd:
    data = fd.read()

x = list(map(to_chars, data.split()))
matrix = np.asarray(x, dtype=int)
part_one(matrix)
part_two(matrix)
