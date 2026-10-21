**Goal:** write one Node.js script that loads `/root/data/object.js`, builds the scene, and bakes every mesh's world transform into its geometry. InstancedMesh must be expanded per instance. Then apply a -90° X rotation (Y-up → Blender Z-up) and write a single OBJ to `/root/output/object.obj`. All original 3D positions must be preserved: nothing may be dropped, recentred or rescaled.

**Inspect cheaply first (do not cat the whole file):**
- `wc -l /root/data/object.js; head -40 /root/data/object.js`
- `grep -n "export\|function\|import\|InstancedMesh\|new THREE\.\(Group\|Mesh\)" /root/data/object.js | head -50`
- Find which function builds the scene (usually `export function createScene()`), what it returns (a root `Object3D`/`Group`/`Scene`), and how it imports three (`import * as THREE from 'three'`).
- Locate three: `ls /root/node_modules/three 2>/dev/null || npm ls -g three; node -v`.
- If three is not installed, try `cd /root && npm i three` (if network is allowed).
- Check whether `three/examples/jsm/exporters/OBJExporter.js` exists. Newer releases also expose it as `three/addons/exporters/OBJExporter.js`.

**ES module setup:**
- Put the script as `/root/export.mjs`; the `.mjs` extension forces ESM.
- Or add `{"type":"module"}` to `package.json` next to it.
- If `object.js` is ESM but has no package.json "type", import it with a dynamic `import('/root/data/object.js')`. If Node complains, copy it to `/root/object_copy.mjs` and import that.
- `node_modules` must be resolvable from the script/data location. Run from `/root`, or symlink `/root/data/node_modules` → `/root/node_modules` if the data file imports 'three'.
- If the file uses CommonJS (`module.exports`), use `createRequire`.

**Script sketch:**
```js
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import fs from 'fs';
const mod = await import('/root/data/object.js');
const root = mod.createScene ? mod.createScene() : (mod.default?.() ?? mod.default);
root.updateMatrixWorld(true);
const axis = new THREE.Matrix4().makeRotationX(-Math.PI/2);
const geoms = [];
const bake = (g, m) => {
  let geom = g.clone();
  geom.applyMatrix4(m);
  geom.applyMatrix4(axis);
  if (geom.index) geom = geom.toNonIndexed();
  for (const k of Object.keys(geom.attributes))
    if (!['position','normal','uv'].includes(k)) geom.deleteAttribute(k);
  if (!geom.attributes.normal) geom.computeVertexNormals();
  geoms.push(geom);
};
root.traverse(o => {
  if (o.isInstancedMesh) {
    const im = new THREE.Matrix4(), t = new THREE.Matrix4();
    for (let i = 0; i < o.count; i++) {
      o.getMatrixAt(i, im);
      t.copy(o.matrixWorld).multiply(im);
      bake(o.geometry, t);
    }
  } else if (o.isMesh) bake(o.geometry, o.matrixWorld);
});
// attribute sets must match for merge: drop uv if any geom lacks it
if (geoms.some(g => !g.attributes.uv)) geoms.forEach(g => g.deleteAttribute('uv'));
const merged = mergeGeometries(geoms, false);
fs.mkdirSync('/root/output', { recursive: true });
fs.writeFileSync('/root/output/object.obj', new OBJExporter().parse(new THREE.Mesh(merged)));
```

**Notes on the sketch:**
- In older three versions, `mergeGeometries` is named `mergeBufferGeometries`. Check with `grep -n "export function merge" .../BufferGeometryUtils.js`.
- Alternative that avoids merge issues: add each baked mesh to a `new THREE.Group()` and run `exporter.parse(group)`. Only do this with geometry that is already baked and objects that have identity transforms, otherwise OBJExporter applies `matrixWorld` again.
- Merging is not required; the requirement is one OBJ with correct world-space vertices.

**Pitfalls:**
- Call `updateMatrixWorld(true)` on the root before reading `matrixWorld`; otherwise nested transforms are lost.
- Apply the axis rotation exactly once. Either apply it to each geometry, or set `root.rotation.x = -Math.PI/2` before `updateMatrixWorld`, but never both.
- The rotation maps (x, y, z) → (x, -z, y). For example, a point at Y-up height y ends up with z = y.
- Do not call `geometry.center()`, normalise or scale anything.
- InstancedMesh: export `count` instances, not just the base geometry.
- Skip non-mesh objects: lights, cameras, `Line`, `Points`. Include `SkinnedMesh` like a normal mesh.
- If the scene function needs a `THREE.Scene` argument or attaches to a global scene, read its signature.
- `createScene` might reference DOM/renderer/canvas. Stub minimal globals, or only call the geometry-building function.
- Materials don't matter for OBJ geometry.

**Verification (cheap):**
- `head -5 /root/output/object.obj; grep -c '^v ' /root/output/object.obj; grep -c '^f ' /root/output/object.obj`
- Bounding-box check with a Python one-liner:
  `python3 -c "import numpy as n;v=n.array([l.split()[1:4] for l in open('/root/output/object.obj') if l.startswith('v ')],float);print(v.min(0),v.max(0))"`
- Compare against the three.js world bbox. In the script, compute `new THREE.Box3().setFromObject(root)` before rotation and print it. The expected Z-up bbox is: x unchanged, new y range = −(old z range), new z = old y.
- The vertex count should equal the sum of the non-indexed triangle counts × 3 across all meshes and instances.
- The face count should be greater than 0, and there should be no NaN values (`grep -c NaN` should give 0).

**Output requirements:**
- Exactly one file, `/root/output/object.obj`, in Wavefront OBJ text format with `v`/`vn`/`f` lines.
- All world-space positions preserved, then rotated -90° about X into Blender Z-up.
- Keep the JS export script as well (e.g. `/root/export.mjs`).
