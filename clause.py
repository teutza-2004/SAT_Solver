from literal import Literal


class Clause:
    def __init__(self, literals: list[Literal]):
        self.literals = literals
        self.n = len(self.literals)

    def __str__(self) -> str:
        return " ∨ ".join(str(lit) for lit in self.literals)

    def to_latex(self) -> str:
        return " \\lor ".join(lit.to_latex() for lit in self.literals)

    def to_dimacs(self) -> str:
        litstrs = (lit.to_dimacs() for lit in self.literals)
        return " ".join(litstrs) + " 0"
