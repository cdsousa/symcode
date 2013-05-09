
import collections
import copy
import sympy
import sys

from . import subexprs


def dead_code_elim( code ):
    """Performe 'dead code elimination' optimization on code."""
    
    se = subexprs.Subexprs()
    se._subexp_iv = {v:k for k, v in code[0]}
    return (se.get_subexprs(code[1]), copy.deepcopy(code[1]))


def inlining_singleops( code ):
    """Performe inlining of once used variables (and elimination of not used variables).

    Expects code with only one operation per subexpression

    """
    
    subexprs_invdict = dict(code[0])
    
    ivs_set = set(subexprs_invdict.keys())
    
    used_ivs = set()
    used_morethanonce_ivs = set()
    
    for expr in subexprs_invdict.values():
        ivs = expr.free_symbols & ivs_set
        used_morethanonce_ivs |= ivs & used_ivs
        used_ivs |= ivs
    
    for expr in code[1]:
        ivs = expr.free_symbols & ivs_set
        used_morethanonce_ivs |= ivs & used_ivs
        used_ivs |= ivs
    
    used_onlyonce_ivs = used_ivs - used_morethanonce_ivs
      
    subexprs_ordereddict = collections.OrderedDict()
        
    def _subexprs(expr):
        subs = {}
        for symb in expr.free_symbols:
          if symb in subexprs_invdict and symb not in subexprs_ordereddict:
              if symb in used_onlyonce_ivs:
                  subexpr = subexprs_invdict[symb]
                  new_expr = _subexprs(subexpr)
                  subs[symb] = new_expr
              else:
                  subexpr = subexprs_invdict[symb]
                  new_expr = _subexprs(subexpr)
                  subexprs_ordereddict[symb] = new_expr

        return expr.subs(subs)
                  

    out_exps = copy.deepcopy(code[1])
    for i,expr in enumerate(out_exps):
      out_exps[i] = _subexprs(expr)
      
    return (subexprs_ordereddict.items(), out_exps)


def copy_propag( code ):
    """Performe 'copy propagation' optimization on code."""
    
    debug = False
    removed=0
    
    retcode = copy.deepcopy(code)
    toremove = []
    
    for i in range(len(retcode[0])):
      
       # constant folding
        v = retcode[0][i][0]
        e = retcode[0][i][1]
        retcode[0][i] = (v,e)
        
        # copy propagation
        if e.is_Atom:
            if debug: print(i,v,e,'is atom')
            retcode = xreplace( retcode, {v:e} )
            toremove.append(i)
            removed += 1
            if debug: print('  poped')

    for r in reversed(toremove):
        retcode[0].pop(r)
        
    # output expression constant folding
    for i,e in enumerate(retcode[1]):
      retcode[1][i] = e
    
    if debug: print('removed',removed)
    return retcode


def constant_fold( code ):
    """Performe 'constant folding' optimization on code."""
    
    retcode = ([], copy.deepcopy(code[1]))
    
    for v,e in code[0]:
        retcode[0].append((v, e.n()))
        
    for i,e in enumerate(code[1]):
        retcode[1][i] = e.n()
    
    return retcode
  
  

def apply_func( code, func, apply_to_ivs=True ):
    if apply_to_ivs:
        code_ivs = [(func(iv), func(se)) for iv, se in code[0]]
    else:
        code_ivs = [(iv, func(se)) for iv, se in code[0]]
    code_exprs = [func(expr) for expr in code[1]]
    return code_ivs, code_exprs


def xreplace( code, xreplace_dict ):
  return apply_func( code, lambda x: x.xreplace( xreplace_dict ) )


def common_subexpr_elim( code, auxvarname = 'cse' ):
    """Performe 'common sub-expression elimination' optimization on code."""
    
    cse = sympy.cse([sympy.Eq(v,e) for v,e in code[0]] + list(code[1]), symbols=sympy.cse_main.numbered_symbols(auxvarname), postprocess=sympy.cse_main.cse_separate )
        
    new_code_out = copy.deepcopy(code[1])
    for i,e in enumerate(cse[1]):
      new_code_out[i] = e
    
    return (cse[0], new_code_out)
    
 

def common_subexpr_elim_OLD( code, auxvarname = 'cse' ):
    """Performe 'common sub-expression elimination' optimization on code."""
    
    se = subexprs.Subexprs()
    se.subexprs_dict = {expr:ivar for ivar,expr in code[0]}
    
    if isinstance(code[1],sympy.Matrix):
      code_out = sympy.flatten(code[1])
    else:
      code_out = code[1]
    
    cse = sympy.cse(se.subexprs_dict.keys() + code_out,  sympy.cse_main.numbered_symbols(auxvarname) )
    
    cse_new_subexprs = cse[0]
    cse_subexprs = cse[1][:len(code[0])]
    cse_outexprs = cse[1][len(code[0]):]
    
    se.subexprs_dict = dict(zip(cse_subexprs, se.subexprs_dict.values()))
    se.subexprs_dict.update({expr:ivar for ivar,expr in cse_new_subexprs})
    
    new_code_out = copy.deepcopy(code[1])
    for i,e in enumerate(cse_outexprs):
      new_code_out[i] = e
    
    return (se.get_subexprs(new_code_out), new_code_out)
    
    
def inlining( code ):
    """Performe inlining of once used variables (and elimination of not used variables)."""
    
    debug = False
    removed=0
    
    retcode = copy.deepcopy(code)
    
    for i in range(len(retcode[0])-1,-1,-1):
        v = retcode[0][i][0]
        e = retcode[0][i][1]
        uses = 0
        usedin_ai = None
        usedin_oi = None
        if debug: print(i,v)
        for ai in range(i+1,len(retcode[0])):
            count = retcode[0][ai][1].count(v)
            if count:
                uses += count
                usedin_ai = ai
                # if debug: print('  used in',ai)
        for oi in range(len(retcode[1])):
            count = sympy.sympify(retcode[1][oi]).count(v)
            if count:
                uses += count
                usedin_oi = oi
                # if debug: print('  used in out',oi)
        
        if uses == 0:
            retcode[0].pop(i)
            removed += 1
            if debug: print('  not used: removed')
        elif uses == 1:
            if usedin_ai != None:
                retcode[0][usedin_ai] = ( retcode[0][usedin_ai][0] , retcode[0][usedin_ai][1].xreplace({v:e}) )
                if debug: print('  used once: removed and substituted in',retcode[0][usedin_ai][0])
            elif usedin_oi != None:
                retcode[1][usedin_oi] = retcode[1][usedin_oi].xreplace({v:e})
                if debug: print('  used once: removed and substituted in out',usedin_oi)
            retcode[0].pop(i)
            removed += 1
    
    if debug: print('removed',removed)
    return retcode


def rename_ivars_unsafe(code, ivarnames ):
    
  retcode = copy.deepcopy(code)
   
  for i in range(len(retcode[0])):

    new_symbol = sympy.Symbol(ivarnames+str(i),real=True)
    Dxreplace = { retcode[0][i][0] : new_symbol }
  
    retcode[0][i] = ( new_symbol , retcode[0][i][1] )
        
    for j in range(i+1,len(retcode[0])):
      retcode[0][j] = ( retcode[0][j][0], retcode[0][j][1].xreplace( Dxreplace ) )
  
    for j in range(len(retcode[1])):
      retcode[1][j] = sympy.sympify(retcode[1][j]).xreplace( Dxreplace )
  
  return retcode


def make_output_single_vars(code, ivarnames=None ):

    retcode = copy.deepcopy(code)

    if ivarnames:
        cnt = 0

    else:
        if retcode[0]:
            lastivar = str(retcode[0][-1][0])
            for i in range(len(lastivar)):
                if not lastivar[-i-1].isdigit(): break
            if i > 0:
                cnt = int(lastivar[-i:]) + 1
                ivarnames = lastivar[:-i]
            else:
                cnt = 1
                ivarnames = lastivar + '_'
        else:
            cnt = 0
            ivarnames = 'outputiv_'

    for i in range(len(retcode[1])):
        if not sympy.sympify(retcode[1][i]).is_Atom:
            new_symbol = sympy.Symbol(ivarnames+str(cnt),real=True)
            retcode[0].append( (new_symbol, retcode[1][i]) )
            retcode[1][i] = new_symbol
            cnt += 1

    return retcode
  

def _fprint(x):
  print(x)
  sys.stdout.flush()


def fully_optimize_code( code, ivarnames=None, singlevarout=False, clearcache=0, debug = True ) :
  
  if debug: _fprint(' dead code elimination and inlining of once used variables')
  code = inlining(code)
  if clearcache > 1: sympy.cache.clear_cache()
  
  if debug: _fprint(' copy propagation')
  code = copy_propag(code,'cse')
  if clearcache > 1: sympy.cache.clear_cache()
  
  if debug: _fprint(' common subexpression elimination')
  code = common_subexpr_elim(code,'cse')
  if clearcache > 1: sympy.cache.clear_cache()
  
  if debug: _fprint(' dead code elimination and inlining of once used variables')
  code = inlining(code)
  if clearcache > 1: sympy.cache.clear_cache()
  
  if debug: _fprint(' copy propagation')
  code = copy_propag(code,'cse')
  if clearcache > 1: sympy.cache.clear_cache()
  
  if debug: _fprint(' constant folding')
  code = constant_fold()(code)
  if clearcache > 1: sympy.cache.clear_cache()
  
  if ivarnames:
    if debug: _fprint(' code_rename_ivars (unsafe)')
    code = rename_ivars_unsafe(code, ivarnames=ivarnames)
    if clearcache > 1: sympy.cache.clear_cache()
  
  if singlevarout:
    if debug: _fprint(' code_make_output_single_vars')
    code = make_output_single_vars(code)
    
  if clearcache: sympy.cache.clear_cache()
  
  if debug: print(' done')
  
  return code


