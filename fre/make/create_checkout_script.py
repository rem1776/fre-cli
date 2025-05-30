'''
checks out a makefile for a given model from the yamls
i think!
'''

import os
import subprocess
import logging
import sys
import click
import fre.yamltools.combine_yamls as cy
from .gfdlfremake import varsfre, yamlfre, checkout, targetfre

def checkout_create(yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose):
    # Define variables
    yml = yamlfile
    name = yamlfile.split(".")[0]
    run = execute
    jobs = str(jobs)
    pcheck = no_parallel_checkout

    if pcheck:
        pc = ""
    else:
        pc = " &"

    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    src_dir="src"
    checkout_script_name = "checkout.sh"
    baremetal_run = False # This is needed if there are no bare metal runs

    ## Split and store the platforms and targets in a list
    plist = platform
    tlist = target

    # Combine model, compile, and platform yamls
    # Default behavior - combine yamls / rewrite combined yaml
    comb = cy.init_compile_yaml(yml,platform,target)
    full_combined = cy.get_combined_compileyaml(comb)

    ## Get the variables in the model yaml
    fre_vars = varsfre.frevars(full_combined)

    ## Open the yaml file, validate the yaml, and parse as fremake_yaml
    model_yaml = yamlfre.freyaml(full_combined,fre_vars)
    fremake_yaml = model_yaml.getCompileYaml()

    ## Error checking the targets
    for target_name in tlist:
        target = targetfre.fretarget(target_name)

    ## Loop through the platforms specified on the command line
    ## If the platform is a baremetal platform, write the checkout script and run it once
    ## This should be done separately and serially because bare metal platforms should all be using
    ## the same source code.
    for platform_name in plist:
        if model_yaml.platforms.hasPlatform(platform_name):
            pass
        else:
            raise ValueError (platform_name + " does not exist in platforms.yaml")

        platform = model_yaml.platforms.getPlatformFromName(platform_name)

        # ceate the source directory for the platform
        if not platform["container"]:
            src_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/src"
            # if the source directory does not exist, it is created
            if not os.path.exists(src_dir):
                os.system("mkdir -p " + src_dir)
            # if the checkout script does not exist, it is created
            if not os.path.exists(src_dir+"/checkout.sh"):
                fre_checkout = checkout.checkout("checkout.sh",src_dir)
                fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(),jobs,pc)
                fre_checkout.finish(pc)
                # Make checkout script executable
                os.chmod(src_dir+"/checkout.sh", 0o744)
                print("\nCheckout script created in "+ src_dir + "/checkout.sh \n")

                # Run the checkout script
                if run:
                    fre_checkout.run()
                else:
                    sys.exit()
            else:
                print("\nCheckout script PREVIOUSLY created in "+ src_dir + "/checkout.sh \n")
                if run:
                    try:
                        subprocess.run(args=[src_dir+"/checkout.sh"], check=True)
                    except:
                        print("\nThere was an error with the checkout script "+src_dir+"/checkout.sh.",
                              "\nTry removing test folder: " + platform["modelRoot"] +"\n")
                        raise
                else:
                    sys.exit()

        else:
            image="ecpe4s/noaa-intel-prototype:2023.09.25"
            bld_dir = platform["modelRoot"] + "/" + fremake_yaml["experiment"] + "/exec"
            tmp_dir = "tmp/"+platform_name
            fre_checkout = checkout.checkoutForContainer("checkout.sh", src_dir, tmp_dir)
            fre_checkout.writeCheckout(model_yaml.compile.getCompileYaml(),jobs,pc)
            fre_checkout.finish(pc)
            print("\nCheckout script created at " + tmp_dir + "/checkout.sh" + "\n")

@click.command()
def _checkout_create(yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose):
    '''
    Decorator for calling checkout_create - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return checkout_create(yamlfile,platform,target,no_parallel_checkout,jobs,execute,verbose)

if __name__ == "__main__":
    checkout_create()
