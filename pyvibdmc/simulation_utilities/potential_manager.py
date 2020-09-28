import multiprocessing as mp
import os
import sys
import time

import numpy as np


class Potential:
    """
    A potential handler that is able to call python functions that
    call .so files, either generated by f2py or loaded in by ctypes.
    :param potential_function: The name of a python function (user specified) that will take in a n x m x 3 stack of geometries and return a 1D numpy array filled with potential values in hartrees.
    :type potential_function: str
    :param potential_dir: The *absolute path* to the directory that contains the .so file and .py file. If it"s a python function, then just the absolute path to your .py file.
    :type: str
    :param pool: Will create a pool of <pool> processes using Python"s multiprocessing module. This should never be larger than the number of processors on the machine this code is run.
    :type: int
    """

    def __init__(self,
                 potential_function,
                 potential_directory,
                 python_file,
                 pool=0
                 ):

        self.pot_func = potential_function
        self.pyFile = python_file
        self.pot_dir = potential_directory
        self.pool = pool
        self._init_pot()

    def _init_pot(self):
        """
        Given the directory, this will cd over to the potential directory and (optionally) start a pool there, which
        can call the python function that calls the potential.
        """
        import importlib
        # Go to potential directory that houses python function and assign a self._pot variable to it
        self._curdir = os.getcwd()
        os.chdir(self.pot_dir)
        sys.path.insert(0, os.getcwd())
        module = self.pyFile.split(".")[0]
        x = importlib.import_module(module)
        self._pot = getattr(x, self.pot_func)

        if self.pool > 1:
            # initialize pool
            self._potPool = mp.Pool(self.pool)
        else:
            self._potPool = None

        os.chdir(self._curdir)

    def getpot(self, cds, timeit=False):
        """
        Uses the potential function we got to call potential
        :param cds: A stack of geometries (nxmx3, n=num_geoms;m=num_atoms;3=x,y,z) whose energies we need
        :type cds: np.ndarray
        :param timeit: The logger telling the potential manager whether or not to time the potential call
        :type timeit: bool

        """
        if timeit:
            start = time.time()
        os.chdir(self.pot_dir)
        if self._potPool is not None:
            cds = np.array_split(cds, self.pool)
            res = self._potPool.map(self._pot, cds)
            v = np.concatenate((res))
        else:
            v = self._pot(cds)
        os.chdir(self._curdir)
        if timeit:
            elapsed = time.time()-start
            return v, elapsed
        else:
            return v
