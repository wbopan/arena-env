1. Inspect `/root/data/object.js` with head/grep (imports/exports, Group names, InstancedMesh) and locate the `three` npm package.
2. Write one `.mjs` script: import the file, call `createScene()`, then `updateMatrixWorld(true)`. Named Groups are parts; assign each Mesh to its nearest named Group ancestor.
3. Bake `matrixWorld` into cloned geometry (toNonIndexed, normals). Export each mesh with OBJExporter to `/root/output/part_meshes/<part>/<mesh>.obj`.
4. Merge each part's meshes with mergeGeometries and write `/root/output/links/<part>.obj`.
5. Verify with find/ls/wc that the part dirs and link files match and every OBJ has vertices.
