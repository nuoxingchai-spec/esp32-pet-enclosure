---
name: esp32-pet-enclosure
description: Design, modify, validate and export a 3D-printable ESP32 desktop-pet enclosure in Blender through BlenderMCP. Use for enclosure shells, display windows, USB/vent/speaker openings, screw bosses, lids, tolerances, manifold checks, STL export, or when the user asks to model/print an ESP32 project case.
---

# ESP32 desk-pet enclosure

Use this skill for any 3D-printed enclosure work for an ESP32-based desktop pet or similar embedded device.

## Before modeling

1. Read `design/enclosure-spec.md` for the print tolerances, ESP32 antenna/thermal rules, and the current hardware placeholders.
2. Confirm real dimensions with the user before promising a printable fit:
   - board L×W×H including headers, USB position, antenna end;
   - display outline/active area/thickness and flex direction;
   - battery/charging board, speaker/mic, buttons/servos;
   - printer nozzle/material and target overall size.
3. Check the BlenderMCP connection with `get_addon_status`. If Blender is not connected, ask the user to run `blender/start_blender_mcp.cmd` or enable the addon and click **Connect to Claude** in the N-panel. The addon refuses to start in `blender -b` background mode.

## Modeling rules

- Work in **1 Blender unit = 1 mm**; set metric display scale 0.001. Export STL with `use_scene_unit=False`, `global_scale=1.0`.
- Keep walls/floor 1.8–2.4 mm; running fits 0.25–0.4 mm; loose fits 0.4–0.6 mm.
- M2.5 self-tapping: pilot Ø2.2, boss OD Ø5.0, lid clearance Ø2.8, counterbore Ø5.0×1.6. Keep 8–10 mm engagement and put bosses outside the board footprint.
- Keep 5–10 mm antenna keep-out from metal/battery/copper; ventilate the enclosure; do not seal a LiPo battery in a hot zone.
- Apply all modifiers; check 0 non-manifold and 0 boundary edges before export.
- Export base and lid separately; parse the binary STL bounding box to verify millimetres. Do not trust only `obj.dimensions`.

## Existing generator

`blender/esp32_pet_enclosure.py` builds a rounded two-part shell with display window/chamfer, USB opening, rear vents, side speaker holes, four bosses and a lipped lid. Run it through `execute_blender_code`:

```python
import os
os.chdir(r"C:\Users\admin\Documents\Qoder\2026-11-10\faf708e5")
exec(open(r"blender\esp32_pet_enclosure.py", encoding="utf-8").read(), globals())
```

Override the `P` dictionary or call `build({...})` for measured hardware. It writes `exports/enclosure_base.stl` and `exports/enclosure_lid.stl`. It preserves unrelated scene objects and only clears its own collection.

## Verification

1. `get_scene_info` with `fields=["size","topology","settings"]` on both objects: dimensions, non-manifold/boundary counts.
2. Export and parse the STL bounding box; compare with expected mm.
3. `look` with views front/three_quarter/top/left to inspect openings and the lid seam.
4. State clearly which items remain unmodeled (board retention, display mount, battery, servos, styling) instead of claiming a finished printable case.

## Current baseline

Outer 70.4×43.9×49.3 mm; cavity 66.4×39.9 mm; display window Ø32 mm; USB 9.4×3.6 mm; M2.5 bosses at ±(30.2, 16.95) mm. This is a parametric starting shell, not a final fit for unknown hardware.
