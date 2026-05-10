# Data Directory — DVC Managed

This directory is managed by [DVC](https://dvc.org/) (Data Version Control).

## Strategy

Large data files (CMB power spectra, KK benchmarks) are **not committed to git**.
Instead, DVC tracks them via checksums in `.dvc` files, and the actual data
lives in remote storage (S3).

## Remotes

| Remote | URL |
|--------|-----|
| `nasa-lambda` | `s3://unitary-manifold-data/nasa-lambda` |
| `cern-opendata` | `s3://unitary-manifold-data/cern-opendata` |

## Fetching Data

```bash
# Pull all DVC-tracked data from default remote
dvc pull

# Run a specific pipeline stage
dvc repro planck_2018_cmb
```

## Stages

- **planck_2018_cmb**: Downloads Planck 2018 PR3 CMB parameters → `data/planck_2018/power_spectrum.npz`
- **kk_spectrum_benchmark**: Runs KK tower VQE → `data/kk_spectrum.json`
- **jax_evolution_benchmark**: Runs JAX field agreement check → `data/jax_benchmark.json`
