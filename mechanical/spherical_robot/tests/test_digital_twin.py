from __future__ import annotations

import importlib.util
import json
import math
import re
from pathlib import Path
import sys
import tempfile
import unittest
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "simulation"
FEA_ROOT = ROOT / "fea"
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))
if str(SIM) not in sys.path:
  sys.path.insert(0, str(SIM))

import calculations
import reduced_order
import mujoco_model

fea_spec = importlib.util.spec_from_file_location(
  "run_structural_fea",
  FEA_ROOT / "run_structural_fea.py",
)
run_structural_fea = importlib.util.module_from_spec(fea_spec)
assert fea_spec.loader is not None
fea_spec.loader.exec_module(run_structural_fea)


class ParameterContractTests(unittest.TestCase):
  def test_sizing_report_uses_current_dimension_keys(self) -> None:
    cfg = calculations.load_config()
    report = calculations.sizing_report(cfg)
    self.assertEqual(report["project_revision"], cfg["project_revision"])
    self.assertGreater(report["mass"]["total_mass_g_estimate"], 1000.0)
    self.assertGreater(report["pendulum"]["minimum_continuous_drive_torque_nm"], 0.0)
    self.assertIn("tt_motor_performance", report["unresolved_input_status_keys"])
    self.assertFalse(report["physical_accepted"])

  def test_placeholder_status_is_not_erased(self) -> None:
    cfg = calculations.load_config()
    statuses = set(cfg["dimension_status"].values())
    self.assertIn("PLACEHOLDER", statuses)
    self.assertIn("ASSUMED", statuses)


class ReducedOrderDynamicsTests(unittest.TestCase):
  def conservative_params(self) -> reduced_order.Parameters:
    params = reduced_order.build_parameters()
    return reduced_order.Parameters(
      radius_m=params.radius_m,
      body_mass_kg=params.body_mass_kg,
      body_inertia_kg_m2=params.body_inertia_kg_m2,
      pendulum_mass_kg=params.pendulum_mass_kg,
      pendulum_length_m=params.pendulum_length_m,
      gravity_m_s2=params.gravity_m_s2,
      static_friction_mu=10.0,
      rolling_drag_ns_per_m=0.0,
      pendulum_damping_nms=0.0,
      motor_torque_nm=params.motor_torque_nm,
      motor_no_load_rad_s=params.motor_no_load_rad_s,
    )

  def test_zero_state_with_zero_torque_is_equilibrium(self) -> None:
    params = self.conservative_params()
    derivative, diag = reduced_order.derivatives(
      reduced_order.State(),
      params,
      0.0,
    )
    for value in derivative.__dict__.values():
      self.assertAlmostEqual(value, 0.0, places=12)
    self.assertGreater(diag.determinant, 0.0)
    self.assertGreater(diag.friction_margin_n, 0.0)

  def test_motor_torque_is_equal_and_opposite_reaction(self) -> None:
    params = self.conservative_params()
    positive, _ = reduced_order.derivatives(
      reduced_order.State(),
      params,
      0.05,
    )
    negative, _ = reduced_order.derivatives(
      reduced_order.State(),
      params,
      -0.05,
    )
    self.assertAlmostEqual(positive.v_m_s, -negative.v_m_s, places=10)
    self.assertAlmostEqual(positive.omega_rad_s, -negative.omega_rad_s, places=10)

  def test_conservative_energy_stays_bounded(self) -> None:
    params = self.conservative_params()
    state = reduced_order.State(theta_rad=0.12)
    initial = reduced_order.total_energy_j(state, params)
    zero = lambda _t, _state, _params: 0.0
    for index in range(3000):
      state, _ = reduced_order.rk4_step(index * 0.0005, state, 0.0005, params, zero)
    final = reduced_order.total_energy_j(state, params)
    scale = max(1e-9, abs(initial))
    self.assertLess(abs(final - initial) / scale, 2e-4)

  def test_default_closed_loop_run_is_finite_and_reports_slip_margin(self) -> None:
    params = reduced_order.build_parameters()
    cfg = reduced_order.load_simulation_config()
    result = reduced_order.simulate(
      params=params,
      controller=reduced_order.speed_controller(0.1, cfg),
      duration_s=0.5,
      dt_s=0.002,
    )
    values = list(result["final_state"].values()) + list(result["metrics"].values())
    self.assertTrue(all(math.isfinite(float(value)) for value in values))
    self.assertIn("minimum_friction_margin_n", result["metrics"])
    self.assertIsInstance(result["slip_risk"], bool)


class MuJoCoInputTests(unittest.TestCase):
  def test_generated_model_is_well_formed_and_bound_to_sources(self) -> None:
    xml = mujoco_model.build_xml()
    root = ElementTree.fromstring(xml)
    self.assertEqual(root.tag, "mujoco")
    self.assertIn("pendulum_motor", xml)
    self.assertIn("steering_yaw", xml)
    self.assertIn("dimensions_sha256", xml)
    self.assertIn("GENERATED_MODEL_NOT_EXECUTED", xml)

  def test_mujoco_internal_pendulum_geoms_do_not_collide_with_solid_shell_proxy(self) -> None:
    root = ElementTree.fromstring(mujoco_model.build_xml())
    by_name = {
      geom.attrib.get("name"): geom
      for geom in root.findall(".//geom")
      if geom.attrib.get("name")
    }
    for name in ("pendulum_arm", "ballast"):
      self.assertEqual(by_name[name].attrib.get("contype"), "0")
      self.assertEqual(by_name[name].attrib.get("conaffinity"), "0")
    self.assertNotEqual(by_name["shell_contact"].attrib.get("contype"), "0")

  def test_generated_model_accepts_scenario_overrides(self) -> None:
    xml = mujoco_model.build_xml(
      ballast_mass_g=400.0,
      arm_mm=68.0,
      friction_mu=0.65,
    )
    self.assertIn('scenario_ballast_g" data="400.000000"', xml)
    self.assertIn('scenario_arm_mm" data="68.000000"', xml)
    self.assertIn('scenario_friction_mu" data="0.650000"', xml)


class CadConfigContractTests(unittest.TestCase):
  def test_blender_cfg_references_exist_in_canonical_dimensions(self) -> None:
    cfg = calculations.load_config()
    for relative in (
      Path("blender/build_robot.py"),
      Path("blender/validate_robot.py"),
      Path("blender/export_parts.py"),
    ):
      source = (ROOT / relative).read_text(encoding="utf-8")
      referenced = set(re.findall(r'CFG\\[["\\\']([^"\\\']+)["\\\']\\]', source))
      missing = sorted(referenced - set(cfg))
      self.assertEqual(missing, [], f"{relative}: stale CFG keys: {missing}")

  def test_legacy_collision_sweep_is_removed(self) -> None:
    source = (ROOT / "blender/build_robot.py").read_text(encoding="utf-8")
    self.assertNotIn("def collision_sweep(inner_r:", source)
    self.assertIn("def collision_sweep_v2(inner_r:", source)


class StructuralFeaContractTests(unittest.TestCase):
  def test_fea_material_truth_is_explicitly_assumed(self) -> None:
    cfg = json.loads((FEA_ROOT / "config.json").read_text(encoding="utf-8"))
    self.assertEqual(cfg["material"]["status"], "ASSUMED")
    self.assertFalse(cfg["evidence_policy"]["physical_accepted"])
    self.assertFalse(cfg["evidence_policy"]["may_promote_to_structural_analysis_pass"])
    self.assertEqual(
      cfg["evidence_policy"]["pass_state"],
      "STRUCTURAL_FEA_SCREENING_PASS",
    )

  def test_five_g_per_arm_load_is_positive_and_uses_worst_ballast(self) -> None:
    dimensions = calculations.load_config()
    simulation = reduced_order.load_simulation_config()
    cfg = json.loads((FEA_ROOT / "config.json").read_text(encoding="utf-8"))
    load_n = run_structural_fea.load_case_force_n(
      dimensions,
      simulation,
      cfg,
    )
    expected = (
      max(float(value) for value in dimensions["ballast_variants_g"])
      + float(simulation["pendulum_extra_mass_g_assumed"])
    ) / 1000.0 * 9.80665 * 5.0 * 0.5
    self.assertAlmostEqual(load_n, expected, places=9)
    self.assertGreater(load_n, 0.0)

  def test_calculix_dat_parser_extracts_displacement_and_mises(self) -> None:
    fixture = """
 displacements (vx,vy,vz) for set NALL and time  0.1000000E+01

         1  0.000000E+00  3.000000E-01  4.000000E-01
         2  0.000000E+00  0.000000E+00  0.000000E+00

 stresses (elem, integ.pnt.,sxx,syy,szz,sxy,sxz,syz) for set EALL and time  0.1000000E+01

         1  1  1.000000E+01  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00  0.000000E+00
"""
    result = run_structural_fea.parse_calculix_dat(fixture)
    self.assertAlmostEqual(result["maximum_displacement_mm"], 0.5, places=9)
    self.assertAlmostEqual(result["maximum_von_mises_mpa"], 10.0, places=9)
    self.assertEqual(result["displacement_rows"], 2)
    self.assertEqual(result["stress_rows"], 1)


if __name__ == "__main__":
  unittest.main()
