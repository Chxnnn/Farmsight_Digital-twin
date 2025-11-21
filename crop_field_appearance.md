Wheat Field 3D Visualization Specification

(Irrigation & Fertilization Stress → Field-Level Rendering)

🌾 Overview

This document defines how irrigation and fertilization stress levels affect the 3D visualization of an entire wheat field across all growth phases.
It includes:

Field-level traits: plant density, canopy closure, patchiness

Plant-level traits: height, color, leaf posture, tillering, stem bending

Stress thresholds based on real irrigation (0–100%) and fertilization (0–100%) levels

Four stress levels:

Ideal

Tier 1 (Minor)

Tier 2 (Moderate)

Tier 3 (Severe)

🌧️ Global Stress Levels
Irrigation Stress (0–100% of required water)
Tier	Stress Level	% Range	Meaning
Tier 0	Ideal	70–100%	Soil moisture optimal
Tier 1	Minor	50–70%	Mild drought signs
Tier 2	Moderate	30–50%	Strong drought stress
Tier 3	Severe	0–30%	Critical drought: collapse, death patches
Fertilization Stress (0–100% of required nitrogen)
Tier	Stress Level	% Range	Meaning
Tier 0	Ideal	80–100%	Adequate nitrogen
Tier 1	Minor	60–80%	Noticeable N deficiency
Tier 2	Moderate	40–60%	Clear yellowing, stunting
Tier 3	Severe	0–40%	Strong chlorosis, low tillers, die-off
🌿 Field-Level Visualization Parameters (Global)
Stress Tier	Density (Plants/m²)	Canopy Coverage	Patchiness	Average Color
Ideal	60–80	Full canopy	No gaps	Rich green
Tier 1	40–60	Mostly full	Small gaps	Slight pale green
Tier 2	20–40	Partial closure	Medium patches	Yellow-green
Tier 3	5–20	Sparse	Large barren patches	Yellow–brown

These apply across all growth stages with stage-specific variations added below.

🧬 Growth Phases (With 3D Visualization Rules)
🌱 1. Emergence (0–10 days)
Ideal (70–100% irrigation, 80–100% fertilization)

Even emergence across field

Bright green seedlings

No gaps

Soil evenly moist

3D:

Dense sprouts evenly spaced

Color: #4CAF50 bright green

No curling

Tier 1 – Minor Stress

(50–70% irrigation OR 60–80% fertilization)

Small empty spots

Slightly pale leaves

Slight leaf-edge curl

3D:

Density reduced ~10%

Slight curl (5°)

Color: slightly desaturated green

Tier 2 – Moderate Stress

(30–50% irrigation OR 40–60% fertilization)

Many weak seedlings

Visible patchiness

Yellow tint

Slow emergence

3D:

Density reduced ~30%

Curl 10–15°

Color: yellow-green (#A3C76D)

Height reduced ~20%

Tier 3 – Severe Stress

(0–30% irrigation OR 0–40% fertilization)

Sparse field

Many dead seedlings

Brown tips

Soil cracked or extremely dry

3D:

Density reduced ~60%

Heavy curl 25–35°

Color: brownish-yellow

Height ~40% of ideal

🌿 2. Tillering (10–30 days)
Ideal

Many tillers per plant

Full canopy closure

Dark green color

3D:

Dense vegetation

High tiller count

Tier 1 – Minor

Slightly uneven canopy

Slight pale lower leaves

Slight reduction in tillers

3D:

Density ↓ ~15%

Color slightly pale

Mild leaf roll

Tier 2 – Moderate

Strong patchiness

Many weaker or small tillers

Yellowing lower leaves

3D:

Density ↓ ~35%

Height ↓ ~20%

Leaf curl strong

Color: yellow-green

Tier 3 – Severe

Many dead tillers

Sparse field

Brown leaf clusters

3D:

Density ↓ 60–70%

Dry texture patches

Height ↓ 40–50%

Strong curling

🌾 3. Stem Elongation (30–50 days)
Ideal

Tall straight stems

Dark green canopy

Uniform field height

3D: Straight rows, even height.

Tier 1 – Minor

Slight height differences

Mild leaf fold

3D:

Slight bending (5°)

Slight dullness

Tier 2 – Moderate

Visible uneven heights

Rolling leaves, bending stems

3D:

Stem bend 10–20°

Color yellowish

Height ↓ ~20%

Tier 3 – Severe

Large collapsed areas

Many stems bent or dead

3D:

Height ↓ 40–50%

Strong brown patches

Heavy bending or collapse

🌾 4. Booting (50–60 days)
Ideal

Upright flag leaves

Even boot swelling

3D: Uniform boot bulge.

Tier 1 – Minor

Slightly pale flag leaves

Mild softening of boot

3D: Slight deformation, mild desaturation.

Tier 2 – Moderate

Noticeable boot distortions

Patchy canopy height

3D:

Moderate deformation

Uneven canopy

Tier 3 – Severe

Boot collapse

High sterility

Yellow/brown zones

3D:

Large deformed areas

Dry textures

Bent stems

🌾 5. Heading (60–80 days)
Ideal

Straight spikes

Fully emerged heads

3D: Clean spikes, upright.

Tier 1 – Minor

Awn tips dry

Slight uneven color

3D: Slight color fade.

Tier 2 – Moderate

Heads droop

Early bleaching patches

3D:

Head bend 10–15°

Yellow tips

Tier 3 – Severe

Severe wilting

Spike collapse

Grain sites drying early

3D:

Head bend 25–40°

Dry textures

Color: pale gold to brown

🌾 6. Grain Filling (80–100 days)
Ideal

Plump grains

Uniform golden transition

3D: Smooth color gradient green → gold.

Tier 1 – Minor

Slight grain shrink

Faster drying

3D:

Slight kernel size reduction

Tier 2 – Moderate

30–50% grain shrivel

Premature drying

3D:

Kernel size reduced

Yellow-brown patches

Tier 3 – Severe

Severe shrinkage

Heavy lodging

Grain abortion

3D:

Collapsed stems

Strong brown textures

Sparse productive heads