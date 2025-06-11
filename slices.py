from collections import defaultdict
from functools import reduce
from operator import or_

from pysmt.shortcuts import *
from pysmt.typing import STRING
from schema import *

def get_dependencies(sch, ep):
    conds, last = ep
    stack = [[sch, 0]]
    ci = 0
    visual_depends = {}
    depends = defaultdict(set)
    pred_depends = {}
    pred_stack = [set()]
    while ci < len(conds) or last:
        s, i = stack[-1]
        if i == len(s.parts):
            stack.pop()
            pred_stack.pop()
            stack[-1][1] += 1
            continue
        if isinstance(s.parts[i], Assign):
            asn : Assign = s.parts[i]
            asn.reached = True
            visual_depends[asn.v] = asn.f + "(" + ",".join(visual_depends[arg] if arg in visual_depends else arg for arg in asn.args) + ")"
            depends[asn.v] = {asn.id} | reduce(or_, (depends[arg] for arg in asn.args), set()) | pred_stack[-1]
        elif isinstance(s.parts[i], If):
            _if : If = s.parts[i]
            pred_depends[_if.id] = reduce(or_, (depends[arg] for arg in _if.args), set())
            _if.reached = True
            pred_stack.append(pred_stack[-1] | pred_depends[_if.id])
            if conds[ci]:
                stack.append([_if.pt, 0])
            else:
                stack.append([_if.pf, 0])
            ci += 1
            continue
        if ci == len(conds):
            last -= 1
            if not last:
                break
        stack[-1][1] += 1
    return depends, pred_depends


def enum_assigns(s, assigns, preds):
    for i in range(len(s.parts)):
        if isinstance(s.parts[i], Assign):
            asn: Assign = s.parts[i]
            asn.id = len(assigns)
            assigns.append(asn)
        elif isinstance(s.parts[i], If):
            _if: If = s.parts[i]
            _if.id = len(preds)
            preds.append(_if)
            enum_assigns(_if.pt, assigns, preds)
            enum_assigns(_if.pf, assigns, preds)


def find_slice(s, ep, v):
    assigns = []
    preds = []
    enum_assigns(s, assigns, preds)
    depends, pred_depends = get_dependencies(s, ep)
    # print(list((i, asn.v, asn.f, asn.args, asn.id, asn.reached) for i, asn in enumerate(assigns)))
    # print(list((i, pred.p, pred.id) for i, pred in enumerate(preds)))
    # print(depends)
    # print(pred_depends)
    included = []
    a_id_include = {}

    # do we include the ith assign statement?
    for assign in assigns:
        asn = Symbol(f"include_{assign.id}", BOOL)
        included.append(asn)
        a_id_include[assign.id] = asn

    path_faithful = []
    # are the assign statements path-faithful?
    # if we include the assignment, we must have reached it in the execution path
    for assign in assigns:
        a_id = assign.id
        asn = a_id_include[a_id]
        pf = Implies(asn, Bool(assign.reached))
        path_faithful.append(pf)

    deps = []
    # are our dependency requirements met?
    # get a set of all dependencies for all the variables we care about
    # if we depend on an assign statement, we must choose to include it
    total_depends = reduce(or_, (depends[var] for var in v), set())
    for a_id in total_depends:
        asn = a_id_include[a_id]
        deps.append(asn)

    # dependencies for predicates
    # only need to preserve predicates that are reached in the path
    pred_deps = []
    for p_id, a_ids in pred_depends.items():
        pred = preds[p_id]
        if pred.reached:
            for a_id in a_ids:
                asn = a_id_include[a_id]
                pred_deps.append(asn)

    # non-triviality
    # is at least one assignment from the original execution path
    # not included
    on_path = []
    for assign in assigns:
        a_id = assign.id
        asn = a_id_include[a_id]
        if assign.reached:
            on_path.append(asn)
    non_trivial = Or(Not(asn) for asn in on_path)

    formula = And(
        And(*path_faithful),
        And(*deps),
        And(*pred_deps),
        non_trivial
    )
    with Solver("z3") as solver:
        solver.add_assertion(formula)
        if solver.solve():
            keep = [solver.get_value(assign).constant_value() for assign in included]
            return {assign.line_number for assign, k in zip(assigns, keep) if not k}
        return None

