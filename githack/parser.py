#!/usr/bin/env python
#
# https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
#

import binascii
import collections
import mmap
import struct
import sys


def check(boolean, message):
    if not boolean:
        print("error: " + message)
        sys.exit(1)


def parse(filename, pretty=True):
    with open(filename, "rb") as o:
        f = mmap.mmap(o.fileno(), 0, access=mmap.ACCESS_READ)

        def read(format):
            format = "! " + format
            bytes = f.read(struct.calcsize(format))
            return struct.unpack(format, bytes)[0]

        index = collections.OrderedDict()

        index["signature"] = f.read(4).decode("ascii")
        check(index["signature"] == "DIRC", "Not a Git index file")

        index["version"] = read("I")
        check(index["version"] in {2, 3},
            "Unsupported version: %s" % index["version"])

        index["entries"] = read("I")

        yield index

        for n in range(index["entries"]):
            entry = collections.OrderedDict()

            entry["entry"] = n + 1

            entry["ctime_seconds"] = read("I")
            entry["ctime_nanoseconds"] = read("I")
            if pretty:
                entry["ctime"] = entry["ctime_seconds"]
                entry["ctime"] += entry["ctime_nanoseconds"] / 1000000000
                del entry["ctime_seconds"]
                del entry["ctime_nanoseconds"]

            entry["mtime_seconds"] = read("I")
            entry["mtime_nanoseconds"] = read("I")
            if pretty:
                entry["mtime"] = entry["mtime_seconds"]
                entry["mtime"] += entry["mtime_nanoseconds"] / 1000000000
                del entry["mtime_seconds"]
                del entry["mtime_nanoseconds"]

            entry["dev"] = read("I")
            entry["ino"] = read("I")

            entry["mode"] = read("I")
            if pretty:
                entry["mode"] = "%06o" % entry["mode"]

            entry["uid"] = read("I")
            entry["gid"] = read("I")
            entry["size"] = read("I")

            entry["sha1"] = binascii.hexlify(f.read(20)).decode("ascii")
            entry["flags"] = read("H")

            entry["assume-valid"] = bool(entry["flags"] & (0b10000000 << 8))
            entry["extended"] = bool(entry["flags"] & (0b01000000 << 8))
            stage_one = bool(entry["flags"] & (0b00100000 << 8))
            stage_two = bool(entry["flags"] & (0b00010000 << 8))
            entry["stage"] = stage_one, stage_two
            namelen = entry["flags"] & 0xFFF

            entrylen = 62

            if entry["extended"] and (index["version"] == 3):
                entry["extra-flags"] = read("H")
                entry["reserved"] = bool(entry["extra-flags"] & (0b10000000 << 8))
                entry["skip-worktree"] = bool(entry["extra-flags"] & (0b01000000 << 8))
                entry["intent-to-add"] = bool(entry["extra-flags"] & (0b00100000 << 8))
                entrylen += 2

            if namelen < 0xFFF:
                entry["name"] = f.read(namelen).decode("utf-8", "replace")
                entrylen += namelen
            else:
                name = []
                while True:
                    byte = f.read(1)
                    if byte == b"\x00":
                        break
                    name.append(byte)
                entry["name"] = b"".join(name).decode("utf-8", "replace")
                entrylen += 1

            padlen = (8 - (entrylen % 8)) or 8
            nuls = f.read(padlen)
            check(set(nuls) == {0} or set(nuls) == {b"\x00"[0]}, "padding contained non-NUL")

            yield entry

        f.close()
