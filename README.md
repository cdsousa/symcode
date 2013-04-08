SymCode
=======

Library to collect sub-expressions from SymPy expressions and generate C and Python code


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
  double tmp6 = -16.0*cse0 + 1.33333333333333*pow(cse11, 3) + 56.0*cse11 + 56.0;
  double cse6 = 0.00476190476190476*tmp6;
  double cse17 = -8.36660026534076*exp(cse11);
  double tmp9 = cse0*cse17*cse6;
  double tmp12 = 4.0*cse0 - 32.0*cse11 - 56.0;
  double tmp14 = -cse0*cse17*cse6;
  double tmp18 = 8.0*cse11 + 32.0;
  double cse1 = 0.019047619047619*tmp12;
  double cse2 = 0.0285714285714286*tmp12;
  double cse3 = 4.0*cse2;
  double cse4 = 0.285714285714286*tmp12;
  double cse5 = 0.285714285714286*tmp18;
  double cse7 = 0.00952380952380952*tmp6;
  double cse8 = 0.0285714285714286*tmp6;
  double cse9 = 2.0*cse8;
  double cse10 = 0.0952380952380952*tmp6;
  double cse12 = -cse0*tmp12;
  double cse13 = -cse0*tmp18;
  double cse14 = -cse11*tmp12;
  double cse15 = -cse11*tmp18;
  double cse16 = -cse11*tmp6;

  out[0] = tmp9;
  out[1] = 0.166666666666667*cse0*cse17*cse2 + cse11*cse17*cse7 + tmp14;
  out[2] = -0.333333333333333*cse0*cse17*cse2 + cse1*cse11*cse17 - 2.0*cse11*cse17*cse7 - 0.00476190476190476*cse13*cse17 - cse17*cse7 + tmp9;
  out[3] = 0.5*cse0*cse17*cse2 - 0.0380952380952381*cse0*cse17 - 2.0*cse11*cse17*cse2 + cse11*cse17*cse8 + 0.0142857142857143*cse13*cse17 - 0.0285714285714286*cse15*cse17 - cse17*cse2 + cse17*cse8 + tmp14;
  out[4] = -cse0*cse1*cse17 + 0.152380952380952*cse0*cse17 + cse11*cse17*cse3 - 0.4*cse11*cse17*cse5 - 4.0*cse11*cse17*cse7 - 0.304761904761905*cse11*cse17 - 0.0285714285714286*cse13*cse17 + cse17*cse3 - 0.2*cse17*cse5 - cse17*cse9 + tmp9;
  out[5] = -0.380952380952381*cse0*cse17 + cse10*cse17 - 0.666666666666667*cse11*cse17*cse4 + cse11*cse17*cse5 + 1.52380952380952*cse11*cse17 - 0.0238095238095238*cse12*cse17 + 0.0476190476190476*cse13*cse17 - 0.0476190476190476*cse16*cse17 - cse17*cse4 + cse17*cse5 + 0.761904761904762*cse17 + tmp14;
  out[6] = -cse0*cse17*cse2 + 0.761904761904762*cse0*cse17 + cse11*cse17*cse4 - 2.0*cse11*cse17*cse5 - cse11*cse17*cse9 - 4.57142857142857*cse11*cse17 - 0.0714285714285714*cse13*cse17 + 2.0*cse17*cse4 - 3.0*cse17*cse5 - 0.142857142857143*cse17*tmp6 - 4.57142857142857*cse17 + tmp9;
  out[7] = -1.33333333333333*cse0*cse17 + 10.6666666666667*cse11*cse17 - 0.0333333333333333*cse12*cse17 + 0.1*cse13*cse17 + 0.4*cse14*cse17 - cse15*cse17 - 0.0666666666666667*cse16*cse17 - cse17*tmp12 + 2.0*cse17*tmp18 + 0.2*cse17*tmp6 + 16.0*cse17 + tmp14;
  out[8] = -2.0*cse0*cse1*cse17 + 2.13333333333333*cse0*cse17 - 8.0*cse11*cse17*cse7 - 21.3333333333333*cse11*cse17 - 0.133333333333333*cse13*cse17 - 0.533333333333333*cse14*cse17 + 1.6*cse15*cse17 + 1.6*cse17*tmp12 - 4.0*cse17*tmp18 - 0.266666666666667*cse17*tmp6 - 42.6666666666667*cse17 + tmp9;
  out[9] = 1.5*cse0*cse17*cse2 - 0.6*cse0*cse17*cse5 - 3.2*cse0*cse17 - 6.0*cse11*cse17*cse3 + 3.0*cse11*cse17*cse8 + 38.4*cse11*cse17 - 2.4*cse15*cse17 + 6.0*cse17*cse9 - 2.4*cse17*tmp12 + 7.2*cse17*tmp18 + 96.0*cse17 + tmp14;
  out[10] = 4.57142857142857*cse0*cse17 - cse10*cse11*cse17 + 3.0*cse11*cse17*cse4 - 12.0*cse11*cse17*cse5 - 64.0*cse11*cse17 + 0.0476190476190476*cse12*cse17 - 0.214285714285714*cse13*cse17 + 12.0*cse17*cse4 - 12.0*cse17*tmp18 - 0.428571428571429*cse17*tmp6 - 192.0*cse17 + tmp9;

  return;
}
```
Author
------

[Cristóvão Duarte Sousa](https://github.com/cdsousa)

Install
-------

From git source:

    git clone git@github.com:cdsousa/symcode.git
    cd symcode
    python setup.py install

License
-------

New BSD license. See LICENSE.txt