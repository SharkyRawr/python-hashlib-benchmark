#! /usr/bin/env python3

import hashlib
import os
import platform
import time
from typing import Callable

tqdm = None
try:
    import tqdm
except:
    pass

TEST_DATA_SIZE = 1024*1024*1024  # 1GB
TEST_BUFFER = bytes()


def prepare_test_data(size: int) -> int:
    if os.path.lexists('test.bin'):
        return 0
    buf = b'\xab\xad\xba\xbe'
    with open("test.bin", 'wb') as f:
        for i in range(int(size / len(buf))):
            f.write(buf)
        return f.tell()


def hashit(hashfunc: Callable, buffer: bytes) -> None:
    hash = hashfunc()
    hash.update(buffer)
    # return hash.digest().hex()


def log(msg: str) -> None:
    os.write(2, msg.encode('utf8') + b'\n')


def bench() -> None:

    log("Preparing {} bytes test data, this might take a while ...".format(TEST_DATA_SIZE))
    TEST_DATA = bytes()
    bytes_written = prepare_test_data(TEST_DATA_SIZE)
    if bytes_written == 0:
        log("Found an already prepared test file, neat!")
    else:
        log("Finished preparing: {}".format(bytes_written))

    with open('test.bin', 'rb') as f:
        TEST_BUFFER = f.read()
    if len(TEST_BUFFER) != TEST_DATA_SIZE:
        raise Exception("test buffer is the expected size")

    results = {}
    with open("results.csv", "w") as f:
        f.write("# Created by Fynne's Python hashlib bench.py - https://github.com/SharkyRawr/python-hashlib-benchmark ,,\n")
        f.write("# This file has been created on a: " +
                platform.processor() + ',,\n')
        f.write('Hash,Duration in ns,bytes per second\n')
        if tqdm:
            pb = tqdm.tqdm(total=len(list(hashlib.algorithms_available)))
        else:
            pb = None
        for a in sorted(hashlib.algorithms_available):
            if not hasattr(hashlib, a):
                if tqdm:
                    pb.update()
                continue
            start = time.time_ns()
            hashit(getattr(hashlib, a), TEST_BUFFER)
            duration = time.time_ns() - start
            bps = (len(TEST_BUFFER) / duration) * 1e9
            msg = "{},{},{}".format(a, duration, bps)
            f.write(msg + "\n")
            if tqdm:
                pb.write(msg)
                pb.update()
        if tqdm:
            pb.close()
    log("Done!")


if __name__ == '__main__':
    bench()
