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
        self._muls = list()
        self._adds = list()
        
        
    def _parse_mul(self, mul):
            
        mulA = set(mul.args)
            
        for i, mulB in enumerate(self._muls):
            
            com = mulA.intersection(mulB)
            if len(com) > 1:
                
                diff_mulA = mulA.difference(com)
                diff_mulB = mulB.difference(com)
                
                if not diff_mulA: # mulA is strict subset of mulB
                    
                    ivar = next(self._tmp_symbols)
                    self._subexp_iv[sympy.Mul(*mulA)] = ivar
                    self._muls.append(mulA)
                    
                    mulB = diff_mulB
                    mulB.add(ivar)
                    self._subexp_iv[sympy.Mul(*mulB)] = self._subexp_iv.pop(sympy.Mul(*self._muls[i]))
                    self._muls[i] = mulB
                    
                    return ivar
                
                elif not diff_mulB: # mulB is strict subset of mulA
                    
                    mulA = diff_mulA
                    mulA.add(self._subexp_iv[sympy.Mul(*mulB)])
                    
                    ivar = self._subexp_iv.get(sympy.Mul(*mulA), None)
                    if ivar:
                        return ivar
                    
                    if len(mulA) == 2:
                        break
                
                else: # mulA != com != mulB
                    
                    ivar = next(self._tmp_symbols)
                    self._subexp_iv[sympy.Mul(*com)] = ivar
                    self._muls.append(com)
                    
                    mulB = diff_mulB
                    mulB.add(ivar)
                    self._subexp_iv[sympy.Mul(*mulB)] = self._subexp_iv.pop(sympy.Mul(*self._muls[i]))
                    self._muls[i] = mulB
                    
                    mulA = diff_mulA
                    mulA.add(ivar)
                    if len(mulA) == 2:
                        break
        
        ivar = next(self._tmp_symbols)
        self._subexp_iv[sympy.Mul(*mulA)] = ivar
        self._muls.append(mulA)
        
        return ivar
    
    def _parse_add(self, add):
            
        addA = set(add.args)
            
        for i, addB in enumerate(self._adds):
            
            com = addA.intersection(addB)
            if len(com) > 1:
                
                diff_addA = addA.difference(com)
                diff_addB = addB.difference(com)
                
                if not diff_addA: # addA is strict subset of addB
                    
                    ivar = next(self._tmp_symbols)
                    self._subexp_iv[sympy.Add(*addA)] = ivar
                    self._adds.append(addA)
                    
                    addB = diff_addB
                    addB.add(ivar)
                    self._subexp_iv[sympy.Add(*addB)] = self._subexp_iv.pop(sympy.Add(*self._adds[i]))
                    self._adds[i] = addB
                    
                    return ivar
                
                elif not diff_addB: # addB is strict subset of addA
                    
                    addA = diff_addA
                    addA.add(self._subexp_iv[sympy.Add(*addB)])
                    
                    ivar = self._subexp_iv.get(sympy.Add(*addA), None)
                    if ivar:
                        return ivar
                    
                    if len(addA) == 2:
                        break
                
                else: # addA != com != addB
                    
                    ivar = next(self._tmp_symbols)
                    self._subexp_iv[sympy.Add(*com)] = ivar
                    self._adds.append(com)
                    
                    addB = diff_addB
                    addB.add(ivar)
                    self._subexp_iv[sympy.Add(*addB)] = self._subexp_iv.pop(sympy.Add(*self._adds[i]))
                    self._adds[i] = addB
                    
                    addA = diff_addA
                    addA.add(ivar)
                    if len(addA) == 2:
                        break
        
        ivar = next(self._tmp_symbols)
        self._subexp_iv[sympy.Add(*addA)] = ivar
        self._adds.append(addA)
        
        return ivar
        
    
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
            return self._parse_mul(subexpr)
        elif subexpr.is_Add:
            return self._parse_add(subexpr)
        else:
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
        
    
    def get(self, exprs=None, symbols=None):
        
        if symbols is None:
            symbols = sympy.utilities.iterables.numbered_symbols()
        else:
            # In case we get passed an iterable with an __iter__ method instead of
            # an actual iterator.
            symbols = iter(symbols)
        
        #self._process_adds_and_muls()
        
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



