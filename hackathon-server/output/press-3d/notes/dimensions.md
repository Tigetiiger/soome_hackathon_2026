# Europress Combi (20 m³): dimensions used in the model

Source drawing: `refs/Europress-Combi-product-brochure_ENG.pdf`, page 2, side and top
dimension drawing of a Combi with a 20 m³ container ("our best-selling Combi device"),
plus the specification table on the same page.

**Source tags**
- **drawing**: the number is printed on the drawing or in the spec table.
- **measured from drawing**: measured by us on the to-scale drawing (page rasterised at 400 dpi).
- **schematic**: not in any published source. We chose it to be plausible. It is not Europress data.

## How the measurements were taken

- Page 2 was rasterised at 400 dpi. The crops we measured are kept as
  `qc/ref_drawing_side_400dpi.png` and `qc/ref_drawing_top_400dpi.png`, both 1920 px wide over
  the same columns of the page, so the side and top views share one x-axis.
- **Scale: 3.927 mm per pixel.** The printed 6520 dimension spans 1660 px (3.928 mm/px) and the
  printed 4090 dimension spans 1042 px (3.925 mm/px). The two agree to 0.1 %.
- We used the other printed dimensions only as checks:

  | printed | measured | difference |
  |---|---|---|
  | 2650 (+ wheels) | 2651 mm (675 px) | +0.0 % |
  | 1480 (+ wheels 30) | 1473–1480 mm | ≤ 0.5 % |
  | 1720 | 1720 mm (438 px) | 0.0 % |
  | 2350 | 2352 mm (599 px) | +0.1 % |
  | MAX 2500 | 2501 mm (637 px) | 0.0 % |
  | 900 (net infeed) | 891 mm (227 px) | −1.0 % (arrowhead reading) |
  | 1500 (net infeed) | 1488 mm (379 px) | −0.8 % (arrowhead reading) |

- **Datums.** x = 0 is the front-most point, the hook-lift bail (start of MAX 6520), and +x runs
  towards the rear door. In the side-view numbers below, z is measured from the underside of the
  hook-lift rails, as on the drawing. The rollers add 30 mm below that (drawing: "1480 +
  wheels 30"), so `build_combi.py` adds W = 0.030 m to every drawing height. +y is the far side;
  the drawing's side view shows the near (−y) side, which carries the control panel.
- `build_combi.py` keeps the raw pixel coordinates in the code: `X(col)`, `Z(row)` and `Y(row)`.
  Every number can therefore be traced back to a pixel on the drawing.

## Overall and main dimensions

| Item | Value used | Source |
|---|---|---|
| Overall length | 6,520 mm (front bail tip → rear lug) | drawing (MAX 6520) |
| Container body length | 4,090 mm, x 2,062 → 6,152 | drawing (4090); start x measured from drawing |
| Overall width | 2,500 mm (rear hinge knuckles ↔ lock levers; front cross beam 2,490) | drawing (MAX 2500) |
| Container width | 2,350 mm | drawing |
| Press-section width | 1,720 mm | drawing |
| Height | 2,650 mm + 30 mm rollers (top of the rear door frame) | drawing ("2650 + wheels") |
| Infeed (loading) height | 1,480 mm + 30 mm rollers (front edge of the hopper lid) | drawing / spec table |
| Roller protrusion below the rails | 30 mm | drawing ("+ wheels 30") |
| Infeed aperture, net | 1,500 mm across × 900 mm along the axis; x 1,162 → 2,062 | drawing (top-view dims 1500 and 900; spec "1500 x 900") |
| Infeed aperture, gross with hopper | 1,450 × 1,510 mm | spec table. Not modelled separately: the hopper is drawn from the side-view lid line |
| Lowered side infeed 1,300 mm | — | spec table. Not modelled: we show the standard version |
| Compaction force 25 t, cycle 42 s, motor 5.5 kW, 400 V | — | spec table. Not geometric: the motor object is named `motor_5_5kW`, nothing else |

Note on the infeed: the brief says "1,500 long × 900 wide". The top view puts the 1500
dimension *across* the machine and 900 *along* its axis. We followed the drawing; the CombiMax
drawing uses the same convention (1850 across, 1300 along).

## Press section (exterior)

| Item | Value (mm; z above the rail underside) | Source |
|---|---|---|
| Front posts | x 94 – 277 | measured from drawing |
| Hook-lift bail | lug ring centre x 130, z 1,510; tip x 0, z 1,598; arc ±290 across | measured from drawing (side + top) |
| Front cross beam | x 173 – 283, y ±1,245 | measured from drawing (top view) |
| Front cross beam height | z 140 – 340 | **schematic** (visible only in the top view) |
| Front end blocks | x 71 – 188, y ±1,045 … ±1,245 | measured from drawing (top view) |
| Top deck of press section | z 1,372 | measured from drawing |
| Side-panel bands and ribs | z 161–194, 444–463, 862–999 | measured from drawing |
| Hopper lid line (front → rear hinge) | (x 326, z 1,480) → (x 2,007, z 1,991) | x measured from drawing; z 1,480 from drawing; z 1,991 measured from drawing |
| Hopper cheek rear edge | x 2,007 | measured from drawing |
| Control panel (rounded rectangle) | x 302 – 954, z 1,009 – 1,353 | measured from drawing. The drawing shows a rounded cover with four bolts; we treat it as the control-panel location (key switch + e-stop as in the photo) |
| Top service hatch | x 342 – 723, y +626 … −630 | measured from drawing (top view) |

## Container (exterior)

| Item | Value (mm) | Source |
|---|---|---|
| Container front face | x 2,062 | measured from drawing (start of the 4090 dimension) |
| Front corner posts | x 2,062 – 2,195, top z 2,474 | measured from drawing |
| Roof side edge (slopes up to the rear) | z 2,411 at x 2,195 → z 2,572 at x 6,036 | measured from drawing |
| Rear frame posts | x 6,036 – 6,161, top z 2,650 | measured from drawing; height from drawing |
| Rear discharge door | x 6,161 – 6,307, outer face tapering to x 6,397 between z 263 and 2,533 | measured from drawing |
| Rear centre lug (rear-most point) | x 6,397 – 6,520, z 1,402 – 1,677 | measured from drawing; end x from drawing (6520) |
| Underside of container body | z 247 | measured from drawing |
| Container floor | z 251 | measured from drawing |
| Bottom side rail | z 247 – 334 | measured from drawing |
| Horizontal side ribs | z 1,111 – 1,143 and 1,335 – 1,390 | measured from drawing |
| Floor cross-member ends | x 2,572 / 3,279 / 3,986 / 4,673 / 5,380, z 181 – 247 | measured from drawing |
| Roof ribs (top view) | y ±399, ±750, ±970, ±1,048 | measured from drawing |
| Locking handles | shaft x 5,753; levers at z 2,246 and 597, x 5,726 – 6,315 | measured from drawing |
| Door hinges | on the far (+y) edge | measured from drawing (top view: hinge knuckle sets MAX 2500 at +y) |
| Plain "EUROPRESS" lettering | spans x 3,350 – 5,247, centre z 1,830 | measured from drawing. Plain IBM Plex type, no logo mark |
| Hook-lift rails | z 0 – 181 | measured from drawing |
| Hook-lift rail spacing | rails at y ±480 … ±580 | **schematic** (not visible in either view) |
| Rollers | Ø150, centres at x 169 (front) and 6,216 (rear) | measured from drawing |
| Paint colour | #1F4FA4 | measured from the brochure photo (lit panels sample #1E4EAA – #2A53AB). The brief gives ≈ #1F4FA0 |

## Internals (all **schematic**, labelled on screen "Internal layout: schematic, not Europress CAD")

| Item | Value used | Basis |
|---|---|---|
| Ram face | 1,500 wide × 900 high (fills the chamber cross-section), 330 deep | brief; depth schematic |
| Ram retracted face | x 1,162 (front edge of the net infeed opening) | schematic, from measured opening |
| Ram entry into the container | 250 mm past the container mouth (x 2,312) | "20 to 30 centimeters", Europress product specialist |
| Ram stroke | 1,150 mm (900 mm infeed + 250 mm entry) | derived |
| Cylinders | 2 × double-acting, along the long axis behind the ram, at y ±420, centre 706 mm above the roller underside | schematic |
| Cylinder bore / sizes | barrel bore 125 (outer 150); telescopic stages Ø125 / Ø100, rod Ø75 | schematic (brief: bore 100–125) |
| Why telescopic | a single-stage cylinder with a 1.15 m stroke needs ≈1.4 m closed length, but only ≈0.55 m fits between the front wall and the retracted ram. Three telescopic stages keep the drawing consistent: no rod is longer than its barrel | schematic choice, not a claim about Europress's design |
| Power unit | shelf z 950–970 above the cylinders, in front of the ram; oil tank 480 × 900 × 200 (~86 L); motor Ø206 × 310; pump; valve block 180 × 200 × 110 with 3 solenoids | schematic |
| Control box | 592 × 118 × 324, directly behind the control panel | schematic |
| SMART Scale platform | ladder frame 6.42 m long (≈ machine length), rails 165 high, platform top 300 above the floor; one leg per corner on a load cell | count and corner positions from the Scale brochure ("four sensors … each corner"; "same length as the waste compactor"); sections and heights schematic |

## Sensors: positions and on-screen confidence label

Coordinates are machine coordinates in metres: x from the front, y negative = near side, z
above the roller underside. The machine stands 0.30 m higher on the scale platform.

| # | Sensor | Where in the model | On-screen tag |
|---|---|---|---|
| 1 | Hydraulic pressure transducer | top of the valve block on the power unit, (0.47, −0.33, 1.28–1.33) | position schematic |
| 2 | Ram, 20–30 cm into the container | ram face strokes 1.162 → 2.312; teal frame on the face; "20–30 cm" bracket | per Europress |
| 3 | Load cells × 4 (optional SMART Scale) | one under each corner leg of the platform: x 0.15 / 6.37, y ±0.71 | per Europress brochure |
| 4 | GPS / 5G SMART module | inside the control box behind the panel, (0.83, −0.76, 1.13) | position schematic |
| 5 | Tilt and movement sensor | inside the control box, (0.42, −0.76, 1.12) | position schematic |
| 6 | Door interlock switch | near-side rear frame post at the door edge, (6.105, −1.205, 1.33); actuator on the door | position schematic |
| 7 | Hopper lid switch | near hopper cheek at the hinge end of the lid, (1.99, −0.885, 1.895) | position schematic |
| 8 | Oil temperature probe (~€30, our proposal) | through the oil-tank lid, (0.75, −0.12, 1.17–1.205) | proposed |

Only the load-cell corners and the 20–30 cm ram entry come from Europress material. Every other
sensor position is a schematic placement and is tagged that way on screen.
