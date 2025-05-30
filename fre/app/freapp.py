#!/usr/bin/env python3
''' fre app calls '''

import time

import click

from .mask_atmos_plevel import mask_atmos_plevel_subtool
from .generate_time_averages.generate_time_averages import generate
from .regrid_xy.regrid_xy import _regrid_xy

@click.group(help=click.style(" - access fre app subcommands", fg=(250,154,90)))
def app_cli():
    ''' entry point to fre app click commands '''

@app_cli.command()
@click.option("-i", "--input_dir",
              type = str,
              help = "`inputDir` / `input_dir` (env var) specifies input directory to regrid, " + \
                     "typically an untarredv history file archive" ,
              required = True)
@click.option("-o", "--output_dir",
              type = str,
              help = "`outputDir` / `output_dir` (env var) specifies target location for output" + \
                     " regridded files",
              required = True)
@click.option("-b", "--begin",
              type = str,
              help = "`begin` / `begin` (env var) ISO8601 datetime format specification for" + \
                     " starting date of data, part of input target file name",
              required = True)
@click.option("-tmp", "--tmp_dir",
              type = str,
              help = "`TMPDIR` / `tmp_dir` (env var) temp directory for location of file " + \
                     "read/writes",
              required = True)
@click.option("-rd", "--remap_dir",
              type = str,
              help = "`fregridRemapDir` / `remap_dir` (env var) directory containing remap file" + \
                     " for regridding",
              required = True)
@click.option("-s", "--source",
              type = str,
              help = "`source` / `source` (env var) source name for input target file name " + \
                     "within input directory to target for regridding. the value for `source` " + \
                     "must be present in at least one component's configuration fields",
              required = True)
@click.option("-g", "--grid_spec",
              type = str,
              help = "`gridSpec` / `grid_spec` (env var) file containing mosaic for regridding",
              required = True)
@click.option("-xy", "--def_xy_interp",
              type = str,
              help = "`defaultxyInterp` / `def_xy_interp` (env var) default lat/lon resolution " + \
                     "for output regridding. (change me? TODO)",
              required = True)
@click.pass_context
def regrid(context,
              input_dir, output_dir, begin, tmp_dir,
              remap_dir, source, grid_spec, def_xy_interp ):
    # pylint: disable=unused-argument
    ''' regrid target netcdf file '''
    context.forward(_regrid_xy)

@app_cli.command()
@click.option("-i", "--infile",
              type = str,
              help = "Input NetCDF file containing pressure-level output to be masked",
              required = True)
@click.option("-o", "--outfile",
              type = str,
              help = "Output file",
              required = True)
@click.option("-p", "--psfile", # surface pressure... ps? TODO
              help = "Input NetCDF file containing surface pressure (ps)",
              required = True)
@click.pass_context
def mask_atmos_plevel(context, infile, outfile, psfile):
    # pylint: disable = unused-argument
    """Mask out pressure level diagnostic output below land surface"""
    context.forward(mask_atmos_plevel_subtool)


@app_cli.command()
@click.option("-i", "--inf",
              type = str,
              required = True,
              help = "Input file name")
@click.option("-o", "--outf",
              type = str,
              required = True,
              help = "Output file name")
@click.option("-p", "--pkg",
              type = click.Choice(["cdo","fre-nctools","fre-python-tools"]),
              default = "cdo",
              help = "Time average approach")
@click.option("-v", "--var",
              type = str,
              default = None,
              help = "Specify variable to average")
@click.option("-u", "--unwgt",
              is_flag = True,
              default = False,
              help = "Request unweighted statistics")
@click.option("-a", "--avg_type",
              type = click.Choice(["month","seas","all"]),
              default = "all",
              help = "Type of time average to generate. \n \
                     currently, fre-nctools and fre-python-tools pkg options\n \
                     do not support seasonal and monthly averaging.\n")
@click.option("-s", "--stddev_type",
              type = click.Choice(["samp","pop","samp_mean","pop_mean"]),
              default = "samp",
              help = "Compute standard deviations for time-averages as well")
@click.pass_context
def gen_time_averages(context, inf, outf, pkg, var, unwgt, avg_type, stddev_type):
    # pylint: disable = unused-argument
    """
    generate time averages for specified set of netCDF files. 
    Example: generate-time-averages.py /path/to/your/files/
    """
    start_time = time.perf_counter()
    context.forward(generate)
    # need to change to a click.echo, not sure if echo supports f strings
    print(f'Finished in total time {round(time.perf_counter() - start_time , 2)} second(s)')

if __name__ == "__main__":
    app_cli()
