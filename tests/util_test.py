# coding=utf-8
import json
from ladybug.dt import Date
from dragonfly_openstudio.util import coincident_peak_design_days


def test_coincident_peak_design_days():
    """Test the ghe_des_to_openstudio function."""
    sp_json = './tests/assets/small_ghe/system_params.json'
    with open(sp_json) as json_file:
        sys_dict = json.load(json_file)

    cooling_day, heating_day, shw_day = coincident_peak_design_days(sys_dict)
    assert cooling_day.sky_condition.date == Date(7, 3)
    assert heating_day.sky_condition.date == Date(1, 4)
    assert shw_day.sky_condition.date == Date(2, 15)
