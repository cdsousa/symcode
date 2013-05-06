import sympy
import sympy.utilities
from sympy.simplify.cse_main import cse_optimizations, preprocess_for_cse, postprocess_for_cse

import collections


class Subexprs(object):
        
    def __init__(self, optimizations=None, postprocess=None):
        
        if optimizations is None:
            # Pull out the default here just in case there are some weird
            # manipulations of the module-level list in some other thread.
            optimizations = list(cse_optimizations)
        self._optimizations = optimizations
        self._postprocess = postprocess
        
        self._tmp_symbols = sympy.utilities.iterables.numbered_symbols('tmp', start=0, real=True)
        
        self._subexp_iv = dict()
        self._muls = set()
        self._adds = set()
        
    
    def _parse(self, expr):
            
        if expr.is_Atom:
            # Exclude atoms, since there is no point in renaming them.
            return expr
        
        if sympy.iterables.iterable(expr):
            return expr
        
        subexpr = type(expr)(*map(self._parse, expr.args))

        if subexpr in self._subexp_iv:
            return self._subexp_iv[subexpr]
        
        if subexpr.is_Mul:
            self._muls.add(subexpr)
        elif subexpr.is_Add:
            self._adds.add(subexpr)

        ivar = next(self._tmp_symbols)
        self._subexp_iv[subexpr] = ivar
        
        return ivar


    def collect(self, exprs):
        
        if isinstance(exprs, sympy.Basic): # if only one expression is passed
            exprs = [exprs]
            is_single_expr = True
        else:
            is_single_expr = False
        
        # Preprocess the expressions to give us better optimization opportunities.
        prep_exprs = [preprocess_for_cse(e, self._optimizations) for e in exprs]
        
        out_exprs = map(self._parse, prep_exprs)
            
        if is_single_expr:
            return out_exprs[0]
        elif isinstance(exprs, sympy.Matrix):
            return sympy.Matrix(exprs.rows, exprs.cols, out_exprs)
        else:
            return out_exprs
        
    
    
    def _process_adss_and_muls(self):
        
        # process adds - any adds that weren't repeated might contain
        # subpatterns that are repeated, e.g. x+y+z and x+y have x+y in common
        adds = list(sympy.ordered(self._adds))
        addargs = [set(a.args) for a in adds]
        for i in xrange(len(addargs)):
            for j in xrange(i + 1, len(addargs)):
                com = addargs[i].intersection(addargs[j])
                if len(com) > 1:
                    
                    add_subexp = sympy.Add(*com)
                    
                    diff_add_i = addargs[i].difference(com)
                    diff_add_j = addargs[j].difference(com)
                    
                    if add_subexp in self._subexp_iv:
                        ivar = self._subexp_iv[add_subexp]
                    else:
                        ivar = next(self._tmp_symbols)
                        self._subexp_iv[add_subexp] = ivar
                        
                    if diff_add_i:
                        newadd = sympy.Add(ivar,*diff_add_i)
                        self._subexp_iv[newadd] = self._subexp_iv.pop(adds[i])
                        self._adds.remove(adds[i])
                        self._adds.add(newadd)
                        adds[i] = newadd
                    #else add_i is itself self._subexp_iv[add_subexp] -> ivar
                    
                    if diff_add_j:
                        newadd = sympy.Add(ivar,*diff_add_j)
                        self._subexp_iv[newadd] = self._subexp_iv.pop(adds[j])
                        self._adds.remove(adds[j])
                        self._adds.add(newadd)
                        adds[j] = newadd
                    #else add_j is itself self._subexp_iv[add_subexp] -> ivar
                            
                    addargs[i] = diff_add_i
                    addargs[j] = diff_add_j
                    
                    for k in xrange(j + 1, len(addargs)):
                        if com.issubset(addargs[k]):
                            
                            diff_add_k = addargs[k].difference(com)
                            
                            if diff_add_k:
                                newadd = sympy.Add(ivar,*diff_add_k)
                                self._subexp_iv[newadd] = self._subexp_iv.pop(adds[k])
                                self._adds.remove(adds[k])
                                self._adds.add(newadd)
                                adds[k] = newadd
                            #else add_k is itself self._subexp_iv[add_subexp] -> ivar
                            
                            addargs[k] = diff_add_k

        # process muls - any muls that weren't repeated might contain
        # subpatterns that are repeated, e.g. x*y*z and x*y have x*y in common
        # *assumes that there are no non-commutative parts*
        muls = list(sympy.ordered(self._muls))
        mulargs = [set(a.args) for a in muls]
        for i in xrange(len(mulargs)):
            for j in xrange(i + 1, len(mulargs)):
                com = mulargs[i].intersection(mulargs[j])
                if len(com) > 1:
                    
                    mul_subexp = sympy.Mul(*com)
                    
                    diff_mul_i = mulargs[i].difference(com)
                    diff_mul_j = mulargs[j].difference(com)
                    
                    if mul_subexp in self._subexp_iv:
                        ivar = self._subexp_iv[mul_subexp]
                    else:
                        ivar = next(self._tmp_symbols)
                        self._subexp_iv[mul_subexp] = ivar
                        
                    if diff_mul_i:
                        newmul = sympy.Mul(ivar,*diff_mul_i)
                        self._subexp_iv[newmul] = self._subexp_iv.pop(muls[i])
                        self._muls.remove(muls[i])
                        self._muls.add(newmul)
                        muls[i] = newmul
                    #else mul_i is itself self._subexp_iv[mul_subexp] -> ivar
                    
                    if diff_mul_j:
                        newmul = sympy.Mul(ivar,*diff_mul_j)
                        self._subexp_iv[newmul] = self._subexp_iv.pop(muls[j])
                        self._muls.remove(muls[j])
                        self._muls.add(newmul)
                        muls[j] = newmul
                    #else mul_j is itself self._subexp_iv[mul_subexp] -> ivar
                            
                    mulargs[i] = diff_mul_i
                    mulargs[j] = diff_mul_j
                    
                    for k in xrange(j + 1, len(mulargs)):
                        if com.issubset(mulargs[k]):
                            
                            diff_mul_k = mulargs[k].difference(com)
                            
                            if diff_mul_k:
                                newmul = sympy.Mul(ivar,*diff_mul_k)
                                self._subexp_iv[newmul] = self._subexp_iv.pop(muls[k])
                                self._muls.remove(muls[k])
                                self._muls.add(newmul)
                                muls[k] = newmul
                            #else mul_k is itself self._subexp_iv[mul_subexp] -> ivar
                            
                            mulargs[k] = diff_mul_k
                            

    def get(self, exprs=None, symbols=None):
        
        if symbols is None:
            symbols = sympy.utilities.iterables.numbered_symbols()
        else:
            # In case we get passed an iterable with an __iter__ method instead of
            # an actual iterator.
            symbols = iter(symbols)
        
        self._process_adss_and_muls()
        
        # Find all of the repeated subexpressions.
        
        ivar_se = {iv:se for se,iv in self._subexp_iv.iteritems()}
        
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
        
        for expr in exprs:
            _find_repeated_subexprs(expr)
            
        # Substitute symbols for all of the repeated subexpressions.
        # remove temporary replacements that weren't used more than once
        
        tmpivs_ivs = dict()
        ordered_iv_se = collections.OrderedDict()
        
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

        out_exprs = _get_subexprs(exprs)    
        
        # Postprocess the expressions to return the expressions to canonical form.
        ordered_iv_se_notopt = ordered_iv_se
        ordered_iv_se = collections.OrderedDict()
        for i, (ivar, subexpr) in enumerate(ordered_iv_se_notopt.items()):
            subexpr = postprocess_for_cse(subexpr, self._optimizations)
            ordered_iv_se[ivar] = subexpr
        out_exprs = [postprocess_for_cse(e, self._optimizations) for e in out_exprs]

        if isinstance(exprs, sympy.Matrix):
            out_exprs = sympy.Matrix(exprs.rows, exprs.cols, out_exprs)
        if self._postprocess is None:
            return ordered_iv_se.items(), out_exprs
        return self._postprocess(ordered_iv_se.items(), out_exprs)



def fast_cse(exprs, symbols='aux'):
    se = Subexprs()
    return se.get(se.collect(exprs))



