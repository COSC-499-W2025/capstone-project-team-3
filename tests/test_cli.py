"""
Test for the CLI placeholder (app/cli.py).

Goal:
Make sure the CLI runs successfully and prints the expected output
without errors — this confirms that argparse is configured correctly
and that we can later extend it safely.
"""

from app.cli import main

def test_cli_prints(capsys):
    """
    Why pass []:
        - Normally, argparse reads global sys.argv.
        - When pytest runs, sys.argv includes flags like "-v" or "-q",
          which would break the CLI parser ("unrecognized arguments: -v").
        - By passing an empty list, we isolate the test from pytest’s arguments.
    """
    main([]) 

    # Capture all output printed to stdout/stderr
    captured = capsys.readouterr()

    assert "CLI started" in captured.out
