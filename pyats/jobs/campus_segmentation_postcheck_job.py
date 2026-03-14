from pyats.easypy import run

def main():
    run(
        testscript="pyats/tests/campus_segmentation_postcheck.py",
        testbed="pyats/testbeds/campus_testbed.yml",
    )
