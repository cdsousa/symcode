SymCode
=======

Library to collect sub-expressions from SymPy expressions and generate C or Python code


Example
-------

```Python
>>> import sympy
>>> import symcode
>>> 
>>> import sympy.physics.hydrogen
>>> from sympy.abc import x
>>> n, l, Z = 6, 2, 6
>>> expr = sympy.physics.hydrogen.R_nl(n, l, x, Z)
>>> print expr
sqrt(70)*x**2*(-4*x**3/3 + 16*x**2 - 56*x + 56)*exp(-x)/210
```

```Python
>>> se = symcode.subexprs.Subexprs(mode='unique_ops')
>>> 
>>> expr_diffs = []
>>> 
>>> for order in range(11): # compute derivatives of 0 to 10 order
>>>     diff = expr
>>>     for _ in range(order):
>>>         diff = diff.diff(x)
>>>     collecteddiff = se.collect(diff) # collect sub-expressions
>>>     expr_diffs.append(collecteddiff)
>>> 
>>> sym_code = (se.subexprs, expr_diffs)
>>> sym_code_opt = symcode.optimization.fully_optimize_code( sym_code )
 dead code elimination and single use propagation
 common sub-expression elimination
 copy propagation
 dead code elimination and single use propagation
 done
```


```Python
>>> c_code_opt = symcode.generation.gen_c_func( sym_code_opt, ['x'], [], 'diffs' )
>>> print c_code_opt
```
```C
void diffs( double* out, const double* x )
{
  double cse0 = -((x)*(x));
  double cse11 = -x;
  double tmp6 = -16*cse0 + 4*pow(cse11, 3)/3 + 56*cse11 + 56;
  double cse6 = tmp6/210;
  double cse17 = -sqrt(70)*exp(cse11);
  double tmp9 = cse0*cse17*cse6;
  double tmp12 = 4*cse0 - 32*cse11 - 56;
  double tmp14 = -cse0*cse17*cse6;
  double tmp18 = 8*cse11 + 32;
  double cse1 = 2*tmp12/105;
  double cse2 = tmp12/35;
  double cse3 = 4*cse2;
  double cse4 = 2*tmp12/7;
  double cse5 = 2*tmp18/7;
  double cse7 = tmp6/105;
  double cse8 = tmp6/35;
  double cse9 = 2*cse8;
  double cse10 = 2*tmp6/21;
  double cse12 = -cse0*tmp12;
  double cse13 = -cse0*tmp18;
  double cse14 = -cse11*tmp12;
  double cse15 = -cse11*tmp18;
  double cse16 = -cse11*tmp6;

  out[0] = tmp9;
  out[1] = cse0*cse17*cse2/6 + cse11*cse17*cse7 + tmp14;
  out[2] = -cse0*cse17*cse2/3 + cse1*cse11*cse17 - 2*cse11*cse17*cse7 - cse13*cse17/210 - cse17*cse7 + tmp9;
  out[3] = cse0*cse17*cse2/2 - 4*cse0*cse17/105 - 2*cse11*cse17*cse2 + cse11*cse17*cse8 + cse13*cse17/70 - cse15*cse17/35 - cse17*cse2 + cse17*cse8 + tmp14;
  out[4] = -cse0*cse1*cse17 + 16*cse0*cse17/105 + cse11*cse17*cse3 - 2*cse11*cse17*cse5/5 - 4*cse11*cse17*cse7 - 32*cse11*cse17/105 - cse13*cse17/35 + cse17*cse3 - cse17*cse5/5 - cse17*cse9 + tmp9;
  out[5] = -8*cse0*cse17/21 + cse10*cse17 - 2*cse11*cse17*cse4/3 + cse11*cse17*cse5 + 32*cse11*cse17/21 - cse12*cse17/42 + cse13*cse17/21 - cse16*cse17/21 - cse17*cse4 + cse17*cse5 + 16*cse17/21 + tmp14;
  out[6] = -cse0*cse17*cse2 + 16*cse0*cse17/21 + cse11*cse17*cse4 - 2*cse11*cse17*cse5 - cse11*cse17*cse9 - 32*cse11*cse17/7 - cse13*cse17/14 + 2*cse17*cse4 - 3*cse17*cse5 - cse17*tmp6/7 - 32*cse17/7 + tmp9;
  out[7] = -4*cse0*cse17/3 + 32*cse11*cse17/3 - cse12*cse17/30 + cse13*cse17/10 + 2*cse14*cse17/5 - cse15*cse17 - cse16*cse17/15 - cse17*tmp12 + 2*cse17*tmp18 + cse17*tmp6/5 + 16*cse17 + tmp14;
  out[8] = -2*cse0*cse1*cse17 + 32*cse0*cse17/15 - 8*cse11*cse17*cse7 - 64*cse11*cse17/3 - 2*cse13*cse17/15 - 8*cse14*cse17/15 + 8*cse15*cse17/5 + 8*cse17*tmp12/5 - 4*cse17*tmp18 - 4*cse17*tmp6/15 - 128*cse17/3 + tmp9;
  out[9] = 3*cse0*cse17*cse2/2 - 3*cse0*cse17*cse5/5 - 16*cse0*cse17/5 - 6*cse11*cse17*cse3 + 3*cse11*cse17*cse8 + 192*cse11*cse17/5 - 12*cse15*cse17/5 + 6*cse17*cse9 - 12*cse17*tmp12/5 + 36*cse17*tmp18/5 + 96*cse17 + tmp14;
  out[10] = 32*cse0*cse17/7 - cse10*cse11*cse17 + 3*cse11*cse17*cse4 - 12*cse11*cse17*cse5 - 64*cse11*cse17 + cse12*cse17/21 - 3*cse13*cse17/14 + 12*cse17*cse4 - 12*cse17*tmp18 - 3*cse17*tmp6/7 - 192*cse17 + tmp9;

  return;
}
```
