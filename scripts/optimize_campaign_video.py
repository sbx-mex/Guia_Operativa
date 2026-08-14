from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def optimize(source: Path, video_output: Path, poster_output: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg es obligatorio para optimizar el video")
    video_output.parent.mkdir(parents=True, exist_ok=True)
    poster_output.parent.mkdir(parents=True, exist_ok=True)
    run([
        ffmpeg, "-y", "-i", str(source), "-an", "-vf", "fps=24,scale=360:-2:flags=lanczos",
        "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(video_output),
    ])
    run([
        ffmpeg, "-y", "-ss", "0.35", "-i", str(source), "-frames:v", "1",
        "-vf", "scale=360:-2:flags=lanczos", "-c:v", "libwebp", "-quality", "78", str(poster_output),
    ])
    if video_output.stat().st_size >= source.stat().st_size:
        raise SystemExit("La salida no mejoró el peso del video original")
    print(
        f"Video optimizado: {source.stat().st_size} -> {video_output.stat().st_size} bytes "
        f"({(1 - video_output.stat().st_size / source.stat().st_size) * 100:.1f}% menos)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Optimiza el video Unicorn para reproducción tipo GIF en la app.")
    parser.add_argument("source", type=Path)
    parser.add_argument("video_output", type=Path)
    parser.add_argument("poster_output", type=Path)
    args = parser.parse_args()
    optimize(args.source, args.video_output, args.poster_output)


if __name__ == "__main__":
    main()
