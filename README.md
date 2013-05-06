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
>>> se = symcode.subexprs.Subexprs()
>>>
>>>expr_diffs = []
>>>
>>>for order in range(11): # compute derivatives of 0 to 10 order
>>>    diff = expr
>>>    for _ in range(order):
>>>        diff = diff.diff(x)
>>>    collecteddiff = se.collect(diff) # collect sub-expressions
>>>    expr_diffs.append(collecteddiff)
>>>
>>>sym_code = se.get(expr_diffs)
```

```Python
>>>c_code = symcode.generation.gen_c_func( sym_code, ['x'], [], 'diffs' )
>>>print(c_code)
```
```C
void diffs( double* out, const double* x )
{
  double x0 = -x;
  double x1 = sqrt(70)*exp(x0);
  double x2 = ((x)*(x));
  double x3 = pow(x, 3);
  double x4 = -12*x2;
  double x5 = 42*x + x3 + x4 - 42;
  double x6 = x2*x5;
  double x7 = -8*x;
  double x8 = x2 + x7 + 14;
  double x9 = x*x8;
  double x10 = -24*x2;
  double x11 = 84*x + x10 + 2*x3 - 84;
  double x12 = (2.0L/315.0L)*x1;
  double x13 = x2*x8;
  double x14 = x*x5;
  double x15 = x - 4;
  double x16 = x15*x2;
  double x17 = x*x15;

  out[0] = -2.0L/315.0L*x1*x6;
  out[1] = -x*x12*(x0*x5 + x11 + 3*x9);
  out[2] = -x12*(x11 - 6*x13 - 4*x14 + 6*x16 + x6 + 12*x9);
  out[3] = -x12*(-396*x + 9*x13 + 6*x14 - 18*x16 + 36*x17 + 96*x2 - 6*x3 - x6 - 36*x9 + 504);
  out[4] = -x12*(1200*x + 36*x16 - 144*x17 - 240*x2 + 12*x3 + x4*x8 + x5*x7 + x6 + 72*x9 - 1800);
  out[5] = x12*(2880*x - 15*x13 - 10*x14 + 60*x16 - 360*x17 - 480*x2 + 20*x3 + x6 + 120*x9 - 4920);
  out[6] = -x12*(5940*x - 18*x13 - 12*x14 + 90*x16 - 720*x17 - 840*x2 + 30*x3 + x6 + 180*x9 - 11340);
  out[7] = x12*(11004*x - 21*x13 - 14*x14 + 126*x16 - 1260*x17 - 1344*x2 + 42*x3 + x6 + 252*x9 - 23184);
  out[8] = -x12*(18816*x + x10*x8 - 16*x14 + 168*x16 - 2016*x17 - 2016*x2 + 56*x3 + x6 + 336*x9 - 43344);
  out[9] = x12*(30240*x - 27*x13 - 18*x14 + 216*x16 - 3024*x17 - 2880*x2 + 72*x3 + x6 + 432*x9 - 75600);
  out[10] = -x12*(46260*x - 30*x13 - 20*x14 + 270*x16 - 4320*x17 - 3960*x2 + 90*x3 + x6 + 540*x9 - 124740);

  return;
}
```

```Python
>>>py_code = symcode.generation.gen_py_func( sym_code, ['x'], [], 'diffs' )
>>>print(py_code)
```
```Python
def diffs( x ) :

    out = [0]*11

    x0 = -x
    x1 = sqrt(70)*exp(x0)
    x2 = ((x)*(x))
    x3 = pow(x, 3)
    x4 = -12*x2
    x5 = 42*x + x3 + x4 - 42
    x6 = x2*x5
    x7 = -8*x
    x8 = x2 + x7 + 14
    x9 = x*x8
    x10 = -24*x2
    x11 = 84*x + x10 + 2*x3 - 84
    x12 = (2.0L/315.0L)*x1
    x13 = x2*x8
    x14 = x*x5
    x15 = x - 4
    x16 = x15*x2
    x17 = x*x15

    out[0] = -2.0L/315.0L*x1*x6
    out[1] = -x*x12*(x0*x5 + x11 + 3*x9)
    out[2] = -x12*(x11 - 6*x13 - 4*x14 + 6*x16 + x6 + 12*x9)
    out[3] = -x12*(-396*x + 9*x13 + 6*x14 - 18*x16 + 36*x17 + 96*x2 - 6*x3 - x6 - 36*x9 + 504)
    out[4] = -x12*(1200*x + 36*x16 - 144*x17 - 240*x2 + 12*x3 + x4*x8 + x5*x7 + x6 + 72*x9 - 1800)
    out[5] = x12*(2880*x - 15*x13 - 10*x14 + 60*x16 - 360*x17 - 480*x2 + 20*x3 + x6 + 120*x9 - 4920)
    out[6] = -x12*(5940*x - 18*x13 - 12*x14 + 90*x16 - 720*x17 - 840*x2 + 30*x3 + x6 + 180*x9 - 11340)
    out[7] = x12*(11004*x - 21*x13 - 14*x14 + 126*x16 - 1260*x17 - 1344*x2 + 42*x3 + x6 + 252*x9 - 23184)
    out[8] = -x12*(18816*x + x10*x8 - 16*x14 + 168*x16 - 2016*x17 - 2016*x2 + 56*x3 + x6 + 336*x9 - 43344)
    out[9] = x12*(30240*x - 27*x13 - 18*x14 + 216*x16 - 3024*x17 - 2880*x2 + 72*x3 + x6 + 432*x9 - 75600)
    out[10] = -x12*(46260*x - 30*x13 - 20*x14 + 270*x16 - 4320*x17 - 3960*x2 + 90*x3 + x6 + 540*x9 - 124740)

    return out
```