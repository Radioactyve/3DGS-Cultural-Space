import os
import subprocess
import sys

def run_command(command, cwd):
    print(f"\n>> Running: {' '.join(command)}")
    try:
        # We use Popen to stream the output in real-time to the terminal
        process = subprocess.Popen(
            command, 
            cwd=cwd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1,
            universal_newlines=True,
            shell=True
        )
        
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        if process.returncode == 0:
            return True
        else:
            print(f"FAILED: Command exited with code {process.returncode}")
            return False
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        return False

def process_folder(folder_path):
    # Normalize path and check existence
    folder_path = os.path.abspath(folder_path)
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return

    base_ply = os.path.join(folder_path, "splat_base.ply")
    if not os.path.exists(base_ply):
        print(f"Error: 'splat_base.ply' not found in {folder_path}")
        return

    print(f"\n--- Starting Processing for: {folder_path} ---\n")

    # Create lodSplat and collission directories if they don't exist
    for subfolder in ["lodSplat", "collission"]:
        dir_path = os.path.join(folder_path, subfolder)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    commands = [
        ["splat-transform", "splat_base.ply", "--filter-nan", "-M", "splat_high.ply"],
        ["splat-transform", "splat_high.ply", "-F", "50%", "splat_mid.ply"],
        ["splat-transform", "splat_high.ply", "-F", "10%", "splat_low.ply"],
        ["splat-transform", "splat_high.ply", "-l", "0", "splat_mid.ply", "-l", "1", "splat_low.ply", "-l", "2", "lodSplat/lod-meta.json", "--filter-nan", "--filter-harmonics", "0"],
        ["splat-transform", "splat_low.ply", "--filter-cluster", "--seed-pos", "0,0,0", "--voxel-params", "0.25,0.2", "--voxel-floor-fill", "-K", "collission/terrain.voxel.json"]
    ]

    for i, cmd in enumerate(commands):
        print(f"\n[Step {i+1}/{len(commands)}]")
        if not run_command(cmd, folder_path):
            print("\n!!! Processing stopped due to error !!!")
            return

    print("\n==========================================")
    print("SUCCESS: All steps completed successfully!")
    print("==========================================\n")

if __name__ == "__main__":
    # If a path was provided as an argument, use it
    if len(sys.argv) > 1:
        target_folder = " ".join(sys.argv[1:])
    else:
        # Otherwise, ask the user
        target_folder = input("Enter the path to the folder containing splat_base.ply: ").strip().strip('"')

    if target_folder:
        process_folder(target_folder)
    else:
        print("No folder provided. Exiting.")
