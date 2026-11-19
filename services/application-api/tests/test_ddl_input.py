import asyncio

import pytest
from application_api.ddl_input import (
    InputError,
    InputLimits,
    receive_multipart,
    validate_content,
    validate_metadata,
)


def test_content_reports_all_categories_and_preserves_literals():
    errors = validate_content([("a.sql", b"\xef\xbb\xbf -- comment\n/* x */"), ("A.SQL", b"\xff"),
                               ("ok.sql", b"SELECT '--not comment';")])
    assert {error["code"] for error in errors} == {"DDL_EMPTY_FILE", "DDL_INVALID_ENCODING", "DDL_DUPLICATE_FILENAME"}
    assert validate_content([("x.sql", b"SELECT '/* not comment */';")]) == []


def test_metadata_bounds_and_names():
    limits = InputLimits(max_files=2, max_total_bytes=5, max_file_bytes=4)
    validate_metadata([{"name": "a", "size_bytes": 4}, {"name": "A", "size_bytes": 1}], limits)
    for files, code in [([{"name": "../x", "size_bytes": 1}], "VALIDATION_ERROR"),
                        ([{"name": "x", "size_bytes": 5}], "DDL_LIMIT_EXCEEDED")]:
        with pytest.raises(InputError, match=code):
            validate_metadata(files, limits)


def run(data, expected, limits=InputLimits()):
    async def stream():
        for offset in range(0, len(data), 3):
            yield data[offset:offset + 3]
    async def check():
        pass
    return asyncio.run(receive_multipart("multipart/form-data; boundary=abc", stream(), expected, limits, check))


def test_streamed_multipart_and_incomplete():
    body = b'--abc\r\nContent-Disposition: form-data; name="files"; filename="x.sql"\r\n\r\nSELECT 1\r\n--abc--\r\n'
    meta = [{"name": "x.sql", "size_bytes": 8}]
    assert run(body, meta) == [("x.sql", b"SELECT 1")]
    with pytest.raises(InputError, match="DDL_ATTEMPT_CONFLICT"):
        run(body[:-9], meta)
    with pytest.raises(InputError, match="DDL_LIMIT_EXCEEDED"):
        run(body, meta, InputLimits(max_file_bytes=7))
    with pytest.raises(InputError, match="DDL_ATTEMPT_CONFLICT"):
        run(body, [{"name": "other", "size_bytes": 8}])
