"""Check actual exported triangles and generate an auditable geometry receipt."""
import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports/exterior'


def verify():
  config = json.loads((ROOT/'config/dimensions.json').read_text())
  radius = config['sphere_outer_diameter_mm']/2
  receipt = json.loads((OUT/'manifest.json').read_text())
  expected = hashlib.sha256((ROOT/'config/dimensions.json').read_bytes()).hexdigest()
  if receipt['parameter_sha256'] != expected:
    raise ValueError('Stale geometry: regenerate from current parameters')
  source_hash = hashlib.sha256((ROOT/'exterior/build.py').read_bytes()).hexdigest()
  if receipt['source_sha256'] != source_hash:
    raise ValueError('Stale geometry: generator changed')
  for row in receipt['parts']:
    path = OUT/(row['part']+'.stl')
    if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
      raise ValueError('Mesh hash mismatch')
    mesh = trimesh.load_mesh(path)
    # STL vertex welding is format decoding, not topology repair.
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0:
      raise ValueError(f'Invalid solid: {row["part"]}')
    if len(mesh.split()) != 1:
      raise ValueError(f'Detached fragment: {row["part"]}')
    if np.linalg.norm(mesh.vertices, axis=1).max() > radius + 0.001:
      raise ValueError('Part protrudes outside the rolling sphere')
    row['watertight'] = True
    row['connected_solids'] = 1
    row['triangles'] = len(mesh.faces)
    row['volume_mm3'] = round(mesh.volume,3)
    row['assembly_bounds_mm'] = mesh.bounds.round(3).tolist()
    if row['part'] != 'SERVICE_HATCH_SEAT':
      mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi/2,[0,1,0]))
      mesh.apply_translation([-mesh.centroid[0],-mesh.centroid[1],-mesh.bounds[0,2]])
      bed = config['exterior']['target_bed_mm']
      if any(mesh.extents[i] + (10 if i < 2 else 0) > bed[i] for i in range(3)):
        raise ValueError('Part with brim exceeds A1 build volume')
      target = OUT/(row['part']+'_PRINT.stl')
      mesh.export(target)
      row['print_file'] = target.name
      row['print_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
      row['print_bounds_mm'] = mesh.bounds.round(3).tolist()
      row['support_decision'] = 'REQUIRED: concave underside; slicer inspection pending'
  receipt['mesh_status'] = 'PASS'
  receipt['status'] = 'MESH_VERIFIED_ASSEMBLY_BLOCKED'
  (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
  return receipt


if __name__ == '__main__':
  print(json.dumps(verify(),indent=2))
