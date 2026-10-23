"""
Run a task's gen_data.py with its fixed seeds shifted by an episode offset, so every episode
gets a fresh instance of the same task. Offset 0 reproduces the original data exactly.

    python3 -c "$SEEDED_RUNNER" GEN_DATA.py OFFSET
"""

RUNNER = r'''
import runpy, sys
gen, off = sys.argv[1], int(sys.argv[2])
if off:
    import random
    K = 7919 * off
    def shift(a):
        if a is None:
            return None
        if isinstance(a, bool):
            return a
        if isinstance(a, int):
            return (a + K) % (2 ** 32)
        return f"{a}|{off}"
    _seed = random.Random.seed
    def seed(self, a=None, *args, **kw):
        return _seed(self, shift(a), *args, **kw)
    random.Random.seed = seed
    random.seed = random._inst.seed
    try:
        import numpy as np
        _np_seed = np.random.seed
        np.random.seed = lambda s=None: _np_seed(shift(s) if isinstance(s, int) else s)
        _rng = np.random.default_rng
        np.random.default_rng = lambda s=None, *a, **k: _rng(shift(s) if isinstance(s, int) else s, *a, **k)
        _RS = np.random.RandomState
        class RandomState(_RS):
            def __init__(self, seed=None):
                super().__init__(shift(seed) if isinstance(seed, int) else seed)
        np.random.RandomState = RandomState
    except ImportError:
        pass
sys.argv = [gen]
runpy.run_path(gen, run_name="__main__")
'''
