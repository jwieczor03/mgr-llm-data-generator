"""Bounded multipart reception and preliminary validation of a DDL bundle."""
from dataclasses import dataclass
from tempfile import SpooledTemporaryFile
from typing import AsyncIterable

from python_multipart import MultipartParser
from python_multipart.exceptions import MultipartParseError
from python_multipart.multipart import parse_options_header
from sqlglot import Dialect
from sqlglot.errors import TokenError


@dataclass(frozen=True)
class InputLimits:
    max_files: int = 1024
    max_total_bytes: int = 64 * 1024 * 1024
    max_file_bytes: int = 64 * 1024 * 1024


class InputError(Exception):
    def __init__(self, code: str, details=None):
        self.code, self.details = code, details
        super().__init__(code)


def validate_metadata(files: list[dict], limits: InputLimits) -> None:
    if not files or len(files) > limits.max_files:
        raise InputError("DDL_LIMIT_EXCEEDED", {"max_files": limits.max_files}) if files else InputError("VALIDATION_ERROR")
    total = 0
    for item in files:
        name, size = item["name"], item["size_bytes"]
        if not name or name in (".", "..") or any(c in name for c in ("\x00", "/", "\\")):
            raise InputError("VALIDATION_ERROR")
        if size < 0:
            raise InputError("VALIDATION_ERROR")
        total += size
        if size > limits.max_file_bytes or total > limits.max_total_bytes:
            raise InputError("DDL_LIMIT_EXCEEDED", {"max_file_bytes": limits.max_file_bytes,
                                                    "max_total_bytes": limits.max_total_bytes})


def validate_content(files: list[tuple[str, bytes]]) -> list[dict]:
    diagnostics = []
    names: dict[str, list[int]] = {}
    tokenizer = Dialect.get_or_raise("postgres").tokenizer()
    for position, (name, content) in enumerate(files):
        names.setdefault(name.casefold(), []).append(position)
        try:
            sql = content.decode("utf-8-sig", errors="strict")
        except UnicodeDecodeError:
            diagnostics.append({"code": "DDL_INVALID_ENCODING", "file": name, "position": position})
            continue
        try:
            has_tokens = bool(tokenizer.tokenize(sql))
        except TokenError:
            # Lexical/syntax problems belong to the later DDL analysis, not input emptiness.
            has_tokens = True
        if not has_tokens:
            diagnostics.append({"code": "DDL_EMPTY_FILE", "file": name, "position": position})
    for positions in names.values():
        if len(positions) > 1:
            diagnostics.append({"code": "DDL_DUPLICATE_FILENAME", "positions": positions})
    return diagnostics


async def receive_multipart(content_type: str, stream: AsyncIterable[bytes], files: list[dict],
                            limits: InputLimits, check_active) -> list[tuple[str, bytes]]:
    """Read only after the caller has checked ownership and reserved the global slot."""
    media, options = parse_options_header(content_type)
    boundary = options.get(b"boundary")
    if media.lower() != b"multipart/form-data" or not boundary or len(boundary) > 200:
        raise InputError("VALIDATION_ERROR")
    received = []
    current = None
    total = 0
    header_name = bytearray()
    header_value = bytearray()
    headers = {}
    ended = False
    part_open = False

    def on_part_begin():
        nonlocal headers, current, part_open
        if part_open or len(received) >= len(files):
            raise InputError("DDL_ATTEMPT_CONFLICT")
        headers, current, part_open = {}, None, True

    def on_header_field(data, start, end):
        header_name.extend(data[start:end])

    def on_header_value(data, start, end):
        header_value.extend(data[start:end])

    def on_header_end():
        key = bytes(header_name).lower()
        if key in headers:
            raise InputError("VALIDATION_ERROR")
        headers[key] = bytes(header_value)
        header_name.clear()
        header_value.clear()

    def on_headers_finished():
        nonlocal current
        disposition, params = parse_options_header(headers.get(b"content-disposition"))
        try:
            name = params[b"filename"].decode("utf-8")
        except (KeyError, UnicodeDecodeError):
            raise InputError("VALIDATION_ERROR") from None
        if disposition.lower() != b"form-data" or params.get(b"name") != b"files" or name != files[len(received)]["name"]:
            raise InputError("DDL_ATTEMPT_CONFLICT")
        current = SpooledTemporaryFile(max_size=1024 * 1024)

    def on_part_data(data, start, end):
        nonlocal total
        if current is None:
            raise InputError("VALIDATION_ERROR")
        length = end - start
        total += length
        if total > limits.max_total_bytes or current.tell() + length > limits.max_file_bytes:
            raise InputError("DDL_LIMIT_EXCEEDED", {"max_file_bytes": limits.max_file_bytes,
                                                    "max_total_bytes": limits.max_total_bytes})
        if current.tell() + length > files[len(received)]["size_bytes"]:
            raise InputError("DDL_ATTEMPT_CONFLICT")
        current.write(data[start:end])

    def on_part_end():
        nonlocal current, part_open
        if current is None or current.tell() != files[len(received)]["size_bytes"]:
            raise InputError("DDL_ATTEMPT_CONFLICT")
        current.seek(0)
        received.append((files[len(received)]["name"], current.read()))
        current.close()
        current = None
        part_open = False

    def on_end():
        nonlocal ended
        ended = True

    callbacks = {"on_part_begin": on_part_begin, "on_header_field": on_header_field,
                 "on_header_value": on_header_value, "on_header_end": on_header_end,
                 "on_headers_finished": on_headers_finished, "on_part_data": on_part_data,
                 "on_part_end": on_part_end, "on_end": on_end}
    parser = MultipartParser(boundary, callbacks)
    try:
        async for chunk in stream:
            await check_active()
            if parser.write(chunk) != len(chunk):
                raise InputError("VALIDATION_ERROR")
        parser.finalize()
        if not ended or part_open or len(received) != len(files):
            raise InputError("DDL_ATTEMPT_CONFLICT")
        return received
    except MultipartParseError:
        raise InputError("VALIDATION_ERROR") from None
    finally:
        if current is not None:
            current.close()
