import multiprocessing as mp
import os,sys
import numpy as np

class Potential:
    def __init__(self,
                 potential_function,
                 python_file,
                 potential_directory,
                 pool=0
                 ):
        """
        A potential handler that is able to call python functions that
        call .so files, either generated by f2py or loaded in by ctypes.
        @param potential_function: The name of a python function (user specified) that will take in a n x m x 3 stack of
         geometries and return a 1D numpy array filled with potential values in hartrees.
        @type potential_function:str
        @param potential_dir: The *absolute path* to the directory that contains the .so file and .py file. If it"s
        a python function, then just the absolute path to your .py file.
        @type:str
        @param pool: Will create a pool of <pool> processes using Python"s multiprocessing module. This should never
        be larger than the number of processors on the machine this code is run.
        @type:int
        """
        self.pot_func = potential_function
        self.pyFile = python_file
        self.pot_dir = potential_directory
        self.pool = pool
        self.initialize()

    def initialize(self):
        if self.pool > 1:
            #initialize pool
            self._potPool = mp.Pool(self.pool)
        else:
            self._potPool = None
        self._init_pot()

    def _init_pot(self):
        import importlib
        """Go to potential directory that houses python function and assign a self._pot variable to it"""
        cur_dir = os.getcwd()
        os.chdir(self.pot_dir)
        sys.path.insert(0, self.pot_dir)
        print(os.getcwd())
        module = self.pyFile.split(".")[0]
        x = importlib.import_module(module)
        print(x)
        self._pot = getattr(x, self.pot_func)
        print(self._pot)
        os.chdir(cur_dir)

    def getpot(self,cds):
        """Uses the potential function we got to call potential"""
        if self._potPool is not None:
            cds = np.array_split(self.pool)
            res = self._potPool.map(self._pot,cds)
            v = np.concatenate((res))
        else:
            v = self._pot(cds)
        return v

if __name__ == "__main__":
    pth = "/mnt/c/Users/rjdir/Dropbox/Grad School/pyvibdmc/pyvibdmc/potentials/FortPots/Bowman_H5O2"
    pot = Potential(potential_function="callPot",
                    python_file="testPot.py",
                    potential_directory=pth,
                    pool=0)
    cds = np.random.random((1000,7,3))
    vv = pot.getpot(cds)
    print(type(vv))
    print(vv)