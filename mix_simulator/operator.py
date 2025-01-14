from __future__ import annotations
from enum import StrEnum
from typing import Tuple


class Operator(StrEnum):
    """Tells the simulator which operation to perform.

    This is a combination of the op code and field (op variant) bytes of an instruction.
    """

    # NOP (0)
    NOP = "NOP"  # no operation

    # Arithmetic Operators (C 1-4)
    ADD = "ADD"  # add
    SUB = "SUB"  # subtract
    MUL = "MUL"  # multiply
    DIV = "DIV"  # divide

    # Conversion Operators (C 5)
    # Depends on the F (op variant) value: 0 = NUM, 1 = CHAR, 2 = HALT
    NUM = "NUM"
    CHAR = "CHAR"
    HLT = "HLT"

    # Miscellaneous Operators (C 6-7)
    # SH depends on the F (op variant) value:
    # 0 = SLA, 1 = SRA, 2 = SLAX, 3 = SRAX, 4 = SLC, 5 = SRC
    SLA = "SLA"  # shift A left
    SRA = "SRA"  # shift A right
    SLAX = "SLAX"  # shift AX left
    SRAX = "SRAX"  # shift AX right
    SLC = "SLC"  # circular shift AX left
    SRC = "SRC"  # circular shift AX right
    MOVE = "MOVE"  # move

    # Loading Operators (C 8-23)
    LDA = "LDA"  # load A
    LD1 = "LD1"  # load I1
    LD2 = "LD2"  # load I2
    LD3 = "LD3"  # load I3
    LD4 = "LD4"  # load I4
    LD5 = "LD5"  # load I5
    LD6 = "LD6"  # load I6
    LDX = "LDX"  # load X
    LDAN = "LDAN"  # load A negative
    LD1N = "LD1N"  # load I1 negative
    LD2N = "LD2N"  # load I2 negative
    LD3N = "LD3N"  # load I3 negative
    LD4N = "LD4N"  # load I4 negative
    LD5N = "LD5N"  # load I5 negative
    LD6N = "LD6N"  # load I6 negative
    LDXN = "LDXN"  # load X negative

    # Storing Operators (C 24-33)
    STA = "STA"  # store A
    ST1 = "ST1"  # store I1
    ST2 = "ST2"  # store I2
    ST3 = "ST3"  # store I3
    ST4 = "ST4"  # store I4
    ST5 = "ST5"  # store I5
    ST6 = "ST6"  # store I6
    STX = "STX"  # store X
    STJ = "STJ"  # store J
    STZ = "STZ"  # store 0

    # Input-output Operators (34-38)
    JBUS = "JBUS"  # unit f busy?
    IOC = "IOC"  # control, unit f
    IN = "IN"  # input, unit f
    OUT = "OUT"  # output, unit f
    JRED = "JRED"  # unit f ready?

    # Jump Operators (C 39-47)
    # JMP depends on the F (op variant) value:
    # 0 = JMP, 1 = JSJ, 2 = JOV, 3 = JNOV, 4 = JL, 5 = JE, 6 = JG, 7 = JGE, 8 = JNE, 9 = JLE
    JMP = "JMP"  # jump
    JSJ = "JSJ"  # jump, save jump
    JOV = "JOV"  # jump on overflow
    JNOV = "JNOV"  # jump on no overflow
    JL = "JL"  # jump less
    JE = "JE"  # jump equal
    JG = "JG"  # jump greater
    JGE = "JGE"  # jump greater equal
    JNE = "JNE"  # jump not equal
    JLE = "JLE"  # jump less equal

    # Register based jumps (J*) also depend on the F (op variant) value:
    # 0 = J*N, 1 = J*Z, 2 = J*P, 3 = J*NN, 4 = J*NZ, 5 = J*NP
    JAN = "JAN"  # jump A negative
    JAZ = "JAZ"  # jump A zero
    JAP = "JAP"  # jump A postive
    JANN = "JANN"  # jump A not negative
    JANZ = "JANZ"  # jump A not zero
    JANP = "JANP"  # jump A not positive

    J1N = "J1N"  # jump I1 negative
    J1Z = "J1Z"  # jump I1 zero
    J1P = "J1P"  # jump I1 postive
    J1NN = "J1NN"  # jump I1 not negative
    J1NZ = "J1NZ"  # jump I1 not zero
    J1NP = "J1NP"  # jump I1 not positive

    J2N = "J2N"  # jump I2 negative
    J2Z = "J2Z"  # jump I2 zero
    J2P = "J2P"  # jump I2 postive
    J2NN = "J2NN"  # jump I2 not negative
    J2NZ = "J2NZ"  # jump I2 not zero
    J2NP = "J2NP"  # jump I2 not positive

    J3N = "J3N"  # jump I3 negative
    J3Z = "J3Z"  # jump I3 zero
    J3P = "J3P"  # jump I3 postive
    J3NN = "J3NN"  # jump I3 not negative
    J3NZ = "J3NZ"  # jump I3 not zero
    J3NP = "J3NP"  # jump I3 not positive

    J4N = "J4N"  # jump I4 negative
    J4Z = "J4Z"  # jump I4 zero
    J4P = "J4P"  # jump I4 postive
    J4NN = "J4NN"  # jump I4 not negative
    J4NZ = "J4NZ"  # jump I4 not zero
    J4NP = "J4NP"  # jump I4 not positive

    J5N = "J5N"  # jump I5 negative
    J5Z = "J5Z"  # jump I5 zero
    J5P = "J5P"  # jump I5 postive
    J5NN = "J5NN"  # jump I5 not negative
    J5NZ = "J5NZ"  # jump I5 not zero
    J5NP = "J5NP"  # jump I5 not positive

    J6N = "J6N"  # jump I6 negative
    J6Z = "J6Z"  # jump I6 zero
    J6P = "J6P"  # jump I6 postive
    J6NN = "J6NN"  # jump I6 not negative
    J6NZ = "J6NZ"  # jump I6 not zero
    J6NP = "J6NP"  # jump I6 not positive

    JXN = "JXN"  # jump X negative
    JXZ = "JXZ"  # jump X zero
    JXP = "JXP"  # jump X postive
    JXNN = "JXNN"  # jump X not negative
    JXNZ = "JXNZ"  # jump X not zero
    JXNP = "JXNP"  # jump X not positive

    # Address Transfer Operators (C 48-55)
    # These depend on the F (op variant) value: 0 = INC, 1 = DEC, 2 = ENT, 3 = ENN
    # AT{R} is used as the "generic name" where R identifies the relevant register
    INCA = "INCA"  # increment A
    DECA = "DECA"  # decrement A
    ENTA = "ENTA"  # enter A
    ENNA = "ENNA"  # enter negative A

    INC1 = "INC1"  # increment I1
    DEC1 = "DEC1"  # decrement I1
    ENT1 = "ENT1"  # enter I1
    ENN1 = "ENN1"  # enter negative I1

    INC2 = "INC2"  # increment I2
    DEC2 = "DEC2"  # decrement I2
    ENT2 = "ENT2"  # enter I2
    ENN2 = "ENN2"  # enter negative I2

    INC3 = "INC3"  # increment I3
    DEC3 = "DEC3"  # decrement I3
    ENT3 = "ENT3"  # enter I3
    ENN3 = "ENN3"  # enter negative I3

    INC4 = "INC4"  # increment I4
    DEC4 = "DEC4"  # decrement I4
    ENT4 = "ENT4"  # enter I4
    ENN4 = "ENN4"  # enter negative I4

    INC5 = "INC5"  # increment I5
    DEC5 = "DEC5"  # decrement I5
    ENT5 = "ENT5"  # enter I5
    ENN5 = "ENN5"  # enter negative I5

    INC6 = "INC6"  # increment I6
    DEC6 = "DEC6"  # decrement I6
    ENT6 = "ENT6"  # enter I6
    ENN6 = "ENN6"  # enter negative I6

    INCX = "INCX"  # increment X
    DECX = "DECX"  # decrement X
    ENTX = "ENTX"  # enter X
    ENNX = "ENNX"  # enter negative X

    # Comparison Operators (C 56-63)
    CMPA = "CMPA"  # compare A
    CMP1 = "CMP1"  # compare I1
    CMP2 = "CMP2"  # compare I2
    CMP3 = "CMP3"  # compare I3
    CMP4 = "CMP4"  # compare I4
    CMP5 = "CMP5"  # compare I5
    CMP6 = "CMP6"  # compare I6
    CMPX = "CMPX"  # compare X

    def to_code_and_field(self) -> Tuple[int, int]:
        return {
            "NOP": (0, 0),
            "ADD": (1, 5),
            "SUB": (2, 5),
            "MUL": (3, 5),
            "DIV": (4, 5),
            "NUM": (5, 0),
            "CHAR": (5, 1),
            "HLT": (5, 2),
            "SLA": (6, 0),
            "SRA": (6, 1),
            "SLAX": (6, 2),
            "SRAX": (6, 3),
            "SLC": (6, 4),
            "SRC": (6, 5),
            "MOVE": (7, 0),
            "LDA": (8, 5),
            "LD1": (9, 5),
            "LD2": (10, 5),
            "LD3": (11, 5),
            "LD4": (12, 5),
            "LD5": (13, 5),
            "LD6": (14, 5),
            "LDX": (15, 5),
            "LDAN": (16, 5),
            "LD1N": (17, 5),
            "LD2N": (18, 5),
            "LD3N": (19, 5),
            "LD4N": (20, 5),
            "LD5N": (21, 5),
            "LD6N": (22, 5),
            "LDXN": (23, 5),
            "STA": (24, 5),
            "ST1": (25, 5),
            "ST2": (26, 5),
            "ST3": (27, 5),
            "ST4": (28, 5),
            "ST5": (29, 5),
            "ST6": (30, 5),
            "STX": (31, 5),
            "STJ": (32, 2),
            "STZ": (33, 5),
            "JBUS": (34, 0),
            "IOC": (35, 0),
            "IN": (36, 0),
            "OUT": (37, 0),
            "JRED": (38, 0),
            "JMP": (39, 0),
            "JSJ": (39, 1),
            "JOV": (39, 2),
            "JNOV": (39, 3),
            "JL": (39, 4),
            "JE": (39, 5),
            "JG": (39, 6),
            "JGE": (39, 7),
            "JNE": (39, 8),
            "JLE": (39, 9),
            "JAN": (40, 0),
            "JAZ": (40, 1),
            "JAP": (40, 2),
            "JANN": (40, 3),
            "JANZ": (40, 4),
            "JANP": (40, 5),
            "J1N": (41, 0),
            "J1Z": (41, 1),
            "J1P": (41, 2),
            "J1NN": (41, 3),
            "J1NZ": (41, 4),
            "J1NP": (41, 5),
            "J2N": (42, 0),
            "J2Z": (42, 1),
            "J2P": (42, 2),
            "J2NN": (42, 3),
            "J2NZ": (42, 4),
            "J2NP": (42, 5),
            "J3N": (43, 0),
            "J3Z": (43, 1),
            "J3P": (43, 2),
            "J3NN": (43, 3),
            "J3NZ": (43, 4),
            "J3NP": (43, 5),
            "J4N": (44, 0),
            "J4Z": (44, 1),
            "J4P": (44, 2),
            "J4NN": (44, 3),
            "J4NZ": (44, 4),
            "J4NP": (44, 5),
            "J5N": (45, 0),
            "J5Z": (45, 1),
            "J5P": (45, 2),
            "J5NN": (45, 3),
            "J5NZ": (45, 4),
            "J5NP": (45, 5),
            "J6N": (46, 0),
            "J6Z": (46, 1),
            "J6P": (46, 2),
            "J6NN": (46, 3),
            "J6NZ": (46, 4),
            "J6NP": (46, 5),
            "JXN": (47, 0),
            "JXZ": (47, 1),
            "JXP": (47, 2),
            "JXNN": (47, 3),
            "JXNZ": (47, 4),
            "JXNP": (47, 5),
            "INCA": (48, 0),
            "DECA": (48, 1),
            "ENTA": (48, 2),
            "ENNA": (48, 3),
            "INC1": (49, 0),
            "DEC1": (49, 1),
            "ENT1": (49, 2),
            "ENN1": (49, 3),
            "INC2": (50, 0),
            "DEC2": (50, 1),
            "ENT2": (50, 2),
            "ENN2": (50, 3),
            "INC3": (51, 0),
            "DEC3": (51, 1),
            "ENT3": (51, 2),
            "ENN3": (51, 3),
            "INC4": (52, 0),
            "DEC4": (52, 1),
            "ENT4": (52, 2),
            "ENN4": (52, 3),
            "INC5": (53, 0),
            "DEC5": (53, 1),
            "ENT5": (53, 2),
            "ENN5": (53, 3),
            "INC6": (54, 0),
            "DEC6": (54, 1),
            "ENT6": (54, 2),
            "ENN6": (54, 3),
            "INCX": (55, 0),
            "DECX": (55, 1),
            "ENTX": (55, 2),
            "ENNX": (55, 3),
            "CMPA": (56, 5),
            "CMP1": (57, 5),
            "CMP2": (58, 5),
            "CMP3": (59, 5),
            "CMP4": (60, 5),
            "CMP5": (61, 5),
            "CMP6": (62, 5),
            "CMPX": (63, 5),
        }[self.name]

    @staticmethod
    def from_code_and_field(code: int, field: int) -> Operator:
        opname = {
            (0, 0): "NOP",
            (1, 5): "ADD",
            (2, 5): "SUB",
            (3, 5): "MUL",
            (4, 5): "DIV",
            (5, 0): "NUM",
            (5, 1): "CHAR",
            (5, 2): "HLT",
            (6, 0): "SLA",
            (6, 1): "SRA",
            (6, 2): "SLAX",
            (6, 3): "SRAX",
            (6, 4): "SLC",
            (6, 5): "SRC",
            (7, 0): "MOVE",
            (8, 5): "LDA",
            (9, 5): "LD1",
            (10, 5): "LD2",
            (11, 5): "LD3",
            (12, 5): "LD4",
            (13, 5): "LD5",
            (14, 5): "LD6",
            (15, 5): "LDX",
            (16, 5): "LDAN",
            (17, 5): "LD1N",
            (18, 5): "LD2N",
            (19, 5): "LD3N",
            (20, 5): "LD4N",
            (21, 5): "LD5N",
            (22, 5): "LD6N",
            (23, 5): "LDXN",
            (24, 5): "STA",
            (25, 5): "ST1",
            (26, 5): "ST2",
            (27, 5): "ST3",
            (28, 5): "ST4",
            (29, 5): "ST5",
            (30, 5): "ST6",
            (31, 5): "STX",
            (32, 2): "STJ",
            (33, 5): "STZ",
            (34, 0): "JBUS",
            (35, 0): "IOC",
            (36, 0): "IN",
            (37, 0): "OUT",
            (38, 0): "JRED",
            (39, 0): "JMP",
            (39, 1): "JSJ",
            (39, 2): "JOV",
            (39, 3): "JNOV",
            (39, 4): "JL",
            (39, 5): "JE",
            (39, 6): "JG",
            (39, 7): "JGE",
            (39, 8): "JNE",
            (39, 9): "JLE",
            (40, 0): "JAN",
            (40, 1): "JAZ",
            (40, 2): "JAP",
            (40, 3): "JANN",
            (40, 4): "JANZ",
            (40, 5): "JANP",
            (41, 0): "J1N",
            (41, 1): "J1Z",
            (41, 2): "J1P",
            (41, 3): "J1NN",
            (41, 4): "J1NZ",
            (41, 5): "J1NP",
            (42, 0): "J2N",
            (42, 1): "J2Z",
            (42, 2): "J2P",
            (42, 3): "J2NN",
            (42, 4): "J2NZ",
            (42, 5): "J2NP",
            (43, 0): "J3N",
            (43, 1): "J3Z",
            (43, 2): "J3P",
            (43, 3): "J3NN",
            (43, 4): "J3NZ",
            (43, 5): "J3NP",
            (44, 0): "J4N",
            (44, 1): "J4Z",
            (44, 2): "J4P",
            (44, 3): "J4NN",
            (44, 4): "J4NZ",
            (44, 5): "J4NP",
            (45, 0): "J5N",
            (45, 1): "J5Z",
            (45, 2): "J5P",
            (45, 3): "J5NN",
            (45, 4): "J5NZ",
            (45, 5): "J5NP",
            (46, 0): "J6N",
            (46, 1): "J6Z",
            (46, 2): "J6P",
            (46, 3): "J6NN",
            (46, 4): "J6NZ",
            (46, 5): "J6NP",
            (47, 0): "JXN",
            (47, 1): "JXZ",
            (47, 2): "JXP",
            (47, 3): "JXNN",
            (47, 4): "JXNZ",
            (47, 5): "JXNP",
            (48, 0): "INCA",
            (48, 1): "DECA",
            (48, 2): "ENTA",
            (48, 3): "ENNA",
            (49, 0): "INC1",
            (49, 1): "DEC1",
            (49, 2): "ENT1",
            (49, 3): "ENN1",
            (50, 0): "INC2",
            (50, 1): "DEC2",
            (50, 2): "ENT2",
            (50, 3): "ENN2",
            (51, 0): "INC3",
            (51, 1): "DEC3",
            (51, 2): "ENT3",
            (51, 3): "ENN3",
            (52, 0): "INC4",
            (52, 1): "DEC4",
            (52, 2): "ENT4",
            (52, 3): "ENN4",
            (53, 0): "INC5",
            (53, 1): "DEC5",
            (53, 2): "ENT5",
            (53, 3): "ENN5",
            (54, 0): "INC6",
            (54, 1): "DEC6",
            (54, 2): "ENT6",
            (54, 3): "ENN6",
            (55, 0): "INCX",
            (55, 1): "DECX",
            (55, 2): "ENTX",
            (55, 3): "ENNX",
            (56, 5): "CMPA",
            (57, 5): "CMP1",
            (58, 5): "CMP2",
            (59, 5): "CMP3",
            (60, 5): "CMP4",
            (61, 5): "CMP5",
            (62, 5): "CMP6",
            (63, 5): "CMPX",
        }[(code, field)]

        return Operator(opname)
