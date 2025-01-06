from enum import IntEnum


class OpCode(IntEnum):
    """Tells the simulator which operation to perform."""

    # Arithmetic Operators
    ADD = 1  # add
    SUB = 2  # subtract
    MUL = 3  # multiply
    DIV = 4  # divide

    # Loading Operators
    LDA = 8  # load A
    LD1 = 9  # load I1
    LD2 = 10  # load I2
    LD3 = 11  # load I3
    LD4 = 12  # load I4
    LD5 = 13  # load I5
    LD6 = 14  # load I6
    LDX = 15  # load X
    LDAN = 16  # load A negative
    LD1N = 17  # load I1 negative
    LD2N = 18  # load I2 negative
    LD3N = 19  # load I3 negative
    LD4N = 20  # load I4 negative
    LD5N = 21  # load I5 negative
    LD6N = 22  # load I6 negative
    LDXN = 23  # load X negative

    # Storing Operators
    STA = 24  # store A
    ST1 = 25  # store I1
    ST2 = 26  # store I2
    ST3 = 27  # store I3
    ST4 = 28  # store I4
    ST5 = 29  # store I5
    ST6 = 30  # store I6
    STX = 31  # store X
    STJ = 32  # store J
    STZ = 33  # store 0
