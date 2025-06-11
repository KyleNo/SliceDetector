from typing import List

class Schema:
    def __init__(self, *args):
        self.parts = list(args)

    def __repr__(self):
        return ("Seq(\n" +
                "\n".join(map(str, self.parts)) +
                "\n)")

class Assign:
    def __init__(self, v: str, f: str, args: List[str], line_no=None):
        self.v = v
        self.f = f
        self.args = args
        self.id = None
        self.reached = False
        self.line_number = line_no

    def __repr__(self):
        return f"Let {self.v} = {self.f}({",".join(self.args)})"

class If:
    def __init__(self, p: str, args: List[str], pt: Schema, pf: Schema):
        self.p = p
        self.args = args
        self.pt = pt
        self.pf = pf
        self.id = None
        self.reached = False

    def __repr__(self):
        return (f"if ({self.p}{tuple(self.args)}:\n"
                f"\t{self.pt}\n"
                f"else\n"
                f"\t{self.pf}")