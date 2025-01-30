# TODO: To be replaced with mpp_error

import traceback


def pyfms_error(mod_name: str, method_name: str, err_msg: str):
    print(f"ERROR: {mod_name}::{method_name}: {err_msg}")
    traceback.print_exc()
