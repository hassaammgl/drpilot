"""Smoke test so pytest is green from day one."""
import pmp


def test_package_imports():
    assert pmp.__version__ == "0.0.1"
