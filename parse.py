import sys
from lex import *

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return kind == self.curToken.kind

    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)

        self.nextToken()
    
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # EOF is handled by lexer

    def abort(self, message):
        sys.exit("Error. " + message)

    # Production rules
    def program(self):
        print("PROGRAM")

        # parse all statements in program
        while not self.checkToken((TokenType.EOF)):
            self.statement()
    
    def statement(self):
        # Check the first token to see what kind of statement this is

        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                self.nextToken()
            else:
                self.expression()

        self.newline()

    def newline(self):
        print("NEWLINE")

        # Require at least one new line
        self.match(TokenType.NEWLINE)

        # allow extras
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()