import argparse
import os
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install it with 'pip install pillow'.")
    sys.exit(1)

FACE_ALIASES = {
    "posx": "posx",
    "negx": "negx",
    "posy": "posy",
    "negy": "negy",
    "posz": "posz",
    "negz": "negz",
    "right": "posx",
    "left": "negx",
    "up": "posy",
    "top": "posy",
    "down": "negy",
    "bottom": "negy",
    "front": "posz",
    "back": "negz",
    "+x": "posx",
    "-x": "negx",
    "+y": "posy",
    "-y": "negy",
    "+z": "posz",
    "-z": "negz",
}
FACE_ORDER = ["posx", "negx", "posy", "negy", "posz", "negz"]
EXTENSIONS = [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp", ".tga"]


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def find_face_files(folder: Path):
    faces = {}
    warnings = []

    for path in folder.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in EXTENSIONS:
            continue

        normalized = normalize_name(path.stem)
        matched = None
        for alias, face in FACE_ALIASES.items():
            if normalized == alias or normalized.endswith(alias) or normalized.startswith(alias):
                matched = face
                break

        if matched:
            if matched in faces:
                warnings.append(f"Multiple candidate files found for {matched}: {faces[matched].name} and {path.name}. Using {faces[matched].name}.")
            else:
                faces[matched] = path

    missing = [face for face in FACE_ORDER if face not in faces]
    return faces, missing, warnings


def load_images(face_files):
    loaded = {}
    for face, path in face_files.items():
        try:
            img = Image.open(path)
            loaded[face] = img.convert("RGBA")
        except Exception as exc:
            raise RuntimeError(f"Failed to open {path}: {exc}") from exc
    return loaded


def normalize_sizes(images):
    sizes = [(img.width, img.height) for img in images.values()]
    min_side = min(min(w, h) for w, h in sizes)
    if any(w != min_side or h != min_side for w, h in sizes):
        resized = {}
        for face, img in images.items():
            if img.width != min_side or img.height != min_side:
                resized[face] = img.resize((min_side, min_side), Image.LANCZOS)
            else:
                resized[face] = img
        return resized, min_side
    return images, min_side


def build_cross_image(images, face_size):
    width = face_size * 4
    height = face_size * 3
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 255))

    layout = {
        "posy": (face_size, 0),
        "negy": (face_size, face_size * 2),
        "negx": (0, face_size),
        "posz": (face_size, face_size),
        "posx": (face_size * 2, face_size),
        "negz": (face_size * 3, face_size),
    }

    for face, position in layout.items():
        canvas.paste(images[face], position)

    return canvas


def save_face_images(images, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for face, img in images.items():
        face_path = output_dir / f"{face}.webp"
        img.save(face_path, format="WEBP", quality=90, method=6)
        written.append(face_path)
    return written


def parse_args():
    parser = argparse.ArgumentParser(description="Create a complete skybox WebP from six named face images.")
    parser.add_argument("path", help="Folder containing the six skybox face images, or one image inside that folder.")
    parser.add_argument("-o", "--output", help="Output path for the generated WebP file or folder.")
    parser.add_argument("--keep-faces", action="store_true", help="Also save each face individually as a WebP file in a subfolder.")
    parser.add_argument("--quality", type=int, default=90, help="WebP quality (0-100). Default: 90")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.path).expanduser().resolve()

    if input_path.is_file():
        folder = input_path.parent
    else:
        folder = input_path

    if not folder.exists() or not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory.")
        return 1

    face_files, missing, warnings = find_face_files(folder)
    if warnings:
        for warning in warnings:
            print(f"Warning: {warning}")

    if missing:
        print("Error: Missing skybox faces:")
        for face in missing:
            print(f"  - {face}")
        print("Expected files with names containing: posx, negx, posy, negy, posz, negz")
        return 1

    images = load_images(face_files)
    images, face_size = normalize_sizes(images)

    output_base = Path(args.output).expanduser().resolve() if args.output else folder / "skybox-cross.webp"
    if output_base.is_dir():
        output_file = output_base / "skybox-cross.webp"
        face_out_dir = output_base / "skybox-faces"
    elif output_base.suffix.lower() == ".webp":
        output_file = output_base
        face_out_dir = output_base.parent / (output_base.stem + "-faces")
    else:
        output_file = output_base / "skybox-cross.webp"
        face_out_dir = output_base / "skybox-faces"

    if args.keep_faces:
        saved_faces = save_face_images(images, face_out_dir)
        print(f"Saved individual face files to: {face_out_dir}")

    cross = build_cross_image(images, face_size)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cross.save(output_file, format="WEBP", quality=args.quality, method=6)
    print(f"Created skybox WebP: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
