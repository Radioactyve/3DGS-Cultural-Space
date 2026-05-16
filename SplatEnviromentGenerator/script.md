# Gaussian Splat Processing Tool

This script automates the generation of Level of Detail (LOD) streaming files and collision data from a base Gaussian Splat PLY file.

## Usage

Run the script from your terminal by providing the path to the folder containing your `splat_base.ply` file.

```bash
python process_splats.py "C:/Path/To/Your/Folder"
```

If you run the script without an argument, it will prompt you to enter the folder path manually.

## Process Details

The script executes the following sequence of operations:

1. **High Quality**: Filters NaNs and aligns the base file into `splat_high.ply`.
2. **Decimation**: Generates `splat_mid.ply` (50% density) and `splat_low.ply` (10% density).
3. **LOD Streaming**: Creates the `lodSplat/` directory with chunked streaming data and `lod-meta.json`.
4. **Collision Data**: Generates `terrain.voxel.json` (voxel data) and `terrain.glb` (collision mesh).

## Reference Commands

For manual execution, these are the underlying commands used by the script:

```bash
# Clean base splat
splat-transform splat_base.ply --filter-nan -M splat_high.ply

# Create Gaussian decimation
splat-transform splat_high.ply -F 50% splat_mid.ply
splat-transform splat_high.ply -F 10% splat_low.ply

# Generate LOD streaming
splat-transform splat_high.ply -l 0 splat_mid.ply -l 1 splat_low.ply -l 2 lodSplat/lod-meta.json --filter-nan --filter-harmonics 0

# Generate collision (Voxel & GLB)
splat-transform splat_low.ply --filter-cluster --seed-pos 0,1,0 --voxel-params 0.05,0.1 --voxel-external-fill 1.6 --voxel-floor-fill 1.6 --voxel-carve 1.6,0.2 -K terrain.voxel.json
```

## Requirements

The script requires the `splat-transform` utility to be installed and available in your system's PATH.

---
**File:** [process_splats.py](file:///d:/TFM/PlayCanvas/LOD%20Maps/SplatEnviromentGenerator/process_splats.py)