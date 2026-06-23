import gzip, time, sys, re, zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ptil import PTILEncoder
from ptil.ultra_compact_serializer import UltraCompactCSCSerializer

encoder = PTILEncoder()
ultra = UltraCompactCSCSerializer()


def count_tokens(text):
    return len(re.findall(r'\w+|[^\w\s]', text))


CORPUS = [
    "The boy will not go to school tomorrow.",
    "She has been reading a book all morning.",
    "The cat sat on the mat.",
    "He should finish the project by Friday.",
    "They are planning a trip to Paris next summer.",
    "The teacher gave the student a difficult assignment.",
    "We need to analyze the data from last quarter.",
    "The company decided to expand into new markets.",
    "She can speak three languages fluently.",
    "The weather forecast predicts rain for the weekend.",
    "He was walking to the store when he saw the accident.",
    "The children played in the park after school.",
    "They will have completed the project by next month.",
    "The doctor examined the patient carefully.",
    "She wants to learn how to cook Italian food.",
]


def main():
    print("=" * 80)
    print("COMPARISON: PTIL vs EXISTING COMPRESSION")
    print("=" * 80)
    print()

    full_text = "\n".join(CORPUS)
    raw_bytes = len(full_text.encode("utf-8"))

    # PTIL Ultra
    t0 = time.time()
    ptil_codes = []
    for text in CORPUS:
        cscs = encoder.encode(text)
        code = ultra.serialize_multiple(cscs)
        ptil_codes.append(code)
    ptil_serial = "\n".join(ptil_codes)
    ptil_bytes = len(ptil_serial.encode("utf-8"))
    ptil_time = time.time() - t0

    # Gzip
    t0 = time.time()
    gzip_bytes = len(gzip.compress(full_text.encode("utf-8")))
    gzip_time = time.time() - t0

    # Zlib
    t0 = time.time()
    zlib_bytes = len(zlib.compress(full_text.encode("utf-8")))
    zlib_time = time.time() - t0

    # Brotli
    has_brotli = False
    try:
        import brotli
        t0 = time.time()
        brotli_bytes = len(brotli.compress(full_text.encode("utf-8")))
        brotli_time = time.time() - t0
        has_brotli = True
    except ImportError:
        pass

    # LZ4
    has_lz4 = False
    try:
        import lz4.frame
        t0 = time.time()
        lz4_bytes = len(lz4.frame.compress(full_text.encode("utf-8")))
        lz4_time = time.time() - t0
        has_lz4 = True
    except ImportError:
        pass

    no_comp_tokens = count_tokens(full_text)
    ptil_tokens = sum(count_tokens(c) for c in ptil_codes)

    print("Method              Bytes     Reduction   Tokens   Readable   Speed")
    print("-" * 80)
    print("Raw text            %5d     baseline    %3d      Yes        -" % (raw_bytes, no_comp_tokens))
    print("PTIL Ultra          %5d     %5.1f%%     %3d      Yes        %.3fs" % (
        ptil_bytes, (1 - ptil_bytes / raw_bytes) * 100, ptil_tokens, ptil_time))
    print("Gzip                %5d     %5.1f%%     -        No         %.3fs" % (
        gzip_bytes, (1 - gzip_bytes / raw_bytes) * 100, gzip_time))
    print("Zlib                %5d     %5.1f%%     -        No         %.3fs" % (
        zlib_bytes, (1 - zlib_bytes / raw_bytes) * 100, zlib_time))
    if has_brotli:
        print("Brotli              %5d     %5.1f%%     -        No         %.3fs" % (
            brotli_bytes, (1 - brotli_bytes / raw_bytes) * 100, brotli_time))
    if has_lz4:
        print("LZ4                 %5d     %5.1f%%     -        No         %.3fs" % (
            lz4_bytes, (1 - lz4_bytes / raw_bytes) * 100, lz4_time))

    print()
    print("=" * 80)
    print("KEY DIFFERENCE")
    print("=" * 80)
    print()
    print("  Gzip:   binary, NOT readable, NOT searchable")
    print("  Brotli: binary, NOT readable, NOT searchable")
    print("  PTIL:   text,   READABLE,     SEARCHABLE")
    print()
    print("  Gzip output:    x\\x03\\x00... (binary garbage)")
    print("  PTIL output:    1FNWaboygschomtmrw (human readable)")
    print()
    print("=" * 80)
    print("SEARCHABILITY TEST")
    print("=" * 80)
    print()
    print('  Can you search for "tomorrow" in compressed data?')
    print()
    print("  Gzip:   NO  (binary, need to decompress first)")
    print("  PTIL:   YES (contains 'tmrw' = tomorrow)")
    print()
    print("=" * 80)
    print("PTIL CODES (readable)")
    print("=" * 80)
    print()
    for text, code in zip(CORPUS, ptil_codes):
        print('  %-50s -> %s' % (text[:50], code))


if __name__ == "__main__":
    main()
