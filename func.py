# Based on https://www.youtube.com/watch?v=5C6sv7-eTKg

# And also https://www.youtube.com/watch?v=pkCLMl0e_0k as a matter of fact.

# Rules:
#
#  * Everything is a function, nothing else.
#  * All functions have a single argument (only function, remember?).
#  * Their return values are function, obviously.
#
# When lost (like I have been), remember. Think of the various concepts as
# "behaviours".


# Booleans and operators.


def TRUE(x):
    def f(y):
        return x

    return f


TRUE = lambda x: lambda y: x


def FALSE(x):
    def f(y):
        return y

    return f


FALSE = lambda x: lambda y: y

# Hint: True is left, False is right.

assert TRUE("5V")("GND") == "5V"
assert FALSE("5V")("GND") == "GND"


def NOT(f):
    return f(FALSE)(TRUE)


NOT = lambda f: f(FALSE)(TRUE)

# Hint: f being TRUE will chose left function, that is FALSE. And conversely.

assert NOT(TRUE) is FALSE
assert NOT(FALSE) is TRUE

assert NOT(TRUE)("5V")("GND") == "GND"
assert NOT(FALSE)("5V")("GND") == "5V"


def AND(x):
    def f(y):
        return x(y)(x)

    return f


AND = lambda x: lambda y: x(y)(x)

# Hint: if x is FALSE, right function (x, as FALSE) is returned.
#       If x is TRUE, let y (that can be either TRUE or FALSE) decide.

assert AND(TRUE)(TRUE) is TRUE
assert AND(TRUE)(FALSE) is FALSE
assert AND(FALSE)(TRUE) is FALSE
assert AND(FALSE)(FALSE) is FALSE


def OR(x):
    def f(y):
        return x(x)(y)

    return f


OR = lambda x: lambda y: x(x)(y)

# Hint: if x is TRUE, left function (x, as TRUE) is returned.
#       If x is FALSE, let y (that can be either TRUE or FALSE) decide.

assert OR(TRUE)(TRUE) is TRUE
assert OR(TRUE)(FALSE) is TRUE
assert OR(FALSE)(TRUE) is TRUE
assert OR(FALSE)(FALSE) is FALSE


# Numbers.

ONE = lambda f: lambda x: f(x)
TWO = lambda f: lambda x: f(f(x))
THREE = lambda f: lambda x: f(f(f(x)))


# Illustrations.

incr = lambda x: x + 1

assert ONE(incr)(0) == 1
assert TWO(incr)(0) == 2
assert THREE(incr)(0) == 3

concat = lambda x: "*" + x

assert ONE(concat)("") == "*"
assert TWO(concat)("") == "**"
assert THREE(concat)("") == "***"


# Exploration.

FOUR = lambda f: lambda x: f(f(f(f(x))))

m = FOUR(THREE)
assert m(incr)(0) == 3**4  # Exponentiation.


ZERO = lambda f: lambda x: x

assert ZERO(incr)(0) == 0


# Successor.


def SUCC(n):
    def ret(f):
        return lambda x: f(n(f)(x))

    return ret


SUCC = lambda n: lambda f: lambda x: f(n(f)(x))

# Hint: "our" numbers want 2 "args" so SUCC must too (think of "signature"/API).
#       May be seen as SUCC = lambda n: (lambda f: lambda x: f( n(f)(x) ) )
#                           Number "API" ^^^^^^^^^^^^^^^^^^^ ^  ^^^^^^^ "old" number
#                                                            |
#                                                     f applied once more

assert SUCC(TWO)(incr)(0) == THREE(incr)(0)
assert SUCC(SUCC(TWO))(incr)(0) == FOUR(incr)(0)


# Addition.

ADD = lambda x: lambda y: x(SUCC)(y)

# Hint: Apply 'x' time SUCC on top of 'y'.

assert ADD(TWO)(THREE)(incr)(0) == ADD(FOUR)(ONE)(incr)(0)


# Multiplication.

MUL = lambda x: lambda y: lambda f: y(x(f))

# Hint: You want to do f 'x' times, and you want to do this 'y' times.

assert MUL(FOUR)(THREE)(incr)(0) == 12


# Data structure.

# Well, aggregation as a couple, using Lispy operators.

CONS = lambda a: lambda b: lambda s: s(a)(b)

# Hint: `lamdba: 3` is a function, store 2 functions and use the initial switch.

p = CONS(2)(3)

assert p(TRUE) == 2
assert p(FALSE) == 3

CAR = lambda p: p(TRUE)
CDR = lambda p: p(FALSE)

assert CAR(CONS(2)(3)) == 2
assert CDR(CONS(2)(3)) == 3

# Composable (linked list).

assert CAR(CDR(CONS(2)(CONS(3)(4)))) == 3


# Predecessor.

COUPLE = lambda p: CONS(SUCC(CAR(p)))(CAR(p))

FOUR_ = FOUR(COUPLE)(CONS(ZERO)(ZERO))

# Hint: (New) numbers are not just f(f(f(...))), but a couple of this and its
#       predecessor.

assert CAR(FOUR_)(incr)(0) == 4
assert CDR(FOUR_)(incr)(0) == 3

PRED = lambda n: CDR(n(COUPLE)(CONS(ZERO)(ZERO)))

EXP = FOUR(THREE)
assert EXP(incr)(0) == 81
assert PRED(EXP)(incr)(0) == 80


# Substraction.

SUB = lambda x: lambda y: y(PRED)(x)

assert SUB(FOUR)(TWO)(incr)(0) == 2


# Test.

IS_ZERO = lambda n: n(lambda _: FALSE)(TRUE)

# Hint: ZERO(f)(x) never applies the f to x. Any other does.

assert IS_ZERO(ZERO) == TRUE
assert IS_ZERO(ONE) == FALSE
assert IS_ZERO(THREE) == FALSE


# Factorial!


def fact(n):
    if n == 0:
        return 1
    else:
        return n * fact(n - 1)


assert fact(3) == 6

# Hint: Raw translation.

FACT = lambda n: IS_ZERO(n)(ONE)(MUL(n)(FACT(PRED(n))))

# But:

try:
    FACT(THREE)
    assert False
except RecursionError:
    # Python is eager: it evaluates all before using, even when not used.
    pass

# We need Python to be lazier. These limitation are coming from Python
# interpreter limitation, not all our plays.
#
# Rules are broken in following code, just to accomodate Python interpreter.

LAZY_TRUE = lambda x: lambda y: x()
LAZY_FALSE = lambda x: lambda y: y()
IS_ZERO = lambda n: n(lambda _: LAZY_FALSE)(LAZY_TRUE)

FACT = lambda n: IS_ZERO(n)(lambda: ONE)(lambda: MUL(n)(FACT(PRED(n))))

assert FACT(THREE)(incr)(0) == 6


# No references

# We use fact name to define fact. That's against the rules!

# Let's do some exploration first.

fact = lambda n: 1 if n == 0 else n * fact(n - 1)

assert fact(5) == 120

# Make unwanted "global" a function argument.
fact = (lambda f: lambda n: 1 if n == 0 else n * f(n - 1))(fact)
assert fact(5) == 120

# Here, it is the same than
# assert 2 == (lambda y: y)(2)

# Try substitution.
fact = (lambda f: lambda n: 1 if n == 0 else n * f(n - 1))(
    lambda f: lambda n: 1 if n == 0 else n * f(n - 1)
)

assert fact(0) == 1
# But:
try:
    assert fact(1) == 1
except TypeError:  # TypeError: unsupported operand type(s) for *: 'int' and 'function'
    pass

# Hint: f takes 2 arguments, but only one is provided. Fix:

fact = (lambda f: lambda n: 1 if n == 0 else n * f(f)(n - 1))(
    lambda f: lambda n: 1 if n == 0 else n * f(f)(n - 1)
)

assert fact(0) == 1
assert fact(5) == 120

# Not beautiful with all those repetitions, but we can now drop the name.

assert (lambda f: lambda n: 1 if n == 0 else n * f(f)(n - 1))(
    lambda f: lambda n: 1 if n == 0 else n * f(f)(n - 1)
)(5) == 120


# Recursion

fact = (lambda f: lambda n: 1 if n == 0 else n * f(n - 1))(fact)

# Hint: try to extract the "middle" part.

R = lambda f: lambda n: 1 if n == 0 else n * f(n - 1)
fact = R(fact)  # We cheat here, as fact already exists. Otherwise, it would not be valid Python.
assert fact(5) == 120

# If a "x is fixed point of f" means f(f(x)) == f(x) == x,
# then fact is a fixed point of R.

# Suppose: Y(R) return a fixed point of R
#          That implies                 Y(R) = R(Y(R))
#          And (already done earlier)   Y(R) = (lambda x: R(x))(Y(R))
#          And, by repeating ourselves  Y(R) = (lambda x: R(x))((lambda x: R(x))(Y(R))
#          But we get to                Y(R) = (lambda x: R(x))(lambda x: R(x))
#          that miss one argument       Y(R) = (lambda x: R(x(x)))(lambda x: R(x(x)))
#          Now pull out the             Y(R) = (lambda f: (lambda x: f(x(x)))(lambda x: f(x(x))))(R)
#          Drop R, as it is present on both sides:

Y = lambda f: (lambda x: f(x(x)))(lambda x: f(x(x)))

# Welcome the Y combinator, invention (or discovery?) of Haskell B. Curry.

R = lambda f: lambda n: 1 if n == 0 else n * f(n - 1)

try:
    fact = Y(R)
except RecursionError:
    # Python has eager evaluation, once again!
    pass

# Python workaround, similar to def g(x): return f(x), i.e. wrapping:
Y = lambda f: (lambda x: f(lambda z: x(x)(z)))(lambda x: f(lambda z: x(x)(z)))
fact = Y(R)

# To be verified: it may be called the Z-combinator.

assert fact(5) == 120

fib = Y(lambda f: lambda n: 1 if n <= 2 else f(n - 1) + f(n - 2))
assert fib(10) == 55