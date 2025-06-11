import re
from schema import *

def parse_schema(lines):
    def parse_block(lines, i):
        stmts = []
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith("if "):
                cond_call = line[3:].strip()
                m = re.match(r'(\w+)\(([^)]*)\)', cond_call)
                if not m:
                    raise SyntaxError(f"Invalid if condition: {line}")
                cond, arg_str = m.groups()
                args = [a.strip() for a in arg_str.split(',') if a.strip()]
                i += 1
                pt, i = parse_block(lines, i)
                pf = Schema()
                if i < len(lines) and lines[i].strip().startswith("else"):
                    i += 1
                    pf, i = parse_block(lines, i)
                if i >= len(lines) or not lines[i].strip().startswith("fi"):
                    raise SyntaxError("Missing fi")
                i += 1
                stmts.append(If(cond, args, pt, pf))
            elif line == "else" or line == "fi":
                break
            else:
                m = re.match(r'(\w+)\s*=\s*(\w+)\(([^)]*)\)', line)
                if not m:
                    raise SyntaxError(f"Invalid assignment: {line}")
                var, func, arg_str = m.groups()
                args = [a.strip() for a in arg_str.split(',') if a.strip()]
                # print(var, func, args)
                stmts.append(Assign(var, func, args, line_no=i))
                i += 1
        return Schema(*stmts), i

    lines = lines.strip().split('\n')
    schema, i = parse_block(lines, 0)
    if i != len(lines):
        raise SyntaxError("Unexpected trailing lines")
    return schema

def parse_input(s):
    program, exec_path, vars = s.split("\n\n")
    schema = parse_schema(program)
    sp = exec_path.split("\n")
    if len(sp) == 2:
        conds, last = sp
        conds = tuple(ch == "T" for ch in conds)
        ep = conds, int(last)
    else:
        ep = tuple(), int(sp[0])
    vars = set(v.strip() for v in vars.split(","))
    return schema, ep, vars

if __name__ == "__main__":
    program = """
    x = f()
    y = g(x)
    z = h(x, y)
    if p(y, z)
        x = i(z)
        z = j()
    else
        w = k(x)
    fi
    y = l(x, z)
    if q(x)
        if r(z)
            x = m(y)
        fi
        if s(x)
            if t(y)
                z = n(z)
            fi
        fi
    fi
    """

    schema = parse_schema(program)
    print(schema)