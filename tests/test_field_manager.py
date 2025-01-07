import os

import pytest
import yaml

from pyfms import FieldError, FieldTable


test_config = {
    "field_table": [
        {
            "field_type": "tracer",
            "modlist": [
                {
                    "model_type": "atmos_mod",
                    "varlist": [
                        {
                            "variable": "sphum",
                            "longname": "specific humidity",
                            "units": "kg/kg",
                            "profile_type": [
                                {"value": "fixed", "surface_value": 3e-06}
                            ],
                        },
                        {
                            "variable": "soa",
                            "longname": "SOA tracer",
                            "units": "mmr",
                            "convection": "all",
                            "chem_param": [
                                {
                                    "value": "aerosol",
                                    "frac_pm1": 0.89,
                                    "frac_pm25": 0.96,
                                    "frac_pm10": 1.0,
                                }
                            ],
                            "profile_type": [
                                {"value": "fixed", "surface_value": 1e-32}
                            ],
                        },
                    ],
                }
            ],
        }
    ]
}


@pytest.fixture(scope="session")
def temp_file(tmpdir_factory):
    file_path = tmpdir_factory.mktemp("data").join("test_fm.yaml")
    with open(file_path, "w") as f:
        yaml.dump(test_config, f)
    yield file_path
    os.remove(file_path)


def test_fieldtable_init(temp_file):
    test_table = FieldTable.from_file(temp_file)
    assert isinstance(test_table, FieldTable)


def test_get_fieldtype(temp_file):
    test_table = FieldTable.from_file(temp_file)
    fieldtype = test_table.field_type
    assert fieldtype == "tracer"


@pytest.mark.xfail(raises=FieldError)
def test_remove_varlist(temp_file):
    with open(temp_file, "r") as f:
        changed_config = yaml.safe_load(f)
    del changed_config["field_table"][0]["modlist"][0]["varlist"]
    FieldTable.from_dict(changed_config)


def test_add_to_varlist(temp_file):
    test_table = FieldTable.from_file(temp_file)
    new_var = {
        "variable": "test",
        "longname": "longtest",
        "units": "m",
        "profile_type": "fixed",
        "subparams": [{"surface_value": 1}],
    }
    test_table.add_to_varlist(module="atmos_mod", var=new_var)
    varlist = [mod for mod in test_table.modlist if mod["model_type"] == "atmos_mod"][
        0
    ]["varlist"]
    assert new_var in varlist


@pytest.mark.xfail(raises=(AttributeError, FieldError, KeyError))
def test_add_to_varlist_fail(temp_file):
    with open(temp_file, "r") as f:
        changed_config = yaml.safe_load(f)
    del changed_config["field_table"][0]["modlist"][0]["varlist"]
    test_table = FieldTable.from_dict(changed_config)
    new_var = {
        "variable": "test",
        "longname": "longtest",
        "units": "m",
        "profile_type": "fixed",
        "subparams": [{"surface_value": 1}],
    }
    test_table.add_to_varlist(module="atmos_mod", var=new_var)


def test_get_var(temp_file):
    test_table = FieldTable.from_file(temp_file)
    var = test_table.get_var(module="atmos_mod", varname="soa")
    assert var == test_table.modlist[0]["varlist"][1]


@pytest.mark.xfail(raises=FieldError)
def test_get_var_fail(temp_file):
    with open(temp_file, "r") as f:
        config = yaml.safe_load(f)
        test_table = FieldTable.from_dict(config)
    test_table.get_var(module="atmos_mod", varname="sob")


def test_get_subparam(temp_file):
    test_table = FieldTable.from_file(temp_file)
    subparameter = test_table.get_subparam(
        module="atmos_mod", varname="soa", subparam_name="chem_param"
    )
    assert subparameter == test_table.modlist[0]["varlist"][1]["chem_param"]


def test_get_value(temp_file):
    test_table = FieldTable.from_file(temp_file)
    value = test_table.get_value(module="atmos_mod", varname="soa", key="units")
    assert value == "mmr"


@pytest.mark.xfail(raises=KeyError)
def test_get_value_key_fail(temp_file):
    with open(temp_file, "r") as f:
        config = yaml.safe_load(f)
        test_table = FieldTable.from_dict(config)
    test_table.get_value(module="atmos_mod", varname="soa", key="unit")


def test_get_subparam_value(temp_file):
    test_table = FieldTable.from_file(temp_file)
    value = test_table.get_subparam_value(
        module="atmos_mod",
        varname="soa",
        listname="chem_param",
        paramname="frac_pm1",
    )
    assert value == 0.89


@pytest.mark.xfail(raises=KeyError)
def test_get_subparam_value_bad_key(temp_file):
    with open(temp_file, "r") as f:
        config = yaml.safe_load(f)
        test_table = FieldTable.from_dict(config)
    test_table.get_subparam_value(
        module="atmos_mod",
        varname="soa",
        listname="chem_param",
        paramname="frac_pms",
    )


@pytest.mark.xfail(raises=TypeError)
def test_get_subparam_value_bad_var_name(temp_file):
    with open(temp_file, "r") as f:
        config = yaml.safe_load(f)
        test_table = FieldTable.from_dict(config)
    test_table.get_subparam_value(
        module="atmos_mod", varname="sob", listname="chem_param", paramname="frac_pm1"
    )


def test_get_variable_list(temp_file):
    test_table = FieldTable.from_file(temp_file)
    test_list = test_table.get_variable_list(module="atmos_mod")
    assert test_list == ["sphum", "soa"]


def test_get_num_variables(temp_file):
    test_table = FieldTable.from_file(temp_file)
    num_vars = test_table.get_num_variables(module="atmos_mod")
    assert num_vars == 2


def test_get_subparam_list(temp_file):
    test_table = FieldTable.from_file(temp_file)
    test_list = test_table.get_subparam_list(module="atmos_mod", varname="soa")
    assert test_list == ["chem_param", "profile_type"]


def test_get_num_subparam(temp_file):
    test_table = FieldTable.from_file(temp_file)
    num = test_table.get_num_subparam(module="atmos_mod", varname="soa")
    assert num == 2


def test_set_value(temp_file):
    test_table = FieldTable.from_file(temp_file)
    test_table.set_value(module="atmos_mod", varname="soa", key="units", value="m")
    varlist = [mod for mod in test_table.modlist if mod["model_type"] == "atmos_mod"][
        0
    ]["varlist"]
    assert varlist[1]["units"] == "m"


def test_set_subparam_value(temp_file):
    test_table = FieldTable.from_file(temp_file)
    test_table.set_subparam_value(
        module="atmos_mod",
        varname="soa",
        listname="chem_param",
        subparamname="frac_pm1",
        value=1,
    )
    varlist = [mod for mod in test_table.modlist if mod["model_type"] == "atmos_mod"][
        0
    ]["varlist"]
    assert varlist[1]["chem_param"][0]["frac_pm1"] == 1


def test_set_var_name(temp_file):
    test_table = FieldTable.from_file(temp_file)
    test_table.set_var_name(module="atmos_mod", old_name="soa", new_name="soc")
    varlist = [mod for mod in test_table.modlist if mod["model_type"] == "atmos_mod"][
        0
    ]["varlist"]
    assert varlist[1]["variable"] == "soc"


def test_set_var_attr_name(temp_file):
    test_table = FieldTable.from_file(temp_file)
    test_table.set_var_attr_name(
        module="atmos_mod", varname="soa", oldname="longname", newname="ln"
    )
    varlist = [mod for mod in test_table.modlist if mod["model_type"] == "atmos_mod"][
        0
    ]["varlist"]
    assert varlist[1]["ln"]


@pytest.mark.xfail(raises=FieldError)
def test_set_var_attr_name_duplicate(temp_file):
    with open(temp_file, "r") as f:
        config = yaml.safe_load(f)
        test_table = FieldTable.from_dict(config)
    test_table.set_var_attr_name(
        module="atmos_mod", varname="soa", oldname="longname", newname="longname"
    )


def test_set_subparam_name(temp_file):
    test_table = FieldTable.from_file(temp_file)
    test_table.set_subparam_name(
        module="atmos_mod",
        varname="soa",
        listname="chem_param",
        oldname="frac_pm1",
        newname="frac_pm2",
    )
    varlist = [mod for mod in test_table.modlist if mod["model_type"] == "atmos_mod"][
        0
    ]["varlist"]
    assert varlist[1]["chem_param"][0]["frac_pm2"]


@pytest.mark.xfail(raises=FieldError)
def test_set_subparam_name_duplicate(temp_file):
    with open(temp_file, "r") as f:
        config = yaml.safe_load(f)
        test_table = FieldTable.from_dict(config)
    test_table.set_subparam_name(
        module="atmos_mod",
        varname="soa",
        listname="chem_param",
        oldname="frac_pm1",
        newname="frac_pm1",
    )
