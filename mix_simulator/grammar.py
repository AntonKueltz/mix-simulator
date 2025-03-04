"""
MIXAL as a context-free grammer G. The language of G is simplified
to a regular language by removing the recursive definitions of
<EXPR> and <W-VALUE>. This removes a little bit of flexibility, but
makes the language easier to parse by allowing regular expressions
to parse programs written in MIXAL.

<DIGIT>         -> 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
<LETTER>        -> A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T | U | V | W | X | Y | Z
<SPACE>         -> " " | "\t"
<SIGN>          -> + | -
<BINARY-OP>     -> + | - | * | / | // | :
<LOC-COUNTER>   -> *
<MIX-OP>        -> NOP | ADD | SUB | MUL | DIV | NUM | CHAR | HLT | SLA | SRA | SLAX | SRAX | SLC | SRC | MOVE | LDA | LD1 | LD2 | LD3 | LD4 | LD5 | LD6 | LDX | LDAN | LD1N | LD2N | LD3N | LD4N | LD5N | LD6N | LDXN | STA | ST1 | ST2 | ST3 | ST4 | ST5 | ST6 | STX | STJ | STZ | JBUS | IOC | IN | OUT | JRED | JMP | JSJ | JOV | JNOV | JL | JE | JG | JGE | JNE | JLE | JAN | JAZ | JAP | JANN | JANZ | JANP | J1N | J1Z | J1P | J1NN | J1NZ | J1NP | J2N | J2Z | J2P | J2NN | J2NZ | J2NP | J3N | J3Z | J3P | J3NN | J3NZ | J3NP | J4N | J4Z | J4P | J4NN | J4NZ | J4NP | J5N | J5Z | J5P | J5NN | J5NZ | J5NP | J6N | J6Z | J6P | J6NN | J6NZ | J6NP | JXN | JXZ | JXP | JXNN | JXNZ | JXNP | INCA | DECA | ENTA | ENNA | INC1 | DEC1 | ENT1 | ENN1 | INC2 | DEC2 | ENT2 | ENN2 | INC3 | DEC3 | ENT3 | ENN3 | INC4 | DEC4 | ENT4 | ENN4 | INC5 | DEC5 | ENT5 | ENN5 | INC6 | DEC6 | ENT6 | ENN6 | INCX | DECX | ENTX | ENNX | CMPA | CMP1 | CMP2 | CMP3 | CMP4 | CMP5 | CMP6 | CMPX
<OP>            -> <MIX-OP> | EQU | ORIG | CON | ALF | END

<SYMBOL>        -> (<DIGIT> | <LETTER>)* <LETTER> (<DIGIT> | <LETTER>)*
<NUMBER>        -> <DIGIT>+
<ATOMIC-EXPR>   -> <NUMBER> | <SYMBOL> | <LOC-COUNTER>
<EXPR>          -> <ATOMIC-EXPR> | <SIGN> <ATOMIC-EXPR> | <EXPR> <BINARY-OP> <ATOMIC-EXPR>

<INDEX-PART>    -> NULL | ,<EXPR>
<F-PART>        -> NULL | (<EXPR>)

<W-VALUE>       -> <EXPR><F-PART> | <W-VALUE>,<EXPR><F-PART>
<LITERAL-CONST> -> =<W-VALUE>=

<A-PART>        -> NULL | <EXPR> | <SYMBOL> | <LITERAL-CONST>
<INSTRUCTION>   -> <SYMBOL>?<SPACE>+<OP><SPACE>+<INDEX-PART><F-PART>
"""

DIGIT = r"[0-9]"
LETTER = r"[A-Z\_]"  # add an underscore to represent spaces in ALF strings/literals
SPACE = r"[ \t]"
SIGN = r"[\+\-]"
BINARY_OP = r"(?:[\+\-\*\/\:]|\/\/)"
LOC_COUNTER = r"\*"
MIX_OP = r"NOP|ADD|SUB|MUL|DIV|NUM|CHAR|HLT|SLA|SRA|SLAX|SRAX|SLC|SRC|MOVE|LDA|LD1|LD2|LD3|LD4|LD5|LD6|LDX|LDAN|LD1N|LD2N|LD3N|LD4N|LD5N|LD6N|LDXN|STA|ST1|ST2|ST3|ST4|ST5|ST6|STX|STJ|STZ|JBUS|IOC|IN|OUT|JRED|JMP|JSJ|JOV|JNOV|JL|JE|JG|JGE|JNE|JLE|JAN|JAZ|JAP|JANN|JANZ|JANP|J1N|J1Z|J1P|J1NN|J1NZ|J1NP|J2N|J2Z|J2P|J2NN|J2NZ|J2NP|J3N|J3Z|J3P|J3NN|J3NZ|J3NP|J4N|J4Z|J4P|J4NN|J4NZ|J4NP|J5N|J5Z|J5P|J5NN|J5NZ|J5NP|J6N|J6Z|J6P|J6NN|J6NZ|J6NP|JXN|JXZ|JXP|JXNN|JXNZ|JXNP|INCA|DECA|ENTA|ENNA|INC1|DEC1|ENT1|ENN1|INC2|DEC2|ENT2|ENN2|INC3|DEC3|ENT3|ENN3|INC4|DEC4|ENT4|ENN4|INC5|DEC5|ENT5|ENN5|INC6|DEC6|ENT6|ENN6|INCX|DECX|ENTX|ENNX|CMPA|CMP1|CMP2|CMP3|CMP4|CMP5|CMP6|CMPX"
OP = rf"(?:{MIX_OP}|EQU|ORIG|CON|ALF|END)"

SYMBOL = rf"(?:{DIGIT}|{LETTER})*{LETTER}(?:{DIGIT}|{LETTER})*"
NUMBER = rf"{DIGIT}+"
ATOMIC_EXPR = rf"(?:{NUMBER}|{SYMBOL}|{LOC_COUNTER})"
# TODO support full recursive definition rather than just one level
EXPR = rf"(?:{ATOMIC_EXPR}|{SIGN}{ATOMIC_EXPR}|{ATOMIC_EXPR}{BINARY_OP}{ATOMIC_EXPR})"

INDEX_PART = rf",({EXPR})"
F_PART = rf"\({EXPR}\)"

# TODO support full recursive definition rather than just one level
W_VALUE = rf"(?:{EXPR}(?:{F_PART})?|{EXPR}(?:{F_PART})?,{EXPR}(?:{F_PART})?)"
LITERAL_CONST = rf"(?:\={W_VALUE}\=)"

A_PART = rf"(?:{EXPR}|{SYMBOL}|{LITERAL_CONST})?"
INSTRUCTION = (
    rf"^"  # start
    rf"({SYMBOL})?"  # optional location
    rf"{SPACE}+"  # space between location and op (or leading space before op)
    rf"({OP})"  # op (only required part)
    rf"(?:{SPACE}+({A_PART}))?"  # optional address (with space separating from op)
    rf"(?:{INDEX_PART})?"  # optional index (capture occurs in INDEX_PART)
    rf"({F_PART})?"  # optional field (capture includes parens due to W_VALUE definition)
    rf"$"  # end
)
