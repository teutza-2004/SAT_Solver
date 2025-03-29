from clause import Clause


class Formula:
    def __init__(self, clauses: list[Clause]):
        self.clauses = clauses
        self.nclauses = len(self.clauses)
        self.count_vars()

    def count_vars(self) -> None:
        max_idx = 1
        for cl in self.clauses:
            for lit in cl.literals:
                if lit.var.idx > max_idx:
                    max_idx = lit.var.idx

        self.nvars = max_idx

    def __str__(self) -> str:
        return " ∧ ".join(str(clause) for clause in self.clauses)

    def to_latex(self) -> str:
        return " \\land ".join(f"({lit.to_latex()})" for lit in self.clauses)

    def to_dimacs(self) -> str:
        firstline = f"p cnf {self.nvars} {self.nclauses}\n"
        clstrs = (cl.to_dimacs() for cl in self.clauses)
        return firstline + "\n".join(clstrs) + "\n"
