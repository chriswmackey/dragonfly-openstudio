# coding=utf-8
"""Utility functions for commonly-performed operations."""
from __future__ import division
import os

from ladybug.dt import DateTime
from ladybug.epw import EPW


def modelica_loads(load_file):
    """Parse Building loads from a .mos load file.

    This function also performs a check to ensure that the load profiles are annual.

    Args:
        load_file: A .mos file containing building loads.

    Returns:
        A tuple with four elements.

        -   seconds: A list of integers for the seconds of the year.

        -   cooling: A list of negative values for the cooling load in Watts.

        -   heating: A list of positive values for the heating load in Watts.

        -   swh: A list of positive values for the service hot water load in Watts.
    """
    seconds, cooling, heating, shw = [], [], [], []
    timeseries_started = False
    with open(load_file, 'r') as lf:
        for line in lf:
            if timeseries_started:
                loads = line.strip().split(';')
                seconds.append(int(loads[0]))
                cooling.append(float(loads[1]))
                heating.append(float(loads[2]))
                shw.append(float(loads[3]))
            elif line.startswith('double tab'):
                timeseries_started = True
    # check the timestep and get the peak values
    timestep = int(3600 / (seconds[1] - seconds[0]))
    assert len(cooling) == 8760 * timestep, 'The building loads simulation was '\
        'not for the full typical year and was for {} days.\nThe loads must be ' \
        'simulated for a full typical year to use them for DES generation.'.format(
            len(cooling) / (timestep * 24))
    return seconds, cooling, heating, shw


def system_coincident_peaks(sys_dict):
    """Gat the coincident peak values and datetimes associated with a system dictionary.

    Args:
        sys_dict: The URBANopt system parameter dictionary for which the coincident
            building peak will be evaluated.

    Returns:
        A tuple with two elements.

        -   peak_values: A list of 3 numbers for the cooling, heating, and shw peaks.

        -   peak_datetimes: A list of 3 DateTimes for the cooling, heating, and shw peaks.
    """
    # extract all of the loads from the modelica files
    cooling_mtx, heating_mtx, shw_mtx = [], [], []
    for bldg_dict in sys_dict['buildings']:
        load_file = bldg_dict['load_model_parameters']['time_series']['filepath']
        seconds, cooling, heating, shw = modelica_loads(load_file)
        cooling_mtx.append(cooling)
        heating_mtx.append(heating)
        shw_mtx.append(shw)
    step_seconds = seconds[1] - seconds[0]

    # determine the peak load and datetimes
    cooling = [sum(row) for row in zip(*cooling_mtx)]
    heating = [sum(row) for row in zip(*heating_mtx)]
    shw = [sum(row) for row in zip(*shw_mtx)]
    sort_cool, c_secs = zip(*sorted(zip(cooling, seconds), key=lambda x: x[0]))
    sort_heat, h_secs = zip(*sorted(zip(heating, seconds), key=lambda x: x[0]))
    sort_shw, s_secs = zip(*sorted(zip(shw, seconds), key=lambda x: x[0]))
    peak_cooling, cooling_time = sort_cool[0], c_secs[0]
    peak_heating, heating_time = sort_heat[-1], h_secs[-1]
    peak_shw, shw_time = sort_shw[-1], s_secs[-1]
    cooling_time = DateTime.from_moy((cooling_time - step_seconds) / 60)
    heating_time = DateTime.from_moy((heating_time - step_seconds) / 60)
    shw_time = DateTime.from_moy((shw_time - step_seconds) / 60)

    return (peak_cooling, peak_heating, peak_shw), (cooling_time, heating_time, shw_time)


def coincident_peak_design_days(sys_dict):
    """Get three DesignDay objects that align with the coincident peaks of a sys_dict.

    Args:
        sys_dict: The URBANopt system parameter dictionary for which the coincident
            building peak will be evaluated.

    Returns:
        A tuple with three elements.

        -   cooling_day: A DesignDay for the cooling coincident peak.

        -   heating_day: A DesignDay for the heating coincident peak.

        -   shw_day: A DesignDay for the service hot water coincident peak.
    """
    # get the peaks of the building loads
    _, peak_datetimes = system_coincident_peaks(sys_dict)
    cooling_time, heating_time, shw_time = peak_datetimes

    # load the EPW file to get other criteria of the design day
    epw_file = sys_dict['weather'].replace('.mos', '.epw')
    assert os.path.isfile(epw_file), 'The weather file path referenced in the ' \
        'system parameter file was not found: {}'.format(epw_file)
    epw_obj = EPW(epw_file)

    # create the design days with dates that align with the peak
    cooling_day = epw_obj.approximate_design_day('SummerDesignDay')
    heating_day = epw_obj.approximate_design_day('WinterDesignDay')
    shw_day = heating_day.duplicate()
    shw_day.name = shw_day.name.replace('Heating', 'SHW')
    cooling_day.sky_condition.date = cooling_time.date
    heating_day.sky_condition.date = heating_time.date
    shw_day.sky_condition.date = shw_time.date

    return cooling_day, heating_day, shw_day
