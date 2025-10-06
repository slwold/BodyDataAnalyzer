import struct

from msgpack import packb, unpackb


def load_length(data_stream, struct_type):
    length = struct.unpack(struct_type, data_stream.read(struct.calcsize(struct_type)))[
        0
    ]
    return data_stream.read(length)


def load_string(data_stream):
    length = 0
    i = 0
    while True:
        serial = struct.unpack("B", data_stream.read(struct.calcsize("B")))[0]
        length |= (0b01111111 & serial) << 7 * i
        if serial >> 7 != 1:
            break
        i += 1
    data = data_stream.read(length)
    return data


def load_type(data_stream, struct_type):
    return struct.unpack(struct_type, data_stream.read(struct.calcsize(struct_type)))[0]


def write_string(data_stream, value):
    length_bytes = b""
    length = len(value)
    while True:
        serial = length & 0b1111111
        if length >> 7 != 0:
            length = length >> 7
            length_bytes += struct.pack("b", 0b10000000 | serial)
        else:
            length_bytes += struct.pack("b", serial)
            break
    data_stream.write(length_bytes)
    data_stream.write(value)


def msg_unpack(data):
    try:
        # 首先尝试标准解析方式
        return unpackb(data, raw=False, strict_map_key=False)
    except Exception:
        # 如果标准方式失败，尝试用raw=True解析，然后手动处理字符串
        try:
            result = unpackb(data, raw=True, strict_map_key=False)
            # 递归处理可能的二进制字符串
            if isinstance(result, bytes):
                try:
                    return result.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return result.decode('shift-jis')
                    except UnicodeDecodeError:
                        return result.decode('cp932', errors='replace')
            elif isinstance(result, dict):
                return {msg_unpack(k) if isinstance(k, bytes) else k: 
                        msg_unpack(v) if isinstance(v, bytes) else v 
                        for k, v in result.items()}
            elif isinstance(result, list):
                return [msg_unpack(item) if isinstance(item, bytes) else item 
                        for item in result]
            else:
                return result
        except Exception:
            # 如果所有尝试都失败，返回原始数据
            return data


def msg_pack(data):
    serialized = packb(data, use_single_float=True, use_bin_type=True)
    return serialized, len(serialized)


def get_png_length(png_data, orig=0):
    idx = orig
    assert png_data[idx : idx + 8] == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"

    idx += 8
    while True:
        chunk_len = struct.unpack(">I", png_data[idx : idx + 4])[0]
        chunk_type = png_data[idx + 4 : idx + 8].decode()
        idx += chunk_len + 12
        if chunk_type == "IEND":
            break
    return idx - orig


def get_png(data_stream):
    origin_pos = data_stream.tell()
    assert data_stream.read(8) == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"
    while True:
        length = load_type(data_stream, ">I")
        chunk_type = data_stream.read(4)
        data_stream.read(length + 4)
        if chunk_type == b"IEND":
            break
    end_pos = data_stream.tell()
    data_stream.seek(origin_pos)
    png_data = data_stream.read(end_pos - origin_pos)
    return png_data
