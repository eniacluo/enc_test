from glob import glob
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="helena",
    scripts=glob("bin/*"),
    ext_modules=cythonize("lib/*.py")
)
