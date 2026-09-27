"""Generate the shared curved hatch geometry; millimetres, +X outward.

OpenSCAD performs exact boolean operations. Blender imports these same meshes;
there is no independent dimensional authority. Neither export nor mesh closure
proves printability, load capacity, hardware fit or collision-free assembly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def parameters():
  cfg = json.loads((ROOT / 'config/dimensions.json').read_text())
  e = cfg['exterior']
  r = cfg['sphere_outer_diameter_mm'] / 2
  w, h = e['hatch_size_mm']
  if not (0 < e['hatch_gap_mm'] < e['seat_lip_mm'] < min(w, h) / 4):
    raise ValueError('Invalid hatch fit or lip')
  if e['hatch_wall_mm'] <= e['screw_head_depth_mm']:
    raise ValueError('Counterbore breaks through hatch')
  if math.hypot(w / 2 + e['seat_border_mm'], h / 2 + e['seat_border_mm']) >= r - e['seat_depth_mm'] - e['hatch_wall_mm']:
    raise ValueError('Hatch exceeds spherical domain')
  for y, z in e['screw_centres_yz_mm']:
    dy = max(0, abs(y) - (w / 2 - e['seat_lip_mm']))
    dz = max(0, abs(z) - (h / 2 - e['seat_lip_mm']))
    ligament = math.hypot(dy, dz) - cfg['m3_clearance_mm'] / 2
    if ligament < cfg['minimum_local_wall_mm']:
      raise ValueError('Screw breaks aperture ligament')
    if abs(y) + cfg['m3_counterbore_diameter_mm'] / 2 >= w / 2 or abs(z) + cfg['m3_counterbore_diameter_mm'] / 2 >= h / 2:
      raise ValueError('Counterbore breaks hatch edge')
  return cfg, e


def source():
  cfg, e = parameters()
  r = cfg['sphere_outer_diameter_mm'] / 2
  w, h = e['hatch_size_mm']
  if [w - 2 * e['seat_lip_mm'], h - 2 * e['seat_lip_mm']] != cfg['service_hatch_opening_mm']:
    raise ValueError('Service aperture differs from canonical dimensions')
  # A spherical patch rather than a tangent plate; recessed heads stay inside R.
  return f'''// Generated from config/dimensions.json. Do not edit.
$fn=160;
r={r}; w={w}; h={h}; wall={e['hatch_wall_mm']}; shell_wall={cfg['shell_wall_mm']};
gap={e['hatch_gap_mm']}; lip={e['seat_lip_mm']};
seat_gap={e['seat_gap_mm']}; border={e['seat_border_mm']};
screws={json.dumps(e['screw_centres_yz_mm'])};
module slab(y,z) {{ translate([r/2,0,0]) cube([r,y,z],center=true); }}
module patch(ro,ri,y,z) {{
  intersection() {{ difference() {{ sphere(ro); sphere(ri); }} slab(y,z); }}
}}
module bore(d,y,z) {{ translate([r-35,y,z]) rotate([0,90,0]) cylinder(h=45,d=d); }}
module screws_cut(heads=false) {{
  for(p=screws) {{
    bore({cfg['m3_clearance_mm']},p[0],p[1]);
    if(heads) translate([sqrt(r*r-pow(sqrt(p[0]*p[0]+p[1]*p[1])+{cfg['m3_counterbore_diameter_mm']}/2,2))-{e['screw_head_depth_mm']},p[0],p[1]])
      rotate([0,90,0]) union() {{
        cylinder(h={e['screw_head_depth_mm']}-0.3,d1={cfg['m3_clearance_mm']},d2={cfg['m3_counterbore_diameter_mm']});
        translate([0,0,{e['screw_head_depth_mm']}-0.3]) cylinder(h=10,d={cfg['m3_counterbore_diameter_mm']});
      }}
  }}
}}
module hatch(av=false) {{
  difference() {{
    patch(r,r-wall,w,h);
    screws_cut(true);
    if(av) {{
      bore({e['camera_aperture_diameter_mm']},0,0);
      translate([r-{e['camera_window_recess_mm']},0,0]) rotate([0,90,0])
        cylinder(h=10,d={e['camera_window_diameter_mm']}+2*gap);
      for(z=[-2.5,0,2.5]) bore({e['microphone_port_diameter_mm']},{e['microphone_centre_yz_mm'][0]},z);
    }}
  }}
}}
module seat() {{
  difference() {{
    patch(r-shell_wall+0.4,r-wall-{e['seat_depth_mm']},w+2*border,h+2*border);
    slab(w-2*lip,h-2*lip);
    intersection() {{
      difference() {{ sphere(r+1); sphere(r-wall-seat_gap); }}
      slab(w+2*gap,h+2*gap);
    }}
    screws_cut(false);
  }}
}}
// Blank is the rolling configuration; AV is an alternative stationary-view lid.
if(part=="SERVICE_HATCH") hatch(false);
if(part=="SERVICE_HATCH_AV") hatch(true);
if(part=="SERVICE_HATCH_SEAT") seat();
'''


def build(output: Path):
  executable = shutil.which('openscad')
  if not executable:
    raise RuntimeError('OpenSCAD required; existing exports must not be reused')
  output.mkdir(parents=True, exist_ok=True)
  scad = output / 'service_hatch.scad'
  scad.write_text(source())
  rows = []
  for part in ('SERVICE_HATCH', 'SERVICE_HATCH_AV', 'SERVICE_HATCH_SEAT'):
    path = output / f'{part}.stl'
    subprocess.run([executable, '--export-format', 'binstl', '-o', str(path), '-D', f'part="{part}"', str(scad)], check=True)
    if not path.exists() or path.stat().st_size < 100:
      raise RuntimeError(f'Empty geometry: {part}')
    rows.append({'part':part, 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
  report = {
    'revision': parameters()[1]['revision'],
    'parameter_sha256':hashlib.sha256((ROOT/'config/dimensions.json').read_bytes()).hexdigest(),
    'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'coordinate_frame':'assembly millimetres, +X outward; NOT bed oriented',
    'parts':rows, 'physical_accepted':False, 'slicer_status':'NOT_RUN',
    'assembly_collision_status':'NOT_RUN', 'status':'GEOMETRY_CANDIDATE'
  }
  (output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
  return report


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--output',type=Path,default=ROOT/'exports/exterior')
  args = parser.parse_args()
  print(json.dumps(build(args.output),indent=2))
