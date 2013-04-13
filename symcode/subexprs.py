
import sympy
import sympy.utilities

import collections

class Subexprs(object):
       
  def __init__(self, ivars_name='tmp', comn_subexpr_elim=True, opt_muladd=True):
    
    self.symbols = sympy.utilities.iterables.numbered_symbols(ivars_name, start=0, real=True)
    self.subexprs_dict = dict()
    
    self.opt_muladd = opt_muladd
    
    self.muls_2a = dict()
    self.muls_ma = dict()
    self.adds_2a = dict()
    self.adds_ma = dict()
    
    if comn_subexpr_elim:
      self._collect_func = self._collect_unique_ops
    else:
      self._collect_func = self._collect_expr
    
    
    
  @property
  def subexprs(self): return self.get_subexprs()
  
            
  def get_subexprs(self, out_exprs=None):
    subexprs_invdict = {v:k for k,v in self.subexprs_dict.items()}
    subexprs_ordereddict = collections.OrderedDict()
    def _subexprs(expr):
      for symb in expr.free_symbols:
        if symb not in subexprs_ordereddict and symb in subexprs_invdict:
          subexpr = subexprs_invdict[symb]
          _subexprs(subexpr)
          subexprs_ordereddict[symb] = subexpr
    if isinstance(out_exprs, sympy.Basic): # if only one expression is passed
      out_exprs = [out_exprs]
    if out_exprs is None:
      out_exprs = subexprs_invdict.keys()
    for expr in out_exprs:
      _subexprs(expr)
    return subexprs_ordereddict.items()
    
   
  
  def _collect_unique_ops(self, expr):
    if expr.is_Atom:
        return expr
    else:
        new_args = []
        for arg in expr.args:
          new_args.append( self._collect_unique_ops(arg) )
        return self._collect_op(type(expr)(*new_args))
  
  def _collect_op(self, expr):
    if expr in self.subexprs_dict:
      return self.subexprs_dict[expr]
    else:
      
      if self.opt_muladd and expr.is_Mul:
        
        args = expr.args
        if len(args) == 2:
          
          new_ivar = next(self.symbols)
          self.subexprs_dict[expr] = new_ivar
          self.muls_2a[expr] = new_ivar
          
          args_set = set(args)
          exprB_change = [exprB for exprB in self.muls_ma if len(args_set.intersection(set(exprB.args))) == 2]
          #print("%s=%s"%(new_ivar,expr))
          for exprB in exprB_change:
            new_exprB = exprB.subs(expr,new_ivar)
            exprB_ivar = self.subexprs_dict.pop(exprB)
            self.subexprs_dict[new_exprB] = exprB_ivar
            self.muls_ma.pop(exprB)
            if len(new_exprB.args) == 2: self.muls_2a[new_exprB] = exprB_ivar
            else: self.muls_ma[new_exprB] = exprB_ivar
            #print("  %s=%s  -->  %s=%s"%(exprB_ivar,exprB,self.subexprs_dict[new_exprB],new_exprB))
          
          return new_ivar
            
            
        else:
          
          args_set = set(args)     
          
          for exprB in self.muls_2a:
            if len(args_set.intersection(set(exprB.args))) == 2:
              expr = expr.subs( exprB, self.muls_2a[exprB] )
              if expr in self.subexprs_dict:
                return self.subexprs_dict[expr]
              elif len(expr.args) == 2:
                new_ivar = next(self.symbols)
                self.subexprs_dict[expr] = new_ivar
                self.muls_2a[expr] = new_ivar
                return new_ivar
              else:
                return self._collect_op(expr)
              
          for exprB in self.muls_ma:
            intersect = args_set.intersection(set(exprB.args))
            intersect_len = len(intersect)
            if intersect_len >= 2:
              intersect_expr = sympy.Mul(*intersect)
              if intersect_expr == exprB:
                intersect_ivar = self.muls_ma[exprB]
              else:
                intersect_ivar = next(self.symbols)
                self.subexprs_dict[intersect_expr] = intersect_ivar
                if intersect_len > 2:
                  self.muls_ma[intersect_expr] = intersect_ivar
                else:
                  self.muls_2a[intersect_expr] = intersect_ivar
                # new exprB:
                exprB_ivar = self.subexprs_dict.pop(exprB)
                self.muls_ma.pop(exprB)
                new_exprB = exprB.subs(intersect_expr,intersect_ivar)
                self.subexprs_dict[new_exprB] = exprB_ivar
                if len(new_exprB.args) > 2:
                  self.muls_ma[new_exprB] = exprB_ivar
                else:
                  self.muls_2a[new_exprB] = exprB_ivar
              # new expr
              if intersect_expr == expr:
                return intersect_ivar
              else:
                new_expr = expr.subs(intersect_expr,intersect_ivar)
                if len(new_expr.args) == 2:
                  new_ivar = next(self.symbols)
                  self.subexprs_dict[new_expr] = new_ivar
                  self.muls_ma[new_expr] = new_ivar
                  return new_ivar
                else:
                  print('check symcode.subexprs.Subexprs._collect_op()')
                  return self._collect_op(new_expr)
        
          new_ivar = next(self.symbols)
          self.subexprs_dict[expr] = new_ivar
          self.muls_ma[expr] = new_ivar
          return new_ivar
            
          
      elif self.opt_muladd and expr.is_Add:
        
        args = expr.args
        if len(args) == 2:
          
          new_ivar = next(self.symbols)
          self.subexprs_dict[expr] = new_ivar
          self.adds_2a[expr] = new_ivar
          
          args_set = set(args)
          exprB_change = [exprB for exprB in self.adds_ma if len(args_set.intersection(set(exprB.args))) == 2]
          #print("%s=%s"%(new_ivar,expr))
          for exprB in exprB_change:
            new_exprB = exprB.subs(expr,new_ivar)
            exprB_ivar = self.subexprs_dict.pop(exprB)
            self.subexprs_dict[new_exprB] = exprB_ivar
            self.adds_ma.pop(exprB)
            if len(new_exprB.args) == 2: self.adds_2a[new_exprB] = exprB_ivar
            else: self.adds_ma[new_exprB] = exprB_ivar
            #print("  %s=%s  -->  %s=%s"%(exprB_ivar,exprB,self.subexprs_dict[new_exprB],new_exprB))
          
          return new_ivar
            
            
        else:
          
          args_set = set(args)     
          
          for exprB in self.adds_2a:
            if len(args_set.intersection(set(exprB.args))) == 2:
              expr = expr.subs( exprB, self.adds_2a[exprB] )
              if expr in self.subexprs_dict:
                return self.subexprs_dict[expr]
              elif len(expr.args) == 2:
                new_ivar = next(self.symbols)
                self.subexprs_dict[expr] = new_ivar
                self.adds_2a[expr] = new_ivar
                return new_ivar
              else:
                return self._collect_op(expr)
              
          for exprB in self.adds_ma:
            intersect = args_set.intersection(set(exprB.args))
            intersect_len = len(intersect)
            if intersect_len >= 2:
              intersect_expr = sympy.Add(*intersect)
              if intersect_expr == exprB:
                intersect_ivar = self.adds_ma[exprB]
              else:
                intersect_ivar = next(self.symbols)
                self.subexprs_dict[intersect_expr] = intersect_ivar
                if intersect_len > 2:
                  self.adds_ma[intersect_expr] = intersect_ivar
                else:
                  self.adds_2a[intersect_expr] = intersect_ivar
                # new exprB:
                exprB_ivar = self.subexprs_dict.pop(exprB)
                self.adds_ma.pop(exprB)
                new_exprB = exprB.subs(intersect_expr,intersect_ivar)
                self.subexprs_dict[new_exprB] = exprB_ivar
                if len(new_exprB.args) > 2:
                  self.adds_ma[new_exprB] = exprB_ivar
                else:
                  self.adds_2a[new_exprB] = exprB_ivar
              # new expr
              if intersect_expr == expr:
                return intersect_ivar
              else:
                new_expr = expr.subs(intersect_expr,intersect_ivar)
                if len(new_expr.args) == 2:
                  new_ivar = next(self.symbols)
                  self.subexprs_dict[new_expr] = new_ivar
                  self.adds_ma[new_expr] = new_ivar
                  return new_ivar
                else:
                  return self._collect_op(new_expr)
        
          new_ivar = next(self.symbols)
          self.subexprs_dict[expr] = new_ivar
          self.adds_ma[expr] = new_ivar
          return new_ivar
            
          
      else:
        new_ivar = next(self.symbols)
        self.subexprs_dict[expr] = new_ivar
        return new_ivar
      

    
  def _collect_expr(self, expr):
    if expr.is_Atom:
      return expr
    else:
      new_ivar = next(self.symbols)
      self.subexprs_dict[expr] = new_ivar
      return new_ivar
    


    
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
