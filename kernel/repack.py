"""Replace only the kernel gzip, preserving the proven ROM's DTBs and ramdisk."""
from pathlib import Path
import hashlib
import json
import struct
import zlib
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--original', type=Path, required=True)
parser.add_argument('--kernel', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if args.output.exists() or args.output.with_suffix('.json').exists():
    raise FileExistsError('Output or report already exists')
original = args.original.read_bytes()
assert hashlib.sha256(original).hexdigest() == "0db389f0d9223d6b4aa4e0a60e3c2c2bbc0b1bfb29e1d773ef4bd2aea47cd05f"
assert original[:8] == b"ANDROID!"
ks, ka, rs, ra, ss, sa, ta, page, version, osv = struct.unpack_from("<10I", original, 8)
assert page == 4096 and version == 0 and ss == 0
align = lambda n: (n + page - 1) // page * page
oldkernel = original[page:page+ks]
ramdisk_start = page + align(ks)
ramdisk = original[ramdisk_start:ramdisk_start+rs]
assert len(original) == ramdisk_start + align(rs)
gz = zlib.decompressobj(31)
raw = gz.decompress(oldkernel) + gz.flush()
assert gz.eof and raw[56:60] == b"ARM\x64"
dtbs = gz.unused_data
assert dtbs[:4] == b"\xd0\x0d\xfe\xed"

def image_id(kernel):
    sha = hashlib.sha1()
    # This LG-compatible v0 header hashes zero sizes for both second stage and
    # the separate DT field. Its actual DTBs are appended inside the kernel.
    for data in (kernel, ramdisk, b"", b""):
        sha.update(data)
        sha.update(struct.pack("<I", len(data)))
    return sha.digest() + b"\0" * 12

assert image_id(oldkernel) == original[576:608], "Original v0 image ID formula mismatch"
newgzip = args.kernel.read_bytes()
ngz = zlib.decompressobj(31)
newraw = ngz.decompress(newgzip) + ngz.flush()
assert ngz.eof and not ngz.unused_data and newraw[56:60] == b"ARM\x64"
newkernel = newgzip + dtbs
header = bytearray(original[:page])
struct.pack_into("<I", header, 8, len(newkernel))
header[576:608] = image_id(newkernel)
pad = lambda data: data + bytes(align(len(data)) - len(data))
output = bytes(header) + pad(newkernel) + pad(ramdisk)
assert len(output) < 41943040
check_header = bytearray(header)
check_header[8:12] = original[8:12]
check_header[576:608] = original[576:608]
assert bytes(check_header) == original[:page]
path = args.output
path.write_bytes(output)
report = {
    "original_sha256": hashlib.sha256(original).hexdigest(),
    "output_sha256": hashlib.sha256(output).hexdigest(),
    "output_size": len(output),
    "kernel_gzip_size": len(newgzip),
    "preserved_dtbs_size": len(dtbs),
    "preserved_dtbs_sha256": hashlib.sha256(dtbs).hexdigest(),
    "preserved_ramdisk_sha256": hashlib.sha256(ramdisk).hexdigest(),
    "header_changes": ["kernel_size", "image_id"],
    "boot_partition_size": 41943040,
    "source_commit": "7e7397d497cdbfc0deedb9295d54d755f799fdd8",
    "compiler": "Ubuntu clang 14 + LLD 14",
    "device_test": "This newly repacked file has not been flashed by this script",
}
args.output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
