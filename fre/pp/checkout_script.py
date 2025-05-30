'''
Description: Checkout script which accounts for 4 different scenarios: 
1. branch not given, folder does not exist,
2. branch given, folder does not exist, 
3. branch not given, folder exists, 
4. branch given and folder exists
'''
import os
import sys
import subprocess

import click

from fre import fre

FRE_WORKFLOWS_URL = 'https://github.com/NOAA-GFDL/fre-workflows.git'

def checkout_template(experiment = None, platform = None, target = None, branch = None):
    """
    Checkout the workflow template files from the repo
    """
    ## Chdir back to here before we exit this routine
    go_back_here = os.getcwd()

    # branch and version parameters
    default_tag = fre.version
    git_clone_branch_arg = branch if branch is not None else default_tag
    if branch is None:
        print(f"(checkout_script) default tag is '{default_tag}'")
    else:
        print(f"(checkout_script) requested branch/tag is '{branch}'")

    # check args + set the name of the directory
    if None in [experiment, platform, target]:
        raise ValueError( 'one of these are None: experiment / platform / target = \n'
                         f'{experiment} / {platform} / {target}' )
    name = f"{experiment}__{platform}__{target}"

    # Create the directory if it doesn't exist
    directory = os.path.expanduser("~/cylc-src")
    try:
        os.makedirs(directory, exist_ok = True)
    except Exception as exc:
        raise OSError(
            '(checkoutScript) directory {directory} wasnt able to be created. exit!') from exc

    checkout_exists = os.path.isdir(f'{directory}/{name}')

    if not checkout_exists: # scenarios 1+2, checkout doesn't exist, branch specified (or not)
        print(f'(checkout_script) checkout does not yet exist; will create now')
        clone_output = subprocess.run( ['git', 'clone','--recursive',
                                        f'--branch={git_clone_branch_arg}',
                                        FRE_WORKFLOWS_URL, f'{directory}/{name}'],
                                       capture_output = True, text = True, check = True)
        print(f'(checkout_script) {clone_output}')

    else:     # the repo checkout does exist, scenarios 3 and 4.
        os.chdir(f'{directory}/{name}')

        # capture the branch and tag
        # if either match git_clone_branch_arg, then success. otherwise, fail.

        current_tag = subprocess.run(["git","describe","--tags"],
                                     capture_output = True,
                                     text = True, check = True).stdout.strip()
        current_branch = subprocess.run(["git", "branch", "--show-current"],
                                         capture_output = True,
                                         text = True, check = True).stdout.strip()

        if current_tag == git_clone_branch_arg or current_branch == git_clone_branch_arg:
            print(f"(checkout_script) checkout exists ('{directory}/{name}'), and matches '{git_clone_branch_arg}'")
        else:
            print(f"(checkout_script) ERROR: checkout exists ('{directory}/{name}') and does not match '{git_clone_branch_arg}'")
            print(f"(checkout_script) ERROR: current branch is '{current_branch}', current tag-describe is '{current_tag}'")
            exit(1)

    # make sure we are back where we should be
    if os.getcwd() != go_back_here:
        os.chdir(go_back_here)

    return 0

#############################################

@click.command()
def _checkout_template(experiment, platform, target, branch ):
    '''
    Wrapper script for calling checkout_template - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return checkout_template(experiment, platform, target, branch)


if __name__ == '__main__':
    checkout_template()
