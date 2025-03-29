class Var:
    def __init__(self, idx: int) -> None:
        self.idx: int = idx

    def __str__(self) -> str:
        return f"x{self.idx}"

    def to_latex(self) -> str:
        return f"x_{{{self.idx}}}"
