**Goal.** Load `/root/data/object.js` in Node, call `createScene()` and bake world transforms. Then write:
- one OBJ per mesh to `/root/output/part_meshes/<part_name>/<mesh_name>.obj`
- one merged OBJ per part to `/root/output/links/<part_name>.obj`

**Inspect cheaply first (no full cat):**
- `wc -l /root/data/object.js; head -40 /root/data/object.js`
- `grep -n "export\|import\|function createScene\|return" /root/data/object.js | head`, to see whether it is an ES module and what it returns.
- `grep -c "new THREE.Group" ...` and `grep -n "\.name *=" ... | head -50`, to see how parts and meshes are named.
- `grep -n "InstancedMesh" ...`, to check for instancing.
- `which node; ls /usr/lib/node_modules /root/node_modules 2>/dev/null | head; npm ls -g three 2>/dev/null`, to find the `three` package.
- `ls ~/.claude/skills/threejs/scripts 2>/dev/null` or `find / -name export_link_objs.mjs 2>/dev/null | head -1`. A ready-made per-link exporter may exist; `node scripts/export_link_objs.mjs --input <scene_js> --out-dir <dir>` handles links only. Writing one full script is usually simpler.

**Node setup.**
- Use ES modules: name the script `.mjs`, or put `{"type":"module"}` in package.json.
- If `three` is not resolvable from the script's location, either:
  - run `npm i three` in the working directory, or
  - set `NODE_PATH` (this only works for CJS), or
  - import by absolute path: `import * as THREE from '/usr/lib/node_modules/three/build/three.module.js'`.
- Imports:
  - `import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js'`
  - `import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js'`
- If object.js has `import * as THREE from 'three'` plus `export function createScene`, `await import('/root/data/object.js')` works, provided `three` resolves from /root/data.
  - Otherwise copy it next to your script.
  - Or read the text, strip the import/export lines, and eval with `new Function('THREE', src + '; return createScene;')(THREE)`.

**Partition rules (from skills).**
- Every **named `THREE.Group`** (`obj.isGroup && obj.name`) at any depth is a part/link.
- Each Mesh belongs to its **nearest named Group ancestor**.
- Nested named groups are separate parts; never merge child-part meshes into the parent.
- Skip parts with zero meshes. Sort part names for determinism.
- If the root is just an unnamed container, skip it. If the root is a named Group that directly owns meshes, it counts as a part.

**Baking.**
- Call `root.updateMatrixWorld(true)` first.
- For each mesh:
  1. `g = mesh.geometry.clone(); g.applyMatrix4(mesh.matrixWorld);`
  2. `if (g.index) g = g.toNonIndexed();`
  3. `if (!g.attributes.normal) g.computeVertexNormals();`
- InstancedMesh: for each i < `count`, `obj.getMatrixAt(i, m)`, then use `M = obj.matrixWorld.clone().multiply(m)`. Each instance is a separate mesh named e.g. `<name>_<i>`.

**Merging geometries.**
- Attribute sets must match for `mergeGeometries`. Keep only `position` and `normal`: delete `uv`, `uv1`/`uv2`, and `color` if they are inconsistent across meshes.
- All geometries must be non-indexed.
- Returns null on mismatch, so check for that.

**Mesh names.**
- Use `mesh.name`. If empty, fall back to `${part}_mesh_${k}`.
- Sanitize to `[A-Za-z0-9_.-]`.
- Deduplicate within a part: if the name already exists, append `_1`, `_2`, and so on.

**Script skeleton (`/root/export.mjs`):**
```js
import fs from 'fs'; import path from 'path';
import * as THREE from 'three';
import { OBJExporter } from 'three/examples/jsm/exporters/OBJExporter.js';
import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
const mod = await import('/root/data/object.js');
const root = await (mod.createScene ?? mod.default)();
root.updateMatrixWorld(true);
const parts = new Map();
root.traverse(o => { if (o.isGroup && o.name) parts.set(o.name, []); });
const owner = o => { let p=o.parent; while(p && !(p.isGroup&&p.name)) p=p.parent; return p; };
const bake = (geo, M) => { let g=geo.clone(); g.applyMatrix4(M); if(g.index) g=g.toNonIndexed();
  for (const k of Object.keys(g.attributes)) if(k!=='position'&&k!=='normal') g.deleteAttribute(k);
  if(!g.attributes.normal) g.computeVertexNormals(); return g; };
root.traverse(o => { if(!o.isMesh) return; const p=owner(o); if(!p) return;
  if (o.isInstancedMesh) { const m=new THREE.Matrix4();
    for(let i=0;i<o.count;i++){ o.getMatrixAt(i,m); parts.get(p.name).push([`${o.name||'inst'}_${i}`, bake(o.geometry, o.matrixWorld.clone().multiply(m))]); }
  } else parts.get(p.name).push([o.name, bake(o.geometry, o.matrixWorld)]); });
const ex = new OBJExporter(); const R='/root/output';
fs.mkdirSync(`${R}/links`,{recursive:true});
for (const name of [...parts.keys()].sort()) { const list=parts.get(name); if(!list.length) continue;
  const dir=`${R}/part_meshes/${name}`; fs.mkdirSync(dir,{recursive:true}); const used=new Set();
  list.forEach(([n,g],k)=>{ let b=(n||`${name}_mesh_${k}`).replace(/[^\w.-]/g,'_'), u=b, j=1;
    while(used.has(u)) u=`${b}_${j++}`; used.add(u);
    const mm=new THREE.Mesh(g); mm.name=u; fs.writeFileSync(`${dir}/${u}.obj`, ex.parse(mm)); });
  const merged=mergeGeometries(list.map(x=>x[1]), false);
  const lm=new THREE.Mesh(merged); lm.name=name; fs.writeFileSync(`${R}/links/${name}.obj`, ex.parse(lm)); }
console.log([...parts].map(([k,v])=>k+':'+v.length).join('\n'));
```

**Pitfalls.**
- Forgetting `updateMatrixWorld(true)` gives local coordinates, which is wrong.
- Do not apply a Y-up to Z-up axis conversion; the task doesn't request it.
- If `createScene` returns a Scene, its named groups are still found via traverse.
- Do not print OBJ contents, only counts.

**Verification.**
- `find /root/output -name '*.obj' | wc -l`
- `ls /root/output/links`
- `ls /root/output/part_meshes | head`
- `head -3 /root/output/links/<some>.obj`
- `grep -c '^v ' ...`, to confirm vertices are present.
- Check that the number of link files equals the number of part dirs, and that each part dir has at least one obj.
- Cross-check the mesh count per part against grep of `.add(` in the source if unsure.
