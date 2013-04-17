
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



def cse(exprs, ivars_name='cse', opt_muladd=True):
  cse_obj = Cse(ivars_name, opt_muladd)
  exprs = cse_obj.collect(exprs)
  return cse_obj.get(exprs)


