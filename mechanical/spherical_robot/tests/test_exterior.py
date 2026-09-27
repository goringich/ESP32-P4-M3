import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('exterior',ROOT/'exterior/build.py')
exterior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exterior)


class ExteriorContractTests(unittest.TestCase):
  def test_lid_uses_canonical_sphere_and_rejects_edge_breakout(self):
    cfg, e = exterior.parameters()
    self.assertIn(f'r={cfg["sphere_outer_diameter_mm"]/2}',exterior.source())
    e['screw_centres_yz_mm'] = [[e['hatch_size_mm'][0]/2,0]]
    import json
    with patch.object(Path,'read_text',return_value=json.dumps(cfg)):
      with self.assertRaisesRegex(ValueError,'edge|ligament'):
        exterior.parameters()

  def test_rejects_counterbore_breakthrough(self):
    cfg, e = exterior.parameters()
    e['screw_head_depth_mm'] = e['hatch_wall_mm']
    import json
    with patch.object(Path,'read_text',return_value=json.dumps(cfg)):
      with self.assertRaisesRegex(ValueError,'breaks through'):
        exterior.parameters()

  def test_reserves_remain_provisional_and_camera_is_parked_only(self):
    _, e = exterior.parameters()
    self.assertEqual(e['status'],'ASSUMED')
    self.assertEqual(e['camera_mode'],'PARKED_ONLY')

  def test_rejects_screw_breaking_into_service_aperture(self):
    cfg, e = exterior.parameters()
    e['screw_centres_yz_mm'] = [[41,24]]
    import json
    with patch.object(Path,'read_text',return_value=json.dumps(cfg)):
      with self.assertRaisesRegex(ValueError,'ligament'):
        exterior.parameters()
