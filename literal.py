from var import Var


class Literal:
    def __init__(self, var: Var, pos: bool = True) -> None:
        self.var: Var = var
        self.pos = pos

    def __str__(self) -> str:
        prefix = "" if self.pos else "¬"
        return prefix + str(self.var)

    def to_latex(self) -> str:
        if self.pos:
            return self.var.to_latex()

        return f"\\overline{{{self.var.to_latex()}}}"

    def to_dimacs(self) -> str:
        prefix = "" if self.pos else "-"
        return prefix + str(self.var.idx)
