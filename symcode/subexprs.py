
import sympy
import sympy.utilities

import collections

class Subexprs(object):
       
  def __init__(self, mode='unique_ops', ivars_name='tmp'):
    
    self.symbols = sympy.utilities.iterables.numbered_symbols(ivars_name, start=0, real=True)
    self.subexprs_dict = dict()
    self.adds = dict()
    self.muls = dict()
    
    if mode == 'unique_ops':
      self._collect_func = self._collect_uniqueops
    elif mode == 'whole_exprs':
      self._collect_func = self._collect_exprs
    else:
      raise Exception("No '%s' sub-expression collection mode known."%mode)
    
  @property
  def subexprs(self): return self.get_subexprs()
  
  class GetSubexprs(object):
    
    def __init__(self, expr, subexprs_invdict, subexprs_ordereddict):
      self.subexprs_invdict = subexprs_invdict
      self.subexprs_ordereddict = subexprs_ordereddict
      if expr is not None:
        self._subexprs(expr)
      else:
        for symb in self.subexprs_invdict:
          self._subexprs(symb)
        
    def _subexprs(self, expr):
      for symb in expr.free_symbols:
        if symb not in self.subexprs_ordereddict and symb in self.subexprs_invdict:
          subexpr = self.subexprs_invdict[symb]
          self._subexprs(subexpr)
          self.subexprs_ordereddict[symb] = subexpr
            
  def get_subexprs(self, out_exprs=[None]):
    subexprs_invdict = {v:k for k,v in self.subexprs_dict.items()}
    subexprs_ordereddict = collections.OrderedDict()
    if isinstance(out_exprs, sympy.Basic): # if only one expression is passed
      out_exprs = [out_exprs]
    for expr in out_exprs:
      self.GetSubexprs(expr, subexprs_invdict, subexprs_ordereddict)
    return subexprs_ordereddict.items()
    
    
  def _collect_exprs(self, expr):
    if expr.is_Atom:
      return expr
    else:
      new_ivar = next(self.symbols)
      self.subexprs_dict[expr] = new_ivar
      return new_ivar
    
    
  def _collect_op(self, expr):
    if expr in self.subexprs_dict:
      return self.subexprs_dict[expr]
    else:
      new_ivar = next(self.symbols)
      self.subexprs_dict[expr] = new_ivar
      if isinstance(expr, sympy.Mul):
        self.muls[expr] = new_ivar
      if isinstance(expr, sympy.Add):
        self.adds[expr] = new_ivar
      return new_ivar
  
  
  def _collect_uniqueops(self, expr):
    if expr.is_Atom:
        return expr
    else:
        new_args = []
        for arg in expr.args:
          new_args.append( self._collect_uniqueops(arg) )
        return self._collect_op(type(expr)(*new_args))
    
    
  def collect(self, exprs):
    
    if isinstance(exprs, sympy.Basic): # if only one expression is passed
      exprs = [exprs]
      is_single_expr = True
    else:
      is_single_expr = False
    
    out_exprs = list()
    
    out_exprs.extend(map(self._collect_func, exprs))
          
    if is_single_expr:
      return out_exprs[0]
    elif isinstance(exprs, sympy.Matrix):
      return sympy.Matrix(exprs.rows, exprs.cols, out_exprs)
    else:
      return out_exprs
