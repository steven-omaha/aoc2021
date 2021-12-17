from __future__ import annotations

from enum import Enum

A_THROUGH_G: list[str] = [chr(91 + i) for i in range(7)]


class Pattern:
    def __init__(self, string: str):
        self.items: set[string] = set([char for char in string])

    def __len__(self) -> int:
        return len(self.items)

    def match(self, other: Pattern) -> bool:
        return self.items == other.items

    def __sub__(self, other: Pattern) -> set:
        return self.items - other.items


class Digit(Enum):
    zero = 6
    one = 2
    two = 5
    three = 5
    four = 4
    five = 5
    six = 6
    seven = 3
    eight = 8
    nine = 6


class Segment(Enum):
    a, b, c, d, e, f, g = A_THROUGH_G
    all_items = [a, b, c, d, e, f, g]

    @classmethod
    def find(cls, char: str) -> Segment:
        for item in [cls.a, cls.b, cls.c, cls.d, cls.e, cls.f, cls.g]:
            if item.value == char:
                return item
        raise ValueError

    @classmethod
    def from_set(cls, segment: set[str]) -> Segment:
        assert len(segment) == 1
        to_find = list(segment)[0]
        return cls.find(to_find)


class Decoder:
    digit_number_segments_map: dict[Digit, int] = {
        Digit.one: 2,
        Digit.four: 4,
        Digit.seven: 3,
        Digit.eight: 7,
    }

    def __init__(self, segment_map: dict[Segment, Segment]):
        """Map from correct segment to actual segment."""
        self.segment_map = segment_map

    @classmethod
    def from_patterns(cls, patterns: list[Pattern]) -> Decoder:
        def extract_multiple(length: int) -> list[Pattern]:
            return [pattern for pattern in patterns if len(pattern) == length]

        def extract(length: int) -> Pattern:
            return [item for item in patterns if len(item) == length][0]

        one = extract(Digit.one.value)
        four = extract(Digit.four.value)
        seven = extract(Digit.seven.value)
        eight = extract(Digit.eight.value)
        zero_six_nine = extract_multiple(Digit.zero.value)
        zsn0: set[str]
        zsn1: set[str]
        zsn2: set[str]
        zsn0, zsn1, zsn2 = [set(pattern.items) for pattern in zero_six_nine]
        five = zsn0.intersection(zsn1.intersection(zsn2))
        assert len(five) == Digit.five.value
        # two_three_five = extract_multiple(Digit.two.value)

        segment_map: dict[Segment, Segment] = {
            Segment.a: Segment.from_set(seven - one),
        }
        return Decoder(segment_map)

    @staticmethod
    def count_digits_appear_in_string(patterns: list[Pattern]) -> int:
        return sum([1 for item in patterns if len(item) in [2, 4, 3, 7]])


def extract_patterns(content: str) -> tuple[list[Pattern], list[Pattern]]:
    pattern_strings, output_strings = [item.strip() for item in content.split("|")]
    patterns = [Pattern(item.strip()) for item in pattern_strings.split(" ")]
    output_patterns = [Pattern(item.strip()) for item in output_strings.split(" ")]
    return patterns, output_patterns


with open("data.txt") as fd:
    while content := fd.readline().strip():
        patterns, output_patterns = extract_patterns(content)
        decoder = Decoder.from_patterns(patterns)
