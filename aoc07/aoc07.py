from __future__ import annotations

from functools import cache

import sys

sys.setrecursionlimit(3000)


def element_sub(array: list[int], value: int) -> list[int]:
    return [element - value for element in array]


def element_abs(x: list[int]) -> list[int]:
    return [abs(y) for y in x]


def fuel(positions: list[int], center: int) -> int:
    return int(sum(element_abs(element_sub(positions, center))))


def fuel2(positions: list[int], center: int) -> int:
    absolutes = element_abs(element_sub(positions, center))
    multiplied = [sum_recursive(value) for value in absolutes]
    return int(sum(multiplied))


@cache
def sum_recursive(number: int) -> int:
    if number == 0:
        return 0
    return number + sum_recursive(number - 1)


def optimise(positions: list[int]) -> None:
    positions_to_check = list(range(min(positions), max(positions) + 1))
    fuel_array = len(positions_to_check) * [0]

    for i, center in enumerate(positions_to_check):
        fuel_array[i] = fuel(positions, center)
    minimum = min(fuel_array)
    optimum_idx = [
        idx for idx in range(len(positions_to_check)) if fuel_array[idx] == minimum
    ][0]
    print(
        f"Position: {positions_to_check[optimum_idx]}, Fuel: {fuel_array[optimum_idx]}"
    )


def optimise2(positions: list[int]) -> None:
    positions_to_check = list(range(min(positions), max(positions) + 1))
    fuel_array = len(positions_to_check) * [0]

    for i, center in enumerate(positions_to_check):
        fuel_array[i] = fuel2(positions, center)
    minimum = min(fuel_array)
    optimum_idx = [
        idx for idx in range(len(positions_to_check)) if fuel_array[idx] == minimum
    ][0]
    print(
        f"Position: {positions_to_check[optimum_idx]}, Fuel: {fuel_array[optimum_idx]}"
    )


def loadfile(filename: str) -> list[int]:
    with open(filename) as fd:
        content = fd.read()
    return [int(item) for item in content.split(",")]


positions = loadfile("data.txt")
optimise(positions)
optimise2(positions)
