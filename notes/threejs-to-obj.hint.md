1. Grep `/root/data/object.js` for the exported scene-builder function and InstancedMesh usage, and check that `three` and `OBJExporter.js` are installed.
2. Write `/root/export.mjs`: import the module, build the root, `updateMatrixWorld(true)`, clone each mesh's geometry and apply `matrixWorld` (matrixWorld×instanceMatrix for InstancedMesh), then `makeRotationX(-Math.PI/2)` once.
3. Merge the geometries and write `OBJExporter().parse(mesh)` to `/root/output/object.obj`.
4. Verify the v/f counts and a numpy bbox: x unchanged, z = old y, y = −old z, no NaN.
