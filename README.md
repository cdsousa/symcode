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
>>> expr_diffs = []
>>>
>>> for order in range(11): # compute derivatives of 0 to 10 order
...     diff = expr
...     for _ in range(order):
...         diff = diff.diff(x)
...     collecteddiff = se.collect(diff) # collect sub-expressions
...     expr_diffs.append(collecteddiff)
>>>
>>> sym_code = se.get(expr_diffs)

```

```Python
>>> c_code = symcode.generation.gen_c_func( sym_code, ['x'], 'diffs' )
>>> print(c_code)
void diffs( double* out, const double* x )
{
  double x0 = sqrt(70)*exp(-x);
  double x1 = ((x)*(x));
  double x2 = pow(x, 3);
  double x3 = 42*x - 12*x1 + x2 - 42;
  double x4 = x1*x3;
  double x5 = -8*x + x1 + 14;
  double x6 = x*x5;
  double x7 = x*x3;
  double x8 = 24*x1;
  double x9 = -84*x - 2*x2 + x8 + 84;
  double x10 = (2.0L/315.0L)*x0;
  double x11 = x - 4;
  double x12 = x1*x11;
  double x13 = -x4;
  double x14 = x1*x5;
  double x15 = x*x11;
//
  out[0] = -2.0L/315.0L*x0*x4;
  out[1] = x*x10*(-3*x6 + x7 + x9);
  out[2] = x10*(-6*x12 + x13 + 6*x14 - 12*x6 + 4*x7 + x9);
  out[3] = x10*(396*x - 96*x1 + 18*x12 - 9*x14 - 36*x15 + 6*x2 + x4 + 36*x6 - 6*x7 - 504);
  out[4] = x10*(-1200*x + 240*x1 - 36*x12 + x13 + 12*x14 + 144*x15 - 12*x2 - 72*x6 + 8*x7 + 1800);
  out[5] = x10*(2880*x - 480*x1 + 60*x12 - 15*x14 - 360*x15 + 20*x2 + x4 + 120*x6 - 10*x7 - 4920);
  out[6] = x10*(-5940*x + 840*x1 - 90*x12 + x13 + 18*x14 + 720*x15 - 30*x2 - 180*x6 + 12*x7 + 11340);
  out[7] = x10*(11004*x - 1344*x1 + 126*x12 - 21*x14 - 1260*x15 + 42*x2 + x4 + 252*x6 - 14*x7 - 23184);
  out[8] = x10*(-18816*x + 2016*x1 - 168*x12 + x13 + 2016*x15 - 56*x2 + x5*x8 - 336*x6 + 16*x7 + 43344);
  out[9] = x10*(30240*x - 2880*x1 + 216*x12 - 27*x14 - 3024*x15 + 72*x2 + x4 + 432*x6 - 18*x7 - 75600);
  out[10] = x10*(-46260*x + 3960*x1 - 270*x12 + x13 + 30*x14 + 4320*x15 - 90*x2 - 540*x6 + 20*x7 + 124740);
//
  return;
}

```

```Python
>>> py_code = symcode.generation.gen_py_func( sym_code, ['x'], 'diffs' )
>>> print(py_code)
def diffs( x ) :
#
    out = [0]*11
#
    x0 = sqrt(70)*exp(-x)
    x1 = ((x)*(x))
    x2 = pow(x, 3)
    x3 = 42*x - 12*x1 + x2 - 42
    x4 = x1*x3
    x5 = -8*x + x1 + 14
    x6 = x*x5
    x7 = x*x3
    x8 = 24*x1
    x9 = -84*x - 2*x2 + x8 + 84
    x10 = (2.0L/315.0L)*x0
    x11 = x - 4
    x12 = x1*x11
    x13 = -x4
    x14 = x1*x5
    x15 = x*x11
#
    out[0] = -2.0L/315.0L*x0*x4
    out[1] = x*x10*(-3*x6 + x7 + x9)
    out[2] = x10*(-6*x12 + x13 + 6*x14 - 12*x6 + 4*x7 + x9)
    out[3] = x10*(396*x - 96*x1 + 18*x12 - 9*x14 - 36*x15 + 6*x2 + x4 + 36*x6 - 6*x7 - 504)
    out[4] = x10*(-1200*x + 240*x1 - 36*x12 + x13 + 12*x14 + 144*x15 - 12*x2 - 72*x6 + 8*x7 + 1800)
    out[5] = x10*(2880*x - 480*x1 + 60*x12 - 15*x14 - 360*x15 + 20*x2 + x4 + 120*x6 - 10*x7 - 4920)
    out[6] = x10*(-5940*x + 840*x1 - 90*x12 + x13 + 18*x14 + 720*x15 - 30*x2 - 180*x6 + 12*x7 + 11340)
    out[7] = x10*(11004*x - 1344*x1 + 126*x12 - 21*x14 - 1260*x15 + 42*x2 + x4 + 252*x6 - 14*x7 - 23184)
    out[8] = x10*(-18816*x + 2016*x1 - 168*x12 + x13 + 2016*x15 - 56*x2 + x5*x8 - 336*x6 + 16*x7 + 43344)
    out[9] = x10*(30240*x - 2880*x1 + 216*x12 - 27*x14 - 3024*x15 + 72*x2 + x4 + 432*x6 - 18*x7 - 75600)
    out[10] = x10*(-46260*x + 3960*x1 - 270*x12 + x13 + 30*x14 + 4320*x15 - 90*x2 - 540*x6 + 20*x7 + 124740)
#
    return out

```