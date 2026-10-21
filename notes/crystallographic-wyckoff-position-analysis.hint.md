1. Run `ls /root/cif_files`, `head -30` one CIF, and check the pymatgen/spglib versions.
2. In `/root/workspace/solution.py`, load with `Structure.from_file` (keeps the full cell), then use `SpacegroupAnalyzer(s).get_symmetry_dataset()` and its `.wyckoffs` (or `["wyckoffs"]`), not `wyckoff_symbols`.
3. Multiplicity is `int` of `Counter(wyckoffs)`. Coordinates are the frac_coords of the first site with each letter, written as `str(Fraction(x).limit_denominator(12))`.
4. Return `{"wyckoff_multiplicity_dict":..., "wyckoff_coordinates_dict":...}`; retry with `symprec=0.1` on failure.
5. Run it on every file and verify FeS2_mp-226 gives a:4 ["0","1/2","1/2"] and c:8 ["3/8","1/9","8/9"].
