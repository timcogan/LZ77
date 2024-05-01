from typing import Final, Optional, Tuple

from bitarray import bitarray


MATCH_LENGTH_MASK: Final[int] = 0xF
WINDOW_SIZE: Final[int] = 0xFFF
IS_MATCH_BIT: Final[bool] = True

# We only consider substrings of length 2 and greater, and just
# output any substring of length 1 (9 bits uncompressed is better than a 17-bit
# reference for the flag, distance, and length)
# Since lengths 0 and 1 are unused, we can encode lengths 2-17 in only 4 bits.
LENGTH_OFFSET: Final[int] = 2


def compress(data: bytes) -> bytes:
    output_buffer = bitarray(endian="big")

    i = 0
    while i < len(data):
        if match := find_longest_match(data, i):
            match_distance, match_length = match
            output_buffer.append(IS_MATCH_BIT)
            dist_hi, dist_lo = match_distance >> 4, match_distance & 0xF
            output_buffer.frombytes(bytes([dist_hi, (dist_lo << 4) | (match_length - LENGTH_OFFSET)]))
            i += match_length
        else:
            output_buffer.append(not IS_MATCH_BIT)
            output_buffer.frombytes(bytes([data[i]]))
            i += 1

    output_buffer.fill()  # Pad to complete last byte
    return output_buffer.tobytes()


def decompress(compressed_bytes: bytes) -> bytes:
    data = bitarray(endian="big")
    data.frombytes(compressed_bytes)
    assert data, f"Cannot decompress {compressed_bytes}"

    output_buffer = []

    while len(data) >= 9:  # Anything less than 9 bits is padding
        if data.pop(0) != IS_MATCH_BIT:
            byte = data[:8].tobytes()
            del data[:8]
            output_buffer.append(byte)
        else:
            hi, lo = data[:16].tobytes()
            del data[:16]
            distance = (hi << 4) | (lo >> 4)
            length = (lo & MATCH_LENGTH_MASK) + LENGTH_OFFSET
            for _ in range(length):
                output_buffer.append(output_buffer[-distance])

    return b"".join(output_buffer)


def find_longest_match(data: bytes, current_position: int) -> Optional[Tuple[int, int]]:
    end_of_buffer = min(current_position + MATCH_LENGTH_MASK + LENGTH_OFFSET, len(data))
    search_start = max(0, current_position - WINDOW_SIZE)

    for match_candidate_end in range(end_of_buffer, current_position + LENGTH_OFFSET + 1, -1):
        match_candidate = data[current_position:match_candidate_end]
        for search_position in range(search_start, current_position):
            if match_candidate == get_wrapped_slice(data[search_position:current_position], len(match_candidate)):
                return current_position - search_position, len(match_candidate)


def get_wrapped_slice(x: bytes, num_bytes: int) -> bytes:
    """
    Examples:
        f(b"1234567", 5) -> b"12345"
        f(b"123", 5) -> b"12312"
    """
    repetitions = num_bytes // len(x)
    remainder = num_bytes % len(x)
    return x * repetitions + x[:remainder]
