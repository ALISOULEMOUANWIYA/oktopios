#token_type.py
from enum import Enum, auto

class TokenType(Enum):
    FALSE = None
    TRUE = None
    VAR = auto()
    VAL = auto()
    REF = auto()
    INOUT = auto()
    FSTRING = auto()
    PRINT = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    VOID = auto()

    IN = auto()
    NOT_IN = auto()
    NOT = auto()
    IS = auto()
    IS_LIKE = auto()
    NOT_LIKE = auto()
    IS_EMPTY = auto()
    IS_MATCHES = auto()
    MATCHES = auto()
    AND = auto()
    OR = auto()
    BETWEEN = auto()
    IF = auto()
    ELSE = auto()
    ELIF = auto()      # ✅ Ajoute ceci
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    WHILE = auto()
    DO = auto()
    UNTIL = auto()
    BREAK = auto()
    CONTINUE = auto()
    FOR = auto()
    # Boucles intelligentes
    LOOP = auto()
    FILTER_LOOP = auto()
    FILTER_WHILE = auto()
    SORT_LOOP = auto()
    PERMUTE_LOOP = auto()
    PERMUTE_WHILE = auto()
    CIRCULAR_LOOP = auto()
    CIRCULAR_WHILE = auto()
    SLEEPING_LOOP = auto()
    # Modificateurs de boucle
    SOURCE = auto()
    SHUFFLE = auto()
    PATTERN = auto()
    STRIDE = auto()
    FILTER = auto()
    TRIGGER = auto()
    SPIRAL = auto()
    WAVE = auto()
    SECTORS = auto()
    WHERE = auto()
    THEN = auto()
    BY = auto()
    ORDER = auto()
    ASC = auto()
    DESC = auto()
    STEP = auto()
    WAIT_UNTIL = auto()
    USING = auto()
    MODE = auto()
    WHENEVER = auto()
    CHECK = auto()


    RANGE = auto()     # :

    ID = auto()
    NUMBER = auto()
    STR = auto()
    CHAR = auto()
    BOOLVAL = auto()

    EQ = auto()
    COLON = auto()
    PIPE = auto()
    SEMICOLON = auto()
    QUESTION = auto()  # ?
    PLUS = auto()
    MINUS = auto()
    PERCENT = auto()
    STAR = auto()
    SLASH = auto()
    PLUSEQ = auto()  # +=
    PLUSPLUS = auto() # ++
    MINUSEQ = auto()  # -=
    MINUSMINUS = auto()  # --
    STAREQ = auto()  # *=
    SLASHEQ = auto()  # /=
    COMMA = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    NEWLINE = auto()
    EOF = auto()
    LAMBDA = auto()

    ARROW = auto()
    GT = auto()
    LT = auto()
    GE = auto()
    LE = auto()
    EQEQ = auto()
    NE = auto()

    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    NEW = auto()
    DOT = auto()  # #--------------- à revenire
    THIS = auto()  #  #--------------- à revenire
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]

    FUN = auto()
    RETURN = auto()

    # Niveau 3 : POO pieuvrique
    CLASS = auto()
    DIRECTOR = auto(),
    SUPEVISOR = auto(),
    AGENT = auto(),
    SECRETARY = auto(),
    TEN = auto()
    INTENTION = auto()
    TENT_RANDOM = auto()
    TENT = auto()
    ENUM  = auto()

    CONSTRUCT = auto()
    DESTRUCT = auto()

    INVOKE = auto()
    OVERRIDE = auto()
    PRIVATE = auto(),
    PUBLIC = auto(),
    PROTECTED = auto(),
    GLOBAL = auto(),

    ACTIVATE = auto()
    EXTENDS = auto()
    ABSTRACT = auto()
    STATIC = auto()
    INTERFACE = auto()
    IMPLEMENTS  = auto()
    SUPER  = auto()
    SUPER_FORCE  = auto()
    IMPORT  = auto()
    INJECT  = auto()
    AS  = auto()
    USE  = auto()
    FROM  = auto()
    DELETE  = auto()

    HEART = auto()
    CORE = auto()
    IO = auto()
    NET = auto()
