
import sympy
import sympy.utilities

import collections

class Cse(object):
       
  def __init__(self, ivars_name='cse', opt_muladd=True):
    
    self._symbols = sympy.utilities.iterables.numbered_symbols(ivars_name, start=0, real=True)
    
    self._se_iv = dict()
    
    self.opt_muladd = opt_muladd
    
    self.muls_2a = dict()
    self.muls_ma = dict()
    self.adds_2a = dict()
    self.adds_ma = dict()
    
     
  def _parse(self, expr):
    
    if expr.is_Atom:
      return expr
      
    else:
      se = type(expr)(*map(self._parse, expr.args))
        
      if se in self._se_iv:
        
        return self._se_iv[se]
      
      else:
        
        
        if self.opt_muladd and se.is_Mul:
          
          args = se.args
          if len(args) == 2:
            
            new_ivar = next(self._symbols)
            self._se_iv[se] = new_ivar
            self.muls_2a[se] = new_ivar
            
            args_set = set(args)
            seB_change = [seB for seB in self.muls_ma if len(args_set.intersection(set(seB.args))) == 2]
            #print("%s=%s"%(new_ivar,se))
            for seB in seB_change:
              new_seB = seB.subs(se,new_ivar)
              seB_ivar = self._se_iv.pop(seB)
              self._se_iv[new_seB] = seB_ivar
              self.muls_ma.pop(seB)
              if len(new_seB.args) == 2: self.muls_2a[new_seB] = seB_ivar
              else: self.muls_ma[new_seB] = seB_ivar
              #print("  %s=%s  -->  %s=%s"%(seB_ivar,seB,self._se_iv[new_seB],new_seB))
            
            return new_ivar
              
              
          else:
            
            args_set = set(args)     
            
            for seB in self.muls_2a:
              if len(args_set.intersection(set(seB.args))) == 2:
                se = se.subs( seB, self.muls_2a[seB] )
                if se in self._se_iv:
                  return self._se_iv[se]
                elif len(se.args) == 2:
                  new_ivar = next(self._symbols)
                  self._se_iv[se] = new_ivar
                  self.muls_2a[se] = new_ivar
                  return new_ivar
                else:
                  return self._parse(se)
                
            for seB in self.muls_ma:
              intersect = args_set.intersection(set(seB.args))
              intersect_len = len(intersect)
              if intersect_len >= 2:
                intersect_se = sympy.Mul(*intersect)
                if intersect_se == seB:
                  intersect_ivar = self.muls_ma[seB]
                else:
                  intersect_ivar = next(self._symbols)
                  self._se_iv[intersect_se] = intersect_ivar
                  if intersect_len > 2:
                    self.muls_ma[intersect_se] = intersect_ivar
                  else:
                    self.muls_2a[intersect_se] = intersect_ivar
                  # new seB:
                  seB_ivar = self._se_iv.pop(seB)
                  self.muls_ma.pop(seB)
                  new_seB = seB.subs(intersect_se,intersect_ivar)
                  self._se_iv[new_seB] = seB_ivar
                  if len(new_seB.args) > 2:
                    self.muls_ma[new_seB] = seB_ivar
                  else:
                    self.muls_2a[new_seB] = seB_ivar
                # new se
                if intersect_se == se:
                  return intersect_ivar
                else:
                  new_se = se.subs(intersect_se,intersect_ivar)
                  if len(new_se.args) == 2:
                    new_ivar = next(self._symbols)
                    self._se_iv[new_se] = new_ivar
                    self.muls_ma[new_se] = new_ivar
                    return new_ivar
                  else:
                    #print('check symcode.subses.Subses._parse()')
                    return self._parse(new_se)
          
            new_ivar = next(self._symbols)
            self._se_iv[se] = new_ivar
            self.muls_ma[se] = new_ivar
            return new_ivar
              
            
        elif self.opt_muladd and se.is_Add:
          
          args = se.args
          if len(args) == 2:
            
            new_ivar = next(self._symbols)
            self._se_iv[se] = new_ivar
            self.adds_2a[se] = new_ivar
            
            args_set = set(args)
            seB_change = [seB for seB in self.adds_ma if len(args_set.intersection(set(seB.args))) == 2]
            #print("%s=%s"%(new_ivar,se))
            for seB in seB_change:
              new_seB = seB.subs(se,new_ivar)
              seB_ivar = self._se_iv.pop(seB)
              self._se_iv[new_seB] = seB_ivar
              self.adds_ma.pop(seB)
              if len(new_seB.args) == 2: self.adds_2a[new_seB] = seB_ivar
              else: self.adds_ma[new_seB] = seB_ivar
              #print("  %s=%s  -->  %s=%s"%(seB_ivar,seB,self._se_iv[new_seB],new_seB))
            
            return new_ivar
              
              
          else:
            
            args_set = set(args)     
            
            for seB in self.adds_2a:
              if len(args_set.intersection(set(seB.args))) == 2:
                se = se.subs( seB, self.adds_2a[seB] )
                if se in self._se_iv:
                  return self._se_iv[se]
                elif len(se.args) == 2:
                  new_ivar = next(self._symbols)
                  self._se_iv[se] = new_ivar
                  self.adds_2a[se] = new_ivar
                  return new_ivar
                else:
                  return self._parse(se)
                
            for seB in self.adds_ma:
              intersect = args_set.intersection(set(seB.args))
              intersect_len = len(intersect)
              if intersect_len >= 2:
                intersect_se = sympy.Add(*intersect)
                if intersect_se == seB:
                  intersect_ivar = self.adds_ma[seB]
                else:
                  intersect_ivar = next(self._symbols)
                  self._se_iv[intersect_se] = intersect_ivar
                  if intersect_len > 2:
                    self.adds_ma[intersect_se] = intersect_ivar
                  else:
                    self.adds_2a[intersect_se] = intersect_ivar
                  # new seB:
                  seB_ivar = self._se_iv.pop(seB)
                  self.adds_ma.pop(seB)
                  new_seB = seB.subs(intersect_se,intersect_ivar)
                  self._se_iv[new_seB] = seB_ivar
                  if len(new_seB.args) > 2:
                    self.adds_ma[new_seB] = seB_ivar
                  else:
                    self.adds_2a[new_seB] = seB_ivar
                # new se
                if intersect_se == se:
                  return intersect_ivar
                else:
                  new_se = se.subs(intersect_se,intersect_ivar)
                  if len(new_se.args) == 2:
                    new_ivar = next(self._symbols)
                    self._se_iv[new_se] = new_ivar
                    self.adds_ma[new_se] = new_ivar
                    return new_ivar
                  else:
                    return self._parse(new_se)
          
            new_ivar = next(self._symbols)
            self._se_iv[se] = new_ivar
            self.adds_ma[se] = new_ivar
            return new_ivar
              
            
        else:
          new_ivar = next(self._symbols)
          self._se_iv[se] = new_ivar
          return new_ivar



  def collect(self, exprs):
    
    if isinstance(exprs, sympy.Basic): # if only one expression is passed
      exprs = [exprs]
      is_single_expr = True
    else:
      is_single_expr = False
    
    out_exprs = map(self._parse, exprs)
          
    if is_single_expr:
      return out_exprs[0]
    elif isinstance(exprs, sympy.Matrix):
      return sympy.Matrix(exprs.rows, exprs.cols, out_exprs)
    else:
      return out_exprs
    
  
  
  
  def get(self, exprs=None):
    
    iv_se = {iv:se for se,iv in self._se_iv.iteritems()}
    
    if isinstance(exprs, sympy.Basic): # if only one expression is passed
      exprs = [exprs]
    elif exprs is None:
      exprs = iv_se.keys()
      
    
    used_ivs = set()
    used_morethanonce_ivs = set()
    
    def _find_used_subexprs(subexpr):
      if subexpr.is_Atom:
        symbs = [subexpr]
      else:
        symbs = subexpr.args
      for symb in symbs:
        if symb in iv_se:
          if symb not in used_ivs:
            _find_used_subexprs(iv_se[symb])
            used_ivs.add(symb)
          else:
            used_morethanonce_ivs.add(symb)
            
    for expr in exprs:
      _find_used_subexprs(expr)


    ordered_se_iv = collections.OrderedDict()
        
    def _get_subexprs(expr):
        subs = dict()
        for symb in expr.free_symbols:
          if symb in iv_se and symb not in ordered_se_iv:
              if symb in used_morethanonce_ivs:
                  subexpr = iv_se[symb]
                  new_expr = _get_subexprs(subexpr)
                  ordered_se_iv[symb] = new_expr
              else:
                  subexpr = iv_se[symb]
                  new_expr = _get_subexprs(subexpr)
                  subs[symb] = new_expr
        return expr.xreplace(subs)

    out_exprs = [_get_subexprs(expr) for expr in exprs]
    
    
    if isinstance(exprs, sympy.Matrix):
      out_exprs = sympy.Matrix(exprs.rows, exprs.cols, out_exprs)
    
    return (ordered_se_iv.items(), out_exprs)



def cse_c(exprs, ivars_name='cse', opt_muladd=True):
  cse_obj = Cse(ivars_name, opt_muladd)
  exprs = cse_obj.collect(exprs)
  return cse_obj.get(exprs)






""" Tools for doing common subexpression elimination.
"""
import difflib

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


def cse_f(exprs, symbols=None, optimizations=None, postprocess=None):
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
    
    _tmp_ivars = numbered_symbols('tmp')
    _subexp_iv = dict()
    _repeated = set()
    _muls = set()
    _adds = set()

    if symbols is None:
        symbols = numbered_symbols()
    else:
        # In case we get passed an iterable with an __iter__ method instead of
        # an actual iterator.
        symbols = iter(symbols)
    seen_subexp = set()
    muls = set()
    adds = set()
    to_eliminate = set()

    if optimizations is None:
        # Pull out the default here just in case there are some weird
        # manipulations of the module-level list in some other thread.
        optimizations = list(cse_optimizations)

    # Handle the case if just one expression was passed.
    if isinstance(exprs, Basic):
        exprs = [exprs]

    # Preprocess the expressions to give us better optimization opportunities.
    reduced_exprs = [preprocess_for_cse(e, optimizations) for e in exprs]


    def _collect(expr):

        if expr.is_Atom or iterable(expr):
            # Exclude atoms, since there is no point in renaming them.
            return expr
        
        subexpr = type(expr)(*map(_collect, expr.args))

        if subexpr in _subexp_iv:
            _repeated.add(subexpr)
            return _subexp_iv[subexpr]
        
        if subexpr.is_Mul:
            _muls.add(subexpr)
        elif subexpr.is_Add:
            _adds.add(subexpr)

        ivar = next(_tmp_ivars)
        _subexp_iv[subexpr] = ivar
        
        return ivar
    
    _tmp_exprs = list()
    for expr in reduced_exprs:
        if isinstance(expr, Basic):
            _tmp_exprs.append(_collect(expr))
        else:
            _tmp_exprs.append(expr)
    
    # Find all of the repeated subexpressions.
    for expr in reduced_exprs:
        if not isinstance(expr, Basic):
            continue
        pt = preorder_traversal(expr)
        for subtree in pt:

            inv = 1/subtree if subtree.is_Pow else None

            if subtree.is_Atom or iterable(subtree) or inv and inv.is_Atom:
                # Exclude atoms, since there is no point in renaming them.
                continue

            if subtree in seen_subexp:
                if inv and _coeff_isneg(subtree.exp):
                    # save the form with positive exponent
                    subtree = inv
                to_eliminate.add(subtree)
                pt.skip()
                continue

            if inv and inv in seen_subexp:
                if _coeff_isneg(subtree.exp):
                    # save the form with positive exponent
                    subtree = inv
                to_eliminate.add(subtree)
                pt.skip()
                continue
            elif subtree.is_Mul:
                muls.add(subtree)
            elif subtree.is_Add:
                adds.add(subtree)

            seen_subexp.add(subtree)
    
    _adds = [set(a.args) for a in ordered(_adds)]
    for i in xrange(len(_adds)):
        for j in xrange(i + 1, len(_adds)):
            com = _adds[i].intersection(_adds[j])
            if len(com) > 1:
                
                subadd = Add(*com)
                _repeated.add(subadd) 
                
                diff_add_i = _adds[i].difference(com)
                diff_add_j = _adds[j].difference(com)
                
                if subadd in _subexp_iv:
                    ivar = _subexp_iv[subadd]
                else:
                    ivar = next(_tmp_ivars)
                    
                if diff_add_i:
                    _subexp_iv[Add(ivar,*diff_add_i)] = _subexp_iv.pop(Add(*_adds[i]))
                #else add_i is itself _subexp_iv[subadd] -> ivar
                
                if diff_add_j:
                    _subexp_iv[Add(ivar,*diff_add_j)] = _subexp_iv.pop(Add(*_adds[j]))
                #else add_j is itself _subexp_iv[subadd] -> ivar
                        
                _adds[i] = diff_add_i
                _adds[j] = diff_add_j
                
                for k in xrange(j + 1, len(_adds)):
                    if com.issubset(_adds[k]):
                        
                        diff_add_k = _adds[k].difference(com)
                        
                        if diff_add_k:
                            _subexp_iv[Add(ivar,*diff_add_k)] = _subexp_iv.pop(Add(*_adds[k]))
                        #else add_k is itself _subexp_iv[subadd] -> ivar
                        
                        _adds[k] = diff_add_k
    
    
    
    # process adds - any adds that weren't repeated might contain
    # subpatterns that are repeated, e.g. x+y+z and x+y have x+y in common
    adds = [set(a.args) for a in ordered(adds)]
    for i in xrange(len(adds)):
        for j in xrange(i + 1, len(adds)):
            com = adds[i].intersection(adds[j])
            if len(com) > 1:
                to_eliminate.add(Add(*com))

                # remove this set of symbols so it doesn't appear again
                adds[i] = adds[i].difference(com)
                adds[j] = adds[j].difference(com)
                for k in xrange(j + 1, len(adds)):
                    if not com.difference(adds[k]):
                        adds[k] = adds[k].difference(com)

    # process muls - any muls that weren't repeated might contain
    # subpatterns that are repeated, e.g. x*y*z and x*y have x*y in common

    # use SequenceMatcher on the nc part to find the longest common expression
    # in common between the two nc parts
    sm = difflib.SequenceMatcher()

    muls = [a.args_cnc(cset=True) for a in ordered(muls)]
    for i in xrange(len(muls)):
        if muls[i][1]:
            sm.set_seq1(muls[i][1])
        for j in xrange(i + 1, len(muls)):
            # the commutative part in common
            ccom = muls[i][0].intersection(muls[j][0])

            # the non-commutative part in common
            if muls[i][1] and muls[j][1]:
                # see if there is any chance of an nc match
                ncom = set(muls[i][1]).intersection(set(muls[j][1]))
                if len(ccom) + len(ncom) < 2:
                    continue

                # now work harder to find the match
                sm.set_seq2(muls[j][1])
                i1, _, n = sm.find_longest_match(0, len(muls[i][1]),
                                                 0, len(muls[j][1]))
                ncom = muls[i][1][i1:i1 + n]
            else:
                ncom = []

            com = list(ccom) + ncom
            if len(com) < 2:
                continue

            to_eliminate.add(Mul(*com))

            # remove ccom from all if there was no ncom; to update the nc part
            # would require finding the subexpr and then replacing it with a
            # dummy to keep bounding nc symbols from being identified as a
            # subexpr, e.g. removing B*C from A*B*C*D might allow A*D to be
            # identified as a subexpr which would not be right.
            if not ncom:
                muls[i][0] = muls[i][0].difference(ccom)
                for k in xrange(j, len(muls)):
                    if not ccom.difference(muls[k][0]):
                        muls[k][0] = muls[k][0].difference(ccom)

    # make to_eliminate canonical; we will prefer non-Muls to Muls
    # so select them first (non-Muls will have False for is_Mul and will
    # be first in the ordering.
    to_eliminate = list(ordered(to_eliminate, lambda _: _.is_Mul))

    # Substitute symbols for all of the repeated subexpressions.
    replacements = []
    reduced_exprs = list(reduced_exprs)
    hit = True
    for i, subtree in enumerate(to_eliminate):
        if hit:
            sym = symbols.next()
        hit = False
        if subtree.is_Pow and subtree.exp.is_Rational:
            update = lambda x: x.xreplace({subtree: sym, 1/subtree: 1/sym})
        else:
            update = lambda x: x.subs(subtree, sym)
        # Make the substitution in all of the target expressions.
        for j, expr in enumerate(reduced_exprs):
            old = reduced_exprs[j]
            reduced_exprs[j] = update(expr)
            hit = hit or (old != reduced_exprs[j])
        # Make the substitution in all of the subsequent substitutions.
        for j in range(i + 1, len(to_eliminate)):
            old = to_eliminate[j]
            to_eliminate[j] = update(to_eliminate[j])
            hit = hit or (old != to_eliminate[j])
        if hit:
            replacements.append((sym, subtree))

    # Postprocess the expressions to return the expressions to canonical form.
    for i, (sym, subtree) in enumerate(replacements):
        subtree = postprocess_for_cse(subtree, optimizations)
        replacements[i] = (sym, subtree)
    reduced_exprs = [postprocess_for_cse(e, optimizations)
        for e in reduced_exprs]

    # remove replacements that weren't used more than once
    _remove_singletons(replacements, reduced_exprs)

    if isinstance(exprs, Matrix):
        reduced_exprs = [Matrix(exprs.rows, exprs.cols, reduced_exprs)]
    if postprocess is None:
        return replacements, reduced_exprs
    return postprocess(replacements, reduced_exprs)

