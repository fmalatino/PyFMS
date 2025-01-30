#!/usr/bin/env python3

import ctypes as ct

import numpy as np


"""
This module allows for conversion between Python object and ctypes objects.
for use in the C based methods which wrap the Fortan FMS source methods.

Array methods: Will return an instance of the object passed and a pointer to
               the object. Arrays are mutable types in Python and do not
               require the a ctypes object to wrap it. If the array object
               is updated by the method the original Python object will
               also contain these updates

Scalar methods: Will return a reference to a ctypes object wrapping the passed
                Python object and a pointer to the new ctypes object.
                Scalar Python types are not mutable, and if method calling a
                pyFMS_data_handling method is expected to update the passed
                Python object, the calling method should not only create an
                explicit ctypes object to wrap passed Python object, but also
                return the value of the ctypes object to update the value.

Example: Wrapping C function that updates an integer and an array

def wrapper_func(py_scalar_obj: int, py_array_obj: npt.NDArray[int])-> int:
    _c_func = clib.c_func

    c_scalar_obj = ctypes.c_int(py_scalar_obj)
    c_array_p, c_array_t = setarray_Cint32(py_array_obj)

    _c_func.argtypes = [ctype.POINTER(ctype.c_int), c_array_t]
    _c_func.restype = None

    _c_func(ctypes.byref(c_scalar_obj), c_array_p)

    return c_scalar_obj.value


x = # some value
var_array = # some numpy array

x = wrapper_func(x, var_array)
"""

"""
Array setting methods
"""


def set_ndpointer(arg, c_type):
    return np.ctypeslib.ndpointer(
        dtype=c_type, ndim=arg.ndim, shape=arg.shape, flags="FORTRAN"
    )


def setarray_Cbool(arg):
    if arg[0] is None:
        return None, ct.POINTER(ct.c_bool)
    else:
        return arg, set_ndpointer(arg, ct.c_bool)


def setarray_Cdouble(arg):
    if arg[0] is None:
        return None, ct.POINTER(ct.c_double)
    else:
        return arg, set_ndpointer(arg, ct.c_double)


def setarray_Cfloat(arg):
    if arg[0] is None:
        return None, ct.POINTER(ct.c_float32)
    else:
        return arg, set_ndpointer(arg, ct.c_float)


def setarray_Cint32(arg):
    if arg[0] is None:
        return None, ct.POINTER(ct.c_int)
    else:
        return arg, set_ndpointer(arg, ct.c_int)


def set_double_pointer(arg, ctype):
    if arg[0] is None:
        return None, ct.POINTER(ct.POINTER(ctype))
    else:
        rows = arg.shape[0]
        row_ptrs = (ct.POINTER(ctype) * rows)()
        for i in range(rows):
            row_ptrs[i] = arg[i].ctypes.data_as(ct.POINTER(ctype))
        return row_ptrs, ct.POINTER(ct.POINTER(ctype))


"""
Scalar setting methods
"""


def setscalar_Cbool(arg):
    if arg is None:
        return arg, ct.POINTER(ct.c_double)
    else:
        return ct.byref(ct.c_bool(arg)), ct.POINTER(ct.c_bool)


def set_Cchar(arg):
    if arg is None:
        return arg, ct.c_char_p
    else:
        return arg.encode("utf-8"), ct.c_char_p


def setscalar_Cdouble(arg):
    if arg is None:
        return arg, ct.POINTER(ct.c_double)
    else:
        return ct.byref(ct.c_double(arg)), ct.POINTER(ct.c_double)


def setscalar_Cfloat(arg):
    if arg is None:
        return arg, ct.POINTER(ct.c_float)
    else:
        return ct.byref(ct.c_float(arg)), ct.POINTER(ct.c_float)


def setscalar_Cint32(arg):
    if arg is None:
        return arg, ct.POINTER(ct.c_int)
    else:
        return ct.byref(ct.c_int(arg)), ct.POINTER(ct.c_int)
