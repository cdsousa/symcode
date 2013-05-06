""" Tools for doing common subexpression elimination.
"""
from collections import OrderedDict

from sympy.core import Basic, Mul, Add, sympify
from sympy.core.basic import preorder_traversal
from sympy.core.function import _coeff_isneg
from sympy.core.compatibility import iterable
from sympy.utilities.iterables import numbered_symbols, \
    sift, topological_sort, ordered

from sympy.simplify import cse_opts

# (preprocessor, postprocessor) pairs which are commonly useful. They should
# each take a sympy expression and return a possibly transformed expression.
# When used in the function ``cse()``, the target expressions will be transformed
# by each of the preprocessor functions in order. After the common
# subexpressions are eliminated, each resulting expression will have the
# postprocessor functions transform them in *reverse* order in order to undo the
# transformation if necessary. This allows the algorithm to operate on
# a representation of the expressions that allows for more optimization
# opportunities.
# ``None`` can be used to specify no transformation for either the preprocessor or
# postprocessor.

cse_optimizations = list(cse_opts.default_optimizations)

# sometimes we want the output in a different format; non-trivial
# transformations can be put here for users
# ===============================================================


def reps_toposort(r):
    """Sort replacements `r` so (k1, v1) appears before (k2, v2)
    if k2 is in v1's free symbols. This orders items in the
    way that cse returns its results (hence, in order to use the
    replacements in a substitution option it would make sense
    to reverse the order).

    Examples
    ========
    >>> from sympy.simplify.cse_main import reps_toposort
    >>> from sympy.abc import x, y
    >>> from sympy import Eq
    >>> for l, r in reps_toposort([(x, y + 1), (y, 2)]):
    ...     print Eq(l, r)
    ...
    y == 2
    x == y + 1

    """
    r = sympify(r)
    E = []
    for c1, (k1, v1) in enumerate(r):
        for c2, (k2, v2) in enumerate(r):
            if k1 in v2.free_symbols:
                E.append((c1, c2))
    return [r[i] for i in topological_sort((range(len(r)), E))]


def cse_separate(r, e):
    """Move expressions that are in the form (symbol, expr) out of the
    expressions and sort them into the replacements using the reps_toposort.

    Examples
    ========
    >>> from sympy.simplify.cse_main import cse_separate
    >>> from sympy.abc import x, y, z
    >>> from sympy import cos, exp, cse, Eq, symbols
    >>> x0, x1 = symbols('x:2')
    >>> eq = (x + 1 + exp((x + 1)/(y + 1)) + cos(y + 1))
    >>> cse([eq, Eq(x, z + 1), z - 2], postprocess=cse_separate) in [
    ... [[(x0, y + 1), (x, z + 1), (x1, x + 1)],
    ...  [x1 + exp(x1/x0) + cos(x0), z - 2]],
    ... [[(x1, y + 1), (x, z + 1), (x0, x + 1)],
    ...  [x0 + exp(x0/x1) + cos(x1), z - 2]]]
    ...
    True
    """
    d = sift(e, lambda w: w.is_Equality and w.lhs.is_Symbol)
    r = r + [w.args for w in d[True]]
    e = d[False]
    return [reps_toposort(r), e]

# ====end of cse postprocess idioms===========================


def preprocess_for_cse(expr, optimizations):
    """ Preprocess an expression to optimize for common subexpression
    elimination.

    Parameters
    ----------
    expr : sympy expression
        The target expression to optimize.
    optimizations : list of (callable, callable) pairs
        The (preprocessor, postprocessor) pairs.

    Returns
    -------
    expr : sympy expression
        The transformed expression.
    """
    for pre, post in optimizations:
        if pre is not None:
            expr = pre(expr)
    return expr


def postprocess_for_cse(expr, optimizations):
    """ Postprocess an expression after common subexpression elimination to
    return the expression to canonical sympy form.

    Parameters
    ----------
    expr : sympy expression
        The target expression to transform.
    optimizations : list of (callable, callable) pairs, optional
        The (preprocessor, postprocessor) pairs.  The postprocessors will be
        applied in reversed order to undo the effects of the preprocessors
        correctly.

    Returns
    -------
    expr : sympy expression
        The transformed expression.
    """
    if optimizations is None:
        optimizations = cse_optimizations
    for pre, post in reversed(optimizations):
        if post is not None:
            expr = post(expr)
    return expr


def _remove_singletons(reps, exprs):
    """
    Helper function for cse that will remove expressions that weren't
    used more than once.
    """
    u_reps = []  # the useful reps that are used more than once
    for i, ui in enumerate(reps):
        used = []  # where it was used
        ri, ei = ui

        # keep track of whether the substitution was used more
        # than once. If used is None, it was never used (yet);
        # if used is an int, that is the last place where it was
        # used (>=0 in the reps, <0 in the expressions) and if
        # it is True, it was used more than once.

        used = None

        tot = 0  # total times used so far

        # search through the reps
        for j in range(i + 1, len(reps)):
            c = reps[j][1].count(ri)
            if c:
                tot += c
                if tot > 1:
                    u_reps.append(ui)
                    used = True
                    break
                else:
                    used = j

        if used is not True:

            # then search through the expressions

            for j, rj in enumerate(exprs):
                c = rj.count(ri)
                if c:
                    # append a negative so we know that it was in the
                    # expression that used it
                    tot += c
                    if tot > 1:
                        u_reps.append(ui)
                        used = True
                        break
                    else:
                        used = j - len(exprs)

            if type(used) is int:

                # undo the change

                rep = {ri: ei}
                j = used
                if j < 0:
                    exprs[j] = exprs[j].subs(rep)
                else:
                    reps[j] = reps[j][0], reps[j][1].subs(rep)

    # reuse unused symbols so a contiguous range of symbols is returned

    if len(u_reps) != len(reps):
        for i, ri in enumerate(u_reps):
            if u_reps[i][0] != reps[i][0]:
                rep = (u_reps[i][0], reps[i][0])
                u_reps[i] = rep[1], u_reps[i][1].subs(*rep)
                for j in range(i + 1, len(u_reps)):
                    u_reps[j] = u_reps[j][0], u_reps[j][1].subs(*rep)
                for j, rj in enumerate(exprs):
                    exprs[j] = exprs[j].subs(*rep)

    reps[:] = u_reps  # change happens in-place


def cse(exprs, symbols=None, optimizations=None, postprocess=None):
    """ Perform common subexpression elimination on an expression.

    Parameters
    ==========

    exprs : list of sympy expressions, or a single sympy expression
        The expressions to reduce.
    symbols : infinite iterator yielding unique Symbols
        The symbols used to label the common subexpressions which are pulled
        out. The ``numbered_symbols`` generator is useful. The default is a
        stream of symbols of the form "x0", "x1", etc. This must be an infinite
        iterator.
    optimizations : list of (callable, callable) pairs, optional
        The (preprocessor, postprocessor) pairs. If not provided,
        ``sympy.simplify.cse.cse_optimizations`` is used.
    postprocess : a function which accepts the two return values of cse and
        returns the desired form of output from cse, e.g. if you want the
        replacements reversed the function might be the following lambda:
        lambda r, e: return reversed(r), e

    Returns
    =======

    replacements : list of (Symbol, expression) pairs
        All of the common subexpressions that were replaced. Subexpressions
        earlier in this list might show up in subexpressions later in this list.
    reduced_exprs : list of sympy expressions
        The reduced expressions with all of the replacements above.
    """
    from sympy.matrices import Matrix

    if symbols is None:
        symbols = numbered_symbols()
    else:
        # In case we get passed an iterable with an __iter__ method instead of
        # an actual iterator.
        symbols = iter(symbols)
    tmp_symbols = numbered_symbols('_csetmp')
    subexp_iv = dict()
    muls = set()
    adds = set()

    if optimizations is None:
        # Pull out the default here just in case there are some weird
        # manipulations of the module-level list in some other thread.
        optimizations = list(cse_optimizations)

    # Handle the case if just one expression was passed.
    if isinstance(exprs, Basic):
        exprs = [exprs]

    # Preprocess the expressions to give us better optimization opportunities.
    prep_exprs = [preprocess_for_cse(e, optimizations) for e in exprs]

    # Find all subexpressions.
    def _parse(expr):
        
        if expr.is_Atom:
            # Exclude atoms, since there is no point in renaming them.
            return expr
        
        if iterable(expr):
            return expr
        
        subexpr = type(expr)(*map(_parse, expr.args))

        if subexpr in subexp_iv:
            return subexp_iv[subexpr]
        
        if subexpr.is_Mul:
            muls.add(subexpr)
        elif subexpr.is_Add:
            adds.add(subexpr)

        ivar = next(tmp_symbols)
        subexp_iv[subexpr] = ivar
        
        return ivar
    
    tmp_exprs = list()
    for expr in prep_exprs:
        if isinstance(expr, Basic):
            tmp_exprs.append(_parse(expr))
        else:
            tmp_exprs.append(expr)
    
    # process adds - any adds that weren't repeated might contain
    # subpatterns that are repeated, e.g. x+y+z and x+y have x+y in common
    adds = list(ordered(adds))
    addargs = [set(a.args) for a in adds]
    for i in xrange(len(addargs)):
        for j in xrange(i + 1, len(addargs)):
            com = addargs[i].intersection(addargs[j])
            if len(com) > 1:
                
                add_subexp = Add(*com)
                
                diff_add_i = addargs[i].difference(com)
                diff_add_j = addargs[j].difference(com)
                
                if add_subexp in subexp_iv:
                    ivar = subexp_iv[add_subexp]
                else:
                    ivar = next(tmp_symbols)
                    subexp_iv[add_subexp] = ivar
                    
                if diff_add_i:
                    newadd = Add(ivar,*diff_add_i)
                    subexp_iv[newadd] = subexp_iv.pop(adds[i])
                    adds[i] = newadd
                #else add_i is itself subexp_iv[add_subexp] -> ivar
                
                if diff_add_j:
                    newadd = Add(ivar,*diff_add_j)
                    subexp_iv[newadd] = subexp_iv.pop(adds[j])
                    adds[j] = newadd
                #else add_j is itself subexp_iv[add_subexp] -> ivar
                        
                addargs[i] = diff_add_i
                addargs[j] = diff_add_j
                
                for k in xrange(j + 1, len(addargs)):
                    if com.issubset(addargs[k]):
                        
                        diff_add_k = addargs[k].difference(com)
                        
                        if diff_add_k:
                            newadd = Add(ivar,*diff_add_k)
                            subexp_iv[newadd] = subexp_iv.pop(adds[k])
                            adds[k] = newadd
                        #else add_k is itself subexp_iv[add_subexp] -> ivar
                        
                        addargs[k] = diff_add_k

    # process muls - any muls that weren't repeated might contain
    # subpatterns that are repeated, e.g. x*y*z and x*y have x*y in common
    # *assumes that there are no non-commutative parts*
    muls = list(ordered(muls))
    mulargs = [set(a.args) for a in muls]
    for i in xrange(len(mulargs)):
        for j in xrange(i + 1, len(mulargs)):
            com = mulargs[i].intersection(mulargs[j])
            if len(com) > 1:
                
                mul_subexp = Mul(*com)
                
                diff_mul_i = mulargs[i].difference(com)
                diff_mul_j = mulargs[j].difference(com)
                
                if mul_subexp in subexp_iv:
                    ivar = subexp_iv[mul_subexp]
                else:
                    ivar = next(tmp_symbols)
                    subexp_iv[mul_subexp] = ivar
                    
                if diff_mul_i:
                    newmul = Mul(ivar,*diff_mul_i)
                    subexp_iv[newmul] = subexp_iv.pop(muls[i])
                    muls[i] = newmul
                #else mul_i is itself subexp_iv[mul_subexp] -> ivar
                
                if diff_mul_j:
                    newmul = Mul(ivar,*diff_mul_j)
                    subexp_iv[newmul] = subexp_iv.pop(muls[j])
                    muls[j] = newmul
                #else mul_j is itself subexp_iv[mul_subexp] -> ivar
                        
                mulargs[i] = diff_mul_i
                mulargs[j] = diff_mul_j
                
                for k in xrange(j + 1, len(mulargs)):
                    if com.issubset(mulargs[k]):
                        
                        diff_mul_k = mulargs[k].difference(com)
                        
                        if diff_mul_k:
                            newmul = Mul(ivar,*diff_mul_k)
                            subexp_iv[newmul] = subexp_iv.pop(muls[k])
                            muls[k] = newmul
                        #else mul_k is itself subexp_iv[mul_subexp] -> ivar
                        
                        mulargs[k] = diff_mul_k
    
    # Find all of the repeated subexpressions.
    
    ivar_se = {iv:se for se,iv in subexp_iv.iteritems()}
    
    used_ivs = set()
    repeated = set()
    
    def _find_repeated_subexprs(subexpr):
        if subexpr.is_Atom:
            symbs = [subexpr]
        else:
            symbs = subexpr.args
        for symb in symbs:
            if symb in ivar_se:
                if symb not in used_ivs:
                    _find_repeated_subexprs(ivar_se[symb])
                    used_ivs.add(symb)
                else:
                    repeated.add(symb)
    
    for expr in tmp_exprs:
        _find_repeated_subexprs(expr)
        
    # Substitute symbols for all of the repeated subexpressions.
    # remove temporary replacements that weren't used more than once
    
    tmpivs_ivs = dict()
    ordered_iv_se = OrderedDict()
    
    def _get_subexprs(args):
        args = list(args)
        for i,symb in enumerate(args):
            if symb in ivar_se:
                if symb in tmpivs_ivs:
                    args[i] = tmpivs_ivs[symb]
                else:
                    subexpr = ivar_se[symb]
                    subexpr = type(subexpr)(*_get_subexprs(subexpr.args))
                    if symb in repeated:
                        ivar = next(symbols)
                        ordered_iv_se[ivar] = subexpr
                        tmpivs_ivs[symb] = ivar
                        args[i] = ivar
                    else:
                        args[i] = subexpr
        return args

    out_exprs = _get_subexprs(tmp_exprs)    
    
    
            
    # Postprocess the expressions to return the expressions to canonical form.
    ordered_iv_se_notopt = ordered_iv_se
    ordered_iv_se = OrderedDict()
    for i, (ivar, subexpr) in enumerate(ordered_iv_se_notopt.items()):
        subexpr = postprocess_for_cse(subexpr, optimizations)
        ordered_iv_se[ivar] = subexpr
    out_exprs = [postprocess_for_cse(e, optimizations) for e in out_exprs]

    if isinstance(exprs, Matrix):
        out_exprs = Matrix(exprs.rows, exprs.cols, out_exprs)
    if postprocess is None:
        return ordered_iv_se.items(), out_exprs
    return postprocess(ordered_iv_se.items(), out_exprs)

