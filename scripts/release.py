import sys
sys.path.insert(0, ".")

import zipfile, re
from pathlib import Path
from scripts.blender import *

init = (root / "nodeserial/__init__.py").read_text()
version_match = re.search(r"\"version\"\:\s\(([0-9]{1}),\s?([0-9]{1,2})\)", init)
mj, mn = version_match[1], version_match[2]

releases = root / "_releases"
releases.mkdir(exist_ok=True, parents=True)

release:Path = releases / f"nodeserial-v{mj}-{mn}.zip"
if release.exists():
    release.unlink()

zf = zipfile.ZipFile(release, "w")
for file in Path("nodeserial").iterdir():
    if not file.is_dir():
        zf.write(file)
zf.close()