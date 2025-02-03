#!/usr/bin/env python3

import ctypes as ct
from typing import Tuple

import numpy as np
import numpy.typing as npt


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

All passed in NumPy arrays must make use of the "FORTRAN" flag during
initialization

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


def set_ndpointer(arg: npt.NDArray) -> np.ctypeslib.ndpointer:
    c_type = np.ctypeslib.as_ctypes_type(arg.dtype)
    return np.ctypeslib.ndpointer(
        dtype=c_type, ndim=arg.ndim, shape=arg.shape, flags="FORTRAN"
    )


def setarray_Cbool(
    arg: npt.NDArray[np.bool_],
) -> Tuple[npt.NDArray[np.bool_], np.ctypeslib.ndpointer]:
    return arg, set_ndpointer(arg)


def setarray_Cdouble(
    arg: npt.NDArray[np.float64],
) -> Tuple[npt.NDArray[np.float64], np.ctypeslib.ndpointer]:
    return arg, set_ndpointer(arg)


def setarray_Cfloat(
    arg: npt.NDArray[np.float32],
) -> Tuple[npt.NDArray[np.float32], np.ctypeslib.ndpointer]:
    return arg, set_ndpointer(arg)


def setarray_Cint32(
    arg: npt.NDArray[np.int32],
) -> Tuple[npt.NDArray[np.int32], np.ctypeslib.ndpointer]:
    return arg, set_ndpointer(arg)


"""
set_multipointer:
    For converting NumPy arrays to pointer equivalent
    This method is able to convert a Numpy array of
    up to 5 dimensions to quintuple pointer (*****).

    If an array of <= 1 or > 5 dimensions is passed
    as an argument, the method will default to the
    returning the passed array and the result of a
    pass to set_ndpointer.
"""


def set_multipointer(arg: npt.NDArray, num_ptr: int) -> Tuple:
    c_type = np.ctypeslib.as_ctypes_type(arg.dtype)
    match num_ptr:
        case 2:
            d_pointer = ct.POINTER(ct.POINTER(c_type))
            arg_ptr = (ct.POINTER(c_type) * arg.shape[0])()
            for i in range(arg.shape[0]):
                arg_ptr[i] = arg[i].ctypes.data_as(ct.POINTER(c_type))
            return arg_ptr, d_pointer
        case 3:
            t_ptr = ct.POINTER(ct.POINTER(ct.POINTER(c_type)))
            arg_ptr = (ct.POINTER(ct.POINTER(c_type)) * arg.shape[0])()
            for i in range(arg.shape[0]):
                arg_ptr[i] = (ct.POINTER(c_type) * arg.shape[1])()
                for j in range(arg.shape[1]):
                    arg_ptr[i][j] = arg[i][j].ctypes.data_as(ct.POINTER(c_type))
            return arg_ptr, t_ptr
        case 4:
            quad_ptr = ct.POINTER(ct.POINTER(ct.POINTER(ct.POINTER(c_type))))
            arg_ptr = (ct.POINTER(ct.POINTER(ct.POINTER(c_type))) * arg.shape[0])()
            for i in range(arg.shape[0]):
                arg_ptr[i] = (ct.POINTER(ct.POINTER(c_type)) * arg.shape[1])()
                for j in range(arg.shape[1]):
                    arg_ptr[i][j] = (ct.POINTER(c_type) * arg.shape[2])()
                    for k in range(arg.shape[2]):
                        arg_ptr[i][j][k] = arg[i][j][k].ctypes.data_as(
                            ct.POINTER(c_type)
                        )
            return arg_ptr, quad_ptr
        case 5:
            quint_ptr = ct.POINTER(
                ct.POINTER(ct.POINTER(ct.POINTER(ct.POINTER(c_type))))
            )
            arg_ptr = (
                ct.POINTER(ct.POINTER(ct.POINTER(ct.POINTER(c_type)))) * arg.shape[0]
            )()
            for i in range(arg.shape[0]):
                arg_ptr[i] = (
                    ct.POINTER(ct.POINTER(ct.POINTER(c_type))) * arg.shape[1]
                )()
                for j in range(arg.shape[1]):
                    arg_ptr[i][j] = (ct.POINTER(ct.POINTER(c_type)) * arg.shape[2])()
                    for k in range(arg.shape[2]):
                        arg_ptr[i][j][k] = (ct.POINTER(c_type) * arg.shape[3])()
                        for n in range(arg.shape[3]):
                            arg_ptr[i][j][k][n] = arg[i][j][k][n].ctypes.data_as(
                                ct.POINTER(c_type)
                            )
            return arg_ptr, quint_ptr
        case _:
            return arg, set_ndpointer(arg)


"""
Scalar setting methods
"""


def setscalar_Cbool(arg: bool) -> Tuple:
    if arg is None:
        return None, None, ct.POINTER(ct.c_bool)
    else:
        arg_c = ct.c_bool(arg)
        return arg_c, ct.byref(arg_c), ct.POINTER(ct.c_bool)


def set_Cchar(arg: str) -> Tuple:
    if arg is None:
        return None, ct.c_char_p
    else:
        return ct.create_string_buffer(arg.encode("utf-8")), ct.c_char_p


def setscalar_Cdouble(arg: float) -> Tuple:
    if arg is None:
        return None, None, ct.POINTER(ct.c_double)
    else:
        arg_c = ct.c_double(arg)
        return arg_c, ct.byref(arg_c), ct.POINTER(ct.c_double)


def setscalar_Cfloat(arg: float) -> Tuple:
    if arg is None:
        return None, None, ct.POINTER(ct.c_float)
    else:
        arg_c = ct.c_float(arg)
        return arg_c, ct.byref(arg_c), ct.POINTER(ct.c_float)


def setscalar_Cint32(arg: int) -> Tuple:
    if arg is None:
        return None, None, ct.POINTER(ct.c_int)
    else:
        arg_c = ct.c_int(arg)
        return arg_c, ct.byref(arg_c), ct.POINTER(ct.c_int)
