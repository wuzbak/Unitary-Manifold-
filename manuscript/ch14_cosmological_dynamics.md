# Chapter 14 — Cosmological Dynamics from 5D Irreversibility Geometry

This chapter formalizes the cosmology lane used in the executable framework: scalar tilt, tensor ratio routing, birefringence lanes, and the dark-energy decision protocol.

## Core equations tracked in code

- `n_s = 1 - 6\epsilon + 2\eta` with UM-consistent closure at `n_s = 0.9635`
- `r_bare = 16\epsilon` then braided correction `r = r_bare * c_s = 0.0315`
- Birefringence sectors `beta = {0.273°, 0.331°}` with explicit forbidden interval

## Observable-facing structure

1. **CMB scalar tilt lane:** currently consistent with Planck.
2. **Tensor lane:** explicit routing for SO DR1 and CMB-S4 windows.
3. **Dark-energy lane:** DESI DR3 tripwire hardcoded and preregistered.
4. **Amplitude lane:** residual bounded and tracked as open architecture gap.

## Machine-readable anchors

- `src/core/inflation.py`
- `src/core/braided_winding.py`
- `src/core/pillar442_so_dr1_routing.py`
- `src/core/pillar486_desi_dr3_final_prep.py`
- `src/core/pillar495_cmb_amplitude_ir_window.py`

## Epistemic status

- Derived for tilt and braided tensor routing
- Open-gap bounded for CMB peak amplitude normalization
- Preregistered decision windows for DESI / SO / LiteBIRD
