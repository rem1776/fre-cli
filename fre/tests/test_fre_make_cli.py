''' test "fre make" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre_make():
    ''' fre make '''
    result = runner.invoke(fre.fre, args=["make"])
    assert result.exit_code == 0

def test_cli_fre_make_help():
    ''' fre make --help '''
    result = runner.invoke(fre.fre, args=["make", "--help"])
    assert result.exit_code == 0

def test_cli_fre_make_opt_dne():
    ''' fre make optionDNE '''
    result = runner.invoke(fre.fre, args=["make", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_make_null_model_build_baremetal():
    ''' fre make --help '''
    result = runner.invoke(fre.fre, args=["make", "run-fremake", "-y", "/fre-cli/fre/make/tests/null_example/null_model.yaml", "-p", "ci.gnu", "-t", "debug"])
    assert result.exit_code == 0
