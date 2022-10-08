# Codes for acoustical simulation

This is the acoustical simulation. It exists in multiple versions:

* cadsd_py.py is the python implementation.
* _cadsd.pyx is the cython implementation. It is very similar to the python implementation, but it is about 100 times faster. Needs to be compiled.

The acoustical simulation has a wrapper, cadsd.py (cython) and cadsd_py.py (python) for higher level access.