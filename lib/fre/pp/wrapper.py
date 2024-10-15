"""
frepp.py, a replacement for the frepp bash script located at:
https://gitlab.gfdl.noaa.gov/fre2/system-settings/-/blob/main/bin/frepp
Author: Carolyn.Whitlock
"""

#todo:
# add relative path import to rest of pp tools
# add command-line args using same format as fre.py
# include arg for pp start / stop
# test yaml path
# error handling

import os
import time
import click

# Import from the local packages
from .checkoutScript import _checkoutTemplate
from .configure_script_xml import _convert
from .configure_script_yaml import _yamlInfo
from .validate import _validate_subtool
from .install import _install_subtool
from .run import _pp_run_subtool
from .status import _status_subtool

@click.command()
def runFre2pp(experiment, platform, target, config_file, branch):
    '''
    Wrapper script for calling a FRE2 pp experiment with the canopy-style
    infrastructure and fre-cli
    time=0000
    '''

    config_file = os.path.abspath(config_file)

    #env_setup
    #todo: check for experiment existing, call frepp_stop to clean experiment,
    try:
        print("calling _checkoutTemplate")
        _checkoutTemplate(experiment, platform, target, branch)
    except Exception as err:
        raise

    #dumb xml check;does it need to be smarter?
    is_xml = config_file[-3:] == "xml"
    if is_xml:
        #TODO: should this prompt for pp start/stop years?
        try:
            _convert(config_file, platform, target, experiment, do_analysis=False)
            #note: arg list for this function is a looooot longer, but all those
            #args can be deduced from the xml when given default vals
        except Exception as err:
            raise
        try:
            _validate_subtool(experiment, platform, target)
            #See notes in main() function
        except Exception as err:
            raise
    else:
        try:
            _yamlInfo(config_file, experiment, platform, target)
        except Exception as err:
            raise

    try:
        _install_subtool(experiment, platform, target)
    except:
        raise

    try:
        _pp_run_subtool(experiment, platform, target)
    except Exception as err:
        raise

    #send off a watcher script that reports on how it's going
    for n in range(1,12):
        try:
            _status_subtool(experiment, platform, target)
        except Exception as err:
            raise
        time.sleep(300)

if __name__ == '__main__':
    runFre2pp()
