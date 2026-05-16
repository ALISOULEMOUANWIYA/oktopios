#lexer.py
from collections import namedtuple
import re
from .token_type import TokenType



KEYWORDS = {
    "var": TokenType.VAR, # pour declarer une variable
    "val": TokenType.VAL, # pour declarer une constante
    "ref": TokenType.REF, # (pas encors implementer) pour declarer une reference
    "inout": TokenType.INOUT, # pour declarer une reference d'entree/sortie
    "print": TokenType.PRINT, # pour afficher une valeur
    "int": TokenType.INT, #
    "float": TokenType.FLOAT,
    "string": TokenType.STRING,
    "char": TokenType.CHAR,
    "bool": TokenType.BOOL,
    "void": TokenType.VOID,

    "true": TokenType.BOOLVAL,
    "false": TokenType.BOOLVAL,
    "and": TokenType.AND,

    "or": TokenType.OR, # (pas encors implementer)
    "is": TokenType.IS, # (pas encors implementer) pour verifier si une veariable A est egale à une variable B
    "like": TokenType.IS_LIKE, # (pas encors implementer) pour verifier si une veariable A est egale à une variable B
    "empty": TokenType.IS_EMPTY, # (pas encors implementer) pour verifier si une variable n'est pas vide
    "in": TokenType.IN, # pour verifier si une veariable A est dans une variable B
    "not": TokenType.NOT,  # pour neguer une condition
    "__matches__": TokenType.IS_MATCHES,
    "matches": TokenType.MATCHES,
    "between": TokenType.BETWEEN,

    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "elif": TokenType.ELIF,
    "switch": TokenType.SWITCH,
    "case": TokenType.CASE,
    "default": TokenType.DEFAULT,
    "while": TokenType.WHILE,
    "do": TokenType.DO, # à faire
    "until": TokenType.UNTIL,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,

    # Boucles intelligentes (mots-clés)
    "loop": TokenType.LOOP,
    "filterLoop": TokenType.FILTER_LOOP,
    "filterWhile": TokenType.FILTER_WHILE,
    "sortLoop": TokenType.SORT_LOOP,
    "permuteLoop": TokenType.PERMUTE_LOOP,
    "permuteWhile": TokenType.PERMUTE_WHILE,
    "circularLoop": TokenType.CIRCULAR_LOOP,
    "circularWhile": TokenType.CIRCULAR_WHILE,
    "sleepingLoop": TokenType.SLEEPING_LOOP,



    # Modificateurs de boucle
    "source": TokenType.SOURCE,
    "shuffle": TokenType.SHUFFLE,
    "pattern": TokenType.PATTERN,
    "stride": TokenType.STRIDE,
    "filter": TokenType.FILTER,
    "trigger": TokenType.TRIGGER,
    "spiral": TokenType.SPIRAL,
    "wave": TokenType.WAVE,
    "sectors": TokenType.SECTORS,
    "where": TokenType.WHERE,
    "then": TokenType.THEN,
    "by": TokenType.BY,
    "order": TokenType.ORDER,
    "asc": TokenType.ASC,
    "desc": TokenType.DESC,
    "using": TokenType.USING,
    "mode": TokenType.MODE,
    "whenever": TokenType.WHENEVER,
    "check": TokenType.CHECK,


    "step": TokenType.STEP,
    "waitUntil": TokenType.WAIT_UNTIL,


    "try": TokenType.TRY,
    "catch": TokenType.CATCH,
    "finally": TokenType.FINALLY,
    "throw": TokenType.THROW,
    "new": TokenType.NEW,
    "this": TokenType.THIS,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "lambda": TokenType.LAMBDA,
    "return": TokenType.RETURN,

    # Niveau 3 : POO pieuvrique
    "class": TokenType.CLASS,
    "abstract": TokenType.ABSTRACT,
    "interface": TokenType.INTERFACE,
    "__construct": TokenType.CONSTRUCT, # Pour construire une instance
    "__destruct": TokenType.DESTRUCT, # Pour detruire une instance

    "director": TokenType.DIRECTOR, # (pas encors implementer)
    "supervisor": TokenType.SUPEVISOR, # (pas encors implementer)
    "agent": TokenType.AGENT, # (pas encors implementer)
    "secretary": TokenType.SECRETARY, # (pas encors implementer)
    "ten": TokenType.TEN, # (pas encors implementer) Pour definir que la class main est un coeur d'une tentacule Xn
    "tent": TokenType.TENT, # (pas encors implementer) Pour definir que la class main est du coeur Central
    "intention": TokenType.INTENTION, # (pas encors implementer) Pour concentrer l'intention de tous les tentacules Xn à une tache en alerte
    "tentRandom": TokenType.TENT_RANDOM, # (pas encors implementer) Pour definir les tentacule à des taches aleatoire selon les paramtre reçus

    "override": TokenType.OVERRIDE, # Pour las fonction override (abstract)
    "activate": TokenType.ACTIVATE, # pour activer une fonction ou une class non heritee
    "invoke": TokenType.INVOKE, # pour invoquer une fonction heritee d'un interface
    "private": TokenType.PRIVATE, # pour definir une fonction ou une class comme private
    "public": TokenType.PUBLIC, # pour definir une fonction ou une class comme public
    "protected": TokenType.PROTECTED, # pour definir une fonction ou une class comme protected
    "global": TokenType.GLOBAL, # pour definir une fonction, une class, var/val ou const comme global
    "extends": TokenType.EXTENDS, # pour heriter d'une class
    "static": TokenType.STATIC, # pour definir une fonction ou une class comme statique
    "implements": TokenType.IMPLEMENTS, # pour implementer une interface
    "enum": TokenType.ENUM, # pour definir une enum
    "super": TokenType.SUPER, # pour faire appel ou envoyer des paramtres à un parent
    "super_force": TokenType.SUPER_FORCE, # pour faire appel ou envoyer des paramtres à un parent de manier doublé
    "import": TokenType.IMPORT, # pour importer une class ou une fonction
    "inject": TokenType.INJECT, # pour injecter une fonction native
    "as": TokenType.AS, # pour faire un alias lors de l'importation d'une fonction
    "use": TokenType.USE, # pour importer un chemein vers une classe
    "from": TokenType.FROM, # pour importer un chemein vers une classe
    "delete": TokenType.DELETE,

    # Accès aux cœurs
    "heart": TokenType.HEART, # (pas encors implementer) Lieu des parametrage centralle
    "core": TokenType.CORE, # (pas encors implementer) Noyeau du coeur central
    "io": TokenType.IO, # (pas encors implementer) indicateur d'instance vers le coeur central
    "net": TokenType.NET, # (pas encors implementer) indicateur d'instance du coeur central vers l'exterieur
}

# | (?P<NOTIN>not\s+in)
# | (?P<IN>\bin\b)

TOK_REGEX = re.compile(r'''
    (?P<NEWLINE>\n)
  | (?P<SKIP>[ \t]+)
  | (?P<COMMENT>//.*)
  | (?P<NUMBER>\d+(\.\d+)?)
  | (?P<STRING>"[^"]*")
  | (?P<CHAR>'[^']*')
  | (?P<ID>[a-zA-Z_][a-zA-Z_0-9]*)
  | (?P<QUESTION>\?)
  | (?P<COLON>:)
  | (?P<SEMICOLON>;)
  | (?P<PERCENT>%)

  | (?P<PLUSPLUS>\+\+)
  | (?P<MINUSMINUS>--)
  | (?P<PLUSEQ>\+=)
  | (?P<MINUSEQ>-=)
  | (?P<STAREQ>\*=)
  | (?P<SLASHEQ>/=)
  | (?P<ARROW>=>)
  | (?P<GE>>=)
  | (?P<LE><=)
  | (?P<EQEQ>==)
  | (?P<NE>!=)

  | (?P<PLUS>\+)
  | (?P<MINUS>-)
  | (?P<STAR>\*)
  | (?P<SLASH>/)
  | (?P<GT>>)
  | (?P<LT><)
  | (?P<EQ>=)



  | (?P<LPAREN>\()
  | (?P<RPAREN>\))  
  | (?P<LBRACKET>\[)
  | (?P<RBRACKET>])
  | (?P<LBRACE>\{)
  | (?P<RBRACE>})
  | (?P<COMMA>,)
  | (?P<DOT>\.)
  | (?P<PIPE>\|)
  | (?P<MISMATCH>.)
''', re.VERBOSE)


TYPE_ALIASES = {
    "int": "int",
    "float": "float",
    "bool": "bool",
    "boolean": "bool",
    "string": "string",
    "str": "string",
    "double": "float",
    "char": "string",
    "string[]": "string[]",
    "int[]": "int[]",
    "bool[]": "bool[]",
    "float[]": "float[]",
    "[]": "array",
    "array": "array",
    "list": "list",
    "tuple": "tuple",
    "sets": "sets",
    "dict": "dict",
    "arrayknot": "arrayknot",
    "map": "map",

}


Token = namedtuple("Token", ["type", "value", "line", "column"])

def tokenize(code):
    line_num = 1
    line_start = 0
    raw_tokens = []
    i = 0

    while i < len(code):
        c = code[i]

        # --- Détection des f-strings ---
        if c == 'f' and i + 1 < len(code) and code[i + 1] in ('"', "'"):
            quote = code[i + 1]
            i += 2
            value = ""
            while i < len(code) and code[i] != quote:
                value += code[i]
                i += 1
            i += 1  # consomme la quote fermante

            # Interprétation des échappements seulement
            value = value.replace(r"\n", "\n").replace(r"\t", "\t").replace(r"\\", "\\")

            raw_tokens.append(Token(TokenType.FSTRING, value, line_num, i))
            continue

        # --- Fin détection f-string ---

        # Applique le regex classique
        match = TOK_REGEX.match(code, i)
        if not match:
            raise SyntaxError(f"[Ligne {line_num}] Caractère inattendu : '{code[i]}'")

        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start
        i = match.end()

        if kind == "NEWLINE":
            line_num += 1
            line_start = match.end()
        elif kind in ("SKIP" ,"COMMENT"):
            continue
        elif kind == "ID" and value in KEYWORDS:
            raw_tokens.append(Token(KEYWORDS[value], value, line_num, column))
        elif kind == "ID":
            raw_tokens.append(Token(TokenType.ID, value, line_num, column))
        elif kind == "NUMBER":
            raw_tokens.append(Token(TokenType.NUMBER, float(value) if "." in value else int(value), line_num, column))
        elif kind == "STRING":
            value = bytes(value[1:-1], "utf-8").decode("unicode_escape")
            raw_tokens.append(Token(TokenType.STR, value, line_num, column))
        elif kind in TokenType.__members__:
            if kind == "PIPE":
                raw_tokens.append(Token(TokenType.RANGE, value, line_num, column))
            else:
                raw_tokens.append(Token(TokenType[kind], value, line_num, column))
        elif kind == "MISMATCH":
            raise SyntaxError(f"[Ligne {line_num}] Caractère inattendu : '{value}'")

    # Fusion "not in"
    tokens = []
    i = 0
    while i < len(raw_tokens):
        if (
            raw_tokens[i].type == TokenType.NOT and
            i + 1 < len(raw_tokens) and
            raw_tokens[i + 1].type == TokenType.IN
        ):
            tokens.append(Token(TokenType.NOT_IN, "not in", raw_tokens[i].line, raw_tokens[i].column))
            i += 2
        else:
            tokens.append(raw_tokens[i])
            i += 1

    tokens.append(Token(TokenType.EOF, "", line_num, 0))
    return tokens
