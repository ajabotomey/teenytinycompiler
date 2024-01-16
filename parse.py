import sys
from lex import *

class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()
        self.labelsDeclared = set()
        self.labelsGotoed = set()

        self.curToken = None
        self.peekToken = None
        self.curLine = 1
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

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    def abort(self, message):
        sys.exit("Error. " + message)

    # Production rules
    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("#include <time.h>")
        self.emitter.headerLine("#include <stdlib.h>")
        self.emitter.headerLine("int main(void){")

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # parse all statements in program
        while not self.checkToken((TokenType.EOF)):
            self.statement()

        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)
    
    def statement(self):
        # Check the first token to see what kind of statement this is

        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                self.emitter.emitLine("printf(\"" + self.curToken.text + "\\n\");")
                self.nextToken()
            else:
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emitLine("));")
        elif self.checkToken(TokenType.IF):
            print("STATEMENT-IF")
            self.nextToken()
            self.emitter.emit("if (")
            self.comparison()

            self.match(TokenType.THEN)
            self.newline()
            self.emitter.emitLine(") {")

            # Zero or more statements in the body
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")
        # elif self.checkToken(TokenType.ELSE):
        #     print("STATEMENT-ELSE")
        #     self.nextToken()
        #     self.newline()

        #     # Zero or more statements in the body
        #     while not self.checkToken(TokenType.ENDIF):
        #         self.statement()

        #     self.match(TokenType.ENDIF)
        # elif self.checkToken(TokenType.ELSEIF):
        #     print("STATEMENT-ELSEIF")
        #     self.nextToken()
        #     self.comparison()

        #     self.match(TokenType.THEN)
        #     self.newline()

        #     # Zero or more statements in the body
        #     while not self.checkToken(TokenType.ENDIF):
        #         self.statement()

        #     self.match(TokenType.ENDIF)
        elif self.checkToken(TokenType.RND):
            print("STATEMENT-RND")
            self.nextToken()
            self.emitter.emitLine("srand(time(0));")
            self.emitter.emitLine("int " + self.curToken.text + " = rand() % 100 + 1;")
            self.match(TokenType.IDENT)

        elif self.checkToken(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.nextToken()
            self.emitter.emit("while (")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.newline()
            self.emitter.emitLine(") {")

            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")
        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.nextToken()
            
            # Make sure label doesn't already exist
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)
        elif self.checkToken(TokenType.LET):
            print("STATEMENT-LET")
            self.nextToken()

            # Check if ident exists
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emitLine(";")
        elif self.checkToken(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.nextToken()

            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emitLine("if (0 == scanf(\"%" + "f\", &" + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ") at line " + str(self.curLine))

        self.newline()

    def comparison(self):
        print("COMPARISON")

        self.expression()
        # Must have at least one comparison operator and another expression
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at " + self.curToken.text)

        # Can have 0 or more comparison operator and expressions
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    def expression(self):
        print("EXPRESSION")

        self.term()
        # Can have 0 or more +/- and expressions
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    def term(self):
        print("TERM")

        self.unary()
        # Can have 0 or more *// and expressions
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    def unary(self):
        print("UNARY")

        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    def primary(self):
        print("PRIMARY (" + self.curToken.text + ")")

        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)
            
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected token at " + self.curToken.text)

    def newline(self):
        print("NEWLINE")

        # Require at least one new line
        self.match(TokenType.NEWLINE)
        self.curLine += 1

        # allow extras
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()