from mix_simulator.byte import Byte
from mix_simulator.word import Word


class Memory:
    """4000 (default) words of storage, each word with five bytes and a sign."""

    def __init__(self, words: int = 4000) -> None:
        self.words = words
        self.cells = [
            Word(sign=False, b1=Byte(0), b2=Byte(0), b3=Byte(0), b4=Byte(0), b5=Byte(0))
            for _ in range(words)
        ]

    def __getitem__(self, cell: int) -> Word:
        if cell >= self.words:
            raise IndexError(
                f"Index {cell} is larger than max memory index {self.words-1}"
            )

        return self.cells[cell]

    def __setitem__(self, cell: int, word: Word) -> None:
        if cell >= self.words:
            raise IndexError(
                f"Index {cell} is larger than max memory index {self.words-1}"
            )

        self.cells[cell] = word
