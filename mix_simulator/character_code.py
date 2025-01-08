from mix_simulator.byte import Byte


alphabet = " ABCDEFGHI" "ΔJKLMNOPQR" "ΣΠSTUVWXYZ" "0123456789" ".,()+-*/=$" "<>@;:'"
lookup = {c: i for (i, c) in enumerate(alphabet)}


def byte_to_char(b: Byte) -> str:
    return alphabet[b.val]


def char_to_byte(c: str) -> Byte:
    return Byte(lookup[c])
