import os


def test_shared_object_exists():
    # file_path = "./cFMS/libcFMS/.libs/libcFMS.so"
    assert os.path.exists("./cFMS/libcFMS/.libs/libcFMS.so")
