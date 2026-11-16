"""
crash_suppressor.py - Bypasses preinit CPU feature check and preinit atomic flag initialization for ARMv8.0-A CPUs.
"""
import re
from typing import Tuple, Dict, Any, List, Union

# Match 32-byte ARM64 CPU feature check starting with ADRP X19, ...; MOV W10, #0x8030; LDR X8, [X19, ...]
CPU_RAW_RE = re.compile(
    rb".{3}[\x90\xb0\xd0\xf0]\x0a\x60\x90\x52\x68.{2}\xf9\xe9\x03\x28\x2a\x3f\x01\x0a\xea\xe1\x02\x00\x54\xe8\x03\x38\x36\xe8\x04\x50\x36",
    re.S,
)
REPLACEMENT_CPU = bytes.fromhex("190000141f2003d51f2003d51f2003d51f2003d51f2003d51f2003d51f2003d5")

# Match the 20-byte preinit LSE atomic body after the 8-byte ADRP X8 / ADD X8 prefix:
# mov w9, #1; ldaddal x9, x8, [x8]; cbz x8, +8; ret; nop
TARGET_ATOMIC_TAIL = bytes.fromhex("290080520801e9f8480000b4c0035fd61f2003d5")
REPLACEMENT_ATOMIC_TAIL = bytes.fromhex("090140f92a008052490000b4c0035fd60a0100f9")

def find_all(data: Union[bytes, bytearray, memoryview], pattern: bytes) -> List[int]:
    matches = []
    pos = 0
    while True:
        pos = data.find(pattern, pos)
        if pos == -1:
            break
        matches.append(pos)
        pos += len(pattern)
    return matches

def apply(data: bytearray, verify: bool = False, dry_run: bool = False, allow_missing: bool = False) -> Tuple[bool, Dict[str, Any]]:
    raw_cpu = [m.start() for m in CPU_RAW_RE.finditer(data)]
    repl_cpu = find_all(data, REPLACEMENT_CPU)
    raw_atomic = find_all(data, TARGET_ATOMIC_TAIL)
    repl_atomic = find_all(data, REPLACEMENT_ATOMIC_TAIL)

    info = {
        "name": "failfast_cpu_and_atomic",
        "cpu_raw": [hex(x) for x in raw_cpu],
        "cpu_patched": [hex(x) for x in repl_cpu],
        "atomic_raw": [hex(x) for x in raw_atomic],
        "atomic_patched": [hex(x) for x in repl_atomic]
    }

    cpu_total = len(raw_cpu) + len(repl_cpu)
    atomic_total = len(raw_atomic) + len(repl_atomic)

    if (cpu_total == 0 or atomic_total == 0):
        if allow_missing:
            info["status"] = "skipped_missing"
            return True, info
        info["status"] = "missing_signature"
        return False, info

    if verify:
        v_ok = (len(raw_cpu) == 0 and len(repl_cpu) >= 1 and len(raw_atomic) == 0 and len(repl_atomic) >= 1)
        info["status"] = "verified" if v_ok else "unverified"
        return v_ok, info

    if len(raw_cpu) == 0 and len(raw_atomic) == 0:
        info["status"] = "already_patched"
        return True, info

    if not dry_run:
        for pos in raw_cpu:
            data[pos:pos + len(REPLACEMENT_CPU)] = REPLACEMENT_CPU
        for pos in raw_atomic:
            data[pos:pos + len(REPLACEMENT_ATOMIC_TAIL)] = REPLACEMENT_ATOMIC_TAIL
        info["status"] = "patched"
    else:
        info["status"] = "dry_run"

    return True, info
