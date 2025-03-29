import string
import logging
from typing import Optional

from model import Model
from var import Var
from literal import Literal
from clause import Clause
from formula import Formula


Answer = tuple[bool, Optional[Model]]


class DummyLogger:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


class Parser:
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.path: Optional[str] = None
        self.logger = logger or DummyLogger()

    def set_path(self, path: str) -> None:
        self.path = path

    def open_and_read(self) -> str:
        if self.path is None:
            raise Exception("No path set! Call \"set_path\" first!")

        with open(self.path, "rt") as fin:
            text = fin.read()

        return text

    def get_non_comment_lines(self, text: str) -> list[tuple[int, str]]:
        origlines = enumerate(text.splitlines())
        # Remove all comments now
        lines = [line for line in origlines if not line[1].startswith("c")]
        return lines


class FormulaParser(Parser):
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(logger)

    def parse(self) -> Optional[Formula]:
        text = self.open_and_read()
        lines = self.get_non_comment_lines(text)

        nvars = None
        nclauses = None
        firstline = lines[0][1]
        if firstline.startswith("p cnf "):
            _, _, vs, cs = firstline.split()
            nvars = int(vs)
            nclauses = int(cs)
            lines = lines[1:]

        literals: list[Literal] = []
        clauses: list[Clause] = []

        # We want to accept the very permissive DIMACS format, in which a
        # single clause can be spread on multiple lines.
        for lineno, line in lines:
            # This is to support a weird format which seems to end in "%\n0"??
            if line == "%":
                break

            for number in line.split():
                if number == "0":
                    newclause = Clause(literals)
                    clauses.append(newclause)
                    literals = []
                    continue

                if number[0] not in "-" + string.digits:
                    self.logger.error(f"[{self.path}:{lineno}] Invalid "
                                      f"literal {number}!")
                    return None

                for d in number[1:]:
                    if d not in string.digits:
                        self.logger.error(f"[{self.path}:{lineno}] Invalid "
                                          f"literal {number}!")
                        return None

                pos: bool = number[0] != "-"
                varidx: int = int(number if pos else number[1:])

                # It can't be lower than 1 at this point, because we explicitly
                # check that it's made of digits and that it's not 0.
                if nvars is not None and varidx > nvars:
                    self.logger.error(f"[{self.path}:{lineno}] Number of "
                                      f"variables explicitly mentioned as "
                                      f"{nvars}, but literal {number} refers "
                                      f"to a larger number!")
                    return None

                newvar = Var(varidx)
                newliteral = Literal(newvar, pos)
                literals.append(newliteral)

        if nclauses is not None and len(clauses) != nclauses:
            self.logger.error(f"[{self.path}] Number of clauses "
                              f"explicitly mentioned as {nclauses}, but "
                              f"there are {len(clauses)} clauses present!")
            return None

        phi = Formula(clauses)
        return phi


class AnswerParser(Parser):
    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(logger)

    def parse(self) -> Optional[Answer]:
        text = self.open_and_read()
        lines = self.get_non_comment_lines(text)

        model = {}
        encountered_answer_line = False
        for lineno, line in lines:
            if line.startswith("s "):
                if encountered_answer_line:
                    self.logger.error(f"[{self.path}:{lineno}] Multiple "
                                      "answer lines!")
                    return None

                encountered_answer_line = True
                _, answer = line.split()
                if answer == "UNSATISFIABLE":
                    if len(lines) != 1:
                        self.logger.error(f"[{self.path}] Invalid answer "
                                          "file, UNSATISFIABLE answer "
                                          "followed by more lines!")
                        return None

                    return (False, None)

                if answer != "SATISFIABLE":
                    self.logger.error(f"[{self.path}] Invalid answer file, "
                                      f"unknown answer: \"{answer}\"!")
                    return None
            elif line.startswith("v "):
                _, *literals = line.split()
                for literal in literals:
                    if literal == "0":
                        continue

                    if literal[0] not in "-" + string.digits:
                        self.logger.error(f"[{self.path}:{lineno}] Invalid "
                                          f"literal {literal}!")
                        return None

                    for d in literal[1:]:
                        if d not in string.digits:
                            self.logger.error(f"[{self.path}:{lineno}] Invalid"
                                              f" literal {literal}!")
                            return None

                    value: bool = literal[0] != "-"
                    varidx: int = int(literal if value else literal[1:])
                    if varidx in model:
                        self.logger.error(f"[{self.path}:{lineno}] Model "
                                          f"already provided value for"
                                          " {varidx}!")
                        return None

                    model[varidx] = value
            else:
                self.logger.error(f"[{self.path}:{lineno}] Invalid model "
                                  "line!")
                return None

        for idx in range(1, len(model.keys()) + 1):
            if idx not in model:
                self.logger.error(f"[{self.path}] Model does not "
                                  f"provide a value for {idx}!")
                return None

        return (True, model)
