import os

from mpi4py import MPI

from pyfms import pyFMS


def test_pyfms_init():
    assert os.path.exists("./cFMS/libcFMS/.libs/libcFMS.so")

    fcomm = MPI.COMM_WORLD.py2f()

    pyfmsobj = pyFMS(
        localcomm=fcomm,
        clibFMS_path="./cFMS/libcFMS/.libs/libcFMS.so",
    )

    assert isinstance(pyfmsobj, pyFMS)

    pyfmsobj.pyfms_end()
