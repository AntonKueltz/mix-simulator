from enum import IntEnum


class OpCode(IntEnum):
    """Tells the simulator which operation to perform."""

    NOP = 0  # no operation

    # Arithmetic Operators
    ADD = 1  # add
    SUB = 2  # subtract
    MUL = 3  # multiply
    DIV = 4  # divide

    # Miscellaneous Operators
    # These depend on the F (op variant) value:
    # 0 = SLA, 1 = SRA, 2 = SLAX, 3 = SRAX, 4 = SLC, 5 = SRC
    SH = 5  # shift

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

    # Jump Operators
    # Depends on the F (op variant) value:
    # 0 = JMP, 1 = JSJ, 2 = JOV, 3 = JNOV, 4 = JL, 5 = JE, 6 = JG, 7 = JGE, 8 = JNE, 9 = JLE
    JMP = 39  # jump
    # Register based jumps also depend on the F (op variant) value:
    # 0 = J*N, 1 = J*Z, 2 = J*P, 3 = J*NN, 4 = J*NZ, 5 = J*NP
    JA = 40  # jump A
    J1 = 41  # jump I1
    J2 = 42  # jump I2
    J3 = 43  # jump I3
    J4 = 44  # jump I4
    J5 = 45  # jump I5
    J6 = 46  # jump I6
    JX = 47  # jump X

    # Address Transfer Operators
    # These depend on the F (op variant) value: 0 = INC, 1 = DEC, 2 = ENT, 3 = ENN
    # AT{R} is used as the "generic name" where R identifies the relevant register
    ATA = 48  # address transfer A
    AT1 = 49  # address transfer I1
    AT2 = 50  # address transfer I2
    AT3 = 51  # address transfer I3
    AT4 = 52  # address transfer I4
    AT5 = 53  # address transfer I5
    AT6 = 54  # address transfer I6
    ATX = 55  # address transfer X

    # Comparison Operators
    CMPA = 56  # compare A
    CMP1 = 57  # compare I1
    CMP2 = 58  # compare I2
    CMP3 = 59  # compare I3
    CMP4 = 60  # compare I4
    CMP5 = 61  # compare I5
    CMP6 = 62  # compare I6
    CMPX = 63  # compare X
