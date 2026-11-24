import argparse
import re
import sys


TOKEN = re.compile(
    r"(?P<SPACE>[ \t\r\n]+)"
    r"|(?P<DATE>[0-9]{2}\.[0-9]{2}\.[0-9]{4}|[0-9]{4}/[0-9]{2}/[0-9]{2})"
    r"|(?P<INT>[0-9]+)|(?P<ID>[a-z]+)|(?P<SIGN>[-+*=();])"
)


def tokenize(text):
    position = 0
    while position < len(text):
        match = TOKEN.match(text, position)
        if match is None:
            raise SyntaxError
        position = match.end()
        kind = match.lastgroup
        if kind == "ID" and len(match.group()) > 2:
            raise SyntaxError
        if kind != "SPACE":
            yield match.group() if kind == "SIGN" else kind
    yield "EOF"


class Parser:
    def __init__(self, text):
        self.tokens = iter(tokenize(text))
        self.lookahead = next(self.tokens)

    def advance(self):
        self.lookahead = next(self.tokens)

    def take(self, token):
        if self.lookahead != token:
            return False
        self.advance()
        return True

    def program(self):
        self.expression()
        while self.take(";"):
            self.expression()
        if self.lookahead != "EOF":
            raise SyntaxError

    def expression(self):
        # E -> ID A | H B. Each ID followed by '=' starts another E.
        while self.take("ID"):
            if not self.take("="):
                break
        else:
            self.non_identifier_operand()
        self.binary_tail()

    def binary_tail(self):
        # B -> + U B | * U B | epsilon.
        while self.lookahead in ("+", "*"):
            self.advance()
            self.operand()

    def operand(self):
        if not self.take("ID"):
            self.non_identifier_operand()

    def non_identifier_operand(self):
        # H -> - U | ( E ) | DATE | INT. Collapse consecutive unary minuses.
        if self.take("-"):
            while self.take("-"):
                pass
            if self.take("ID"):
                return
        if self.take("("):
            self.expression()
            if not self.take(")"):
                raise SyntaxError
        elif self.lookahead in ("DATE", "INT"):
            self.advance()
        else:
            raise SyntaxError


def accepts(text):
    try:
        Parser(text).program()
    except SyntaxError:
        return False
    return True


def main():
    cli = argparse.ArgumentParser(description="Recognize a sequence of expressions.")
    cli.add_argument("text", nargs="?", help="input sequence (defaults to standard input)")
    args = cli.parse_args()
    text = sys.stdin.read() if args.text is None else args.text
    print("Accepted" if accepts(text) else "Rejected")


if __name__ == "__main__":
    main()
