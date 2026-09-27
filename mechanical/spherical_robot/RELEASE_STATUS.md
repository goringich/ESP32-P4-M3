# P0.3 exterior candidate — NOT a print or robot release

Primary class: ENGINEERING_CAD. Source is stacked on hardening PR #11.
Scope: shared parametric curved service hatch, integral ledge, recessed fasteners,
optional parked-camera window/microphone apertures, verified isolated STL meshes,
A1 process notes and Russian integration guide. Parameters remain in the existing
`config/dimensions.json`; no second project/parameter authority is introduced.

| Evidence | Status |
|---|---|
| Repository contract and Python unit tests | Run; see PR receipt |
| OpenSCAD generation of 3 isolated solids | Run; SHA-256 in exports/exterior/manifest.json |
| Actual STL closure, winding, connected solid, volume and spherical envelope | exports/exterior/verification.json |
| Two lids oriented to Z=0, A1 bed envelope including 5 mm brim | verification.json; envelope check, not slicing |
| Orthographic STL inspection | geometry-review.png; not whole-robot assembly validation |
| Blender whole-assembly regeneration and collision sweep | BLOCKED: Blender unavailable in current environment |
| Structural analysis of ledge/fasteners, supports and insert/fastener coupon | PENDING |
| Bambu Studio A1 slice, removable supports, exact print time/material | BLOCKED: compatible slicer not available |
| Measured component fit, thermal, HIL, rolling and repeated validation | PENDING; no physical tests performed |
| Camera/microphone mounts and relocation of switch/charge holders | PENDING; reserved envelopes only |

`physical_accepted=false`. All old assembly STL/GLB/BLEND, renders and collision
reports predate this candidate. Do not claim their PASS covers this change.
Do not print the old +X panel and expect the new lid to fit it.

## Exact continuation

1. Review PR #11 and this dependent PR without merging around its gates.
2. In an environment with OpenSCAD and compatible Blender, rebuild from this
   branch. Resolve any manifold, assembly/fastener or collision failures.
3. Test ledge/fastener structure and access; generate assembly/service views.
4. Slice the regenerated panel plus blank lid using the native A1 profile;
   inspect underside supports and their removal from mating faces. Print coupons.
5. Measure the actual purchased parts (#13); select/characterize actuator (#12).
6. Select exact camera and mic; redesign their carriers and switch/charge routing
   inside the reserved region, then repeat collision and service checks.
7. Bind product controller (#14), then HIL and physical staged trials.

A GitHub merge alone must not convert this candidate into PRINT_READY.
