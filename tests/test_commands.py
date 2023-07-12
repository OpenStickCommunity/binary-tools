"""Test our tools themselves to make sure they adhere to certain flags."""
import json
import os
import sys
from subprocess import run

from decorator import decorator

from gp2040ce_bintools import __version__

HERE = os.path.dirname(os.path.abspath(__file__))


@decorator
def with_pb2s(test, *args, **kwargs):
    """Wrap a test with precompiled pb2 files on the path."""
    proto_path = os.path.join(HERE, 'test-files', 'pb2-files')
    sys.path.append(proto_path)

    test(*args, **kwargs)

    sys.path.pop()
    del sys.modules['config_pb2']


def test_version_flag():
    """Test that tools report the version."""
    result = run(['visualize-storage', '-v'], capture_output=True, encoding='utf8')
    assert __version__ in result.stdout


def test_help_flag():
    """Test that tools report the usage information."""
    result = run(['visualize-storage', '-h'], capture_output=True, encoding='utf8')
    assert 'usage: visualize-storage' in result.stdout
    assert 'Read the configuration section from a dump of a GP2040-CE board' in result.stdout


def test_concatenate_invocation(tmpdir):
    """Test that a normal invocation against a dump works."""
    out_filename = os.path.join(tmpdir, 'out.bin')
    _ = run(['concatenate', 'tests/test-files/test-firmware.bin', 'tests/test-files/test-storage-area.bin',
             '--new-binary-filename', out_filename])
    with open(out_filename, 'rb') as out_file, open('tests/test-files/test-storage-area.bin', 'rb') as storage_file:
        out = out_file.read()
        storage = storage_file.read()
    assert out[2088960:2097152] == storage


def test_storage_dump_invocation():
    """Test that a normal invocation against a dump works."""
    result = run(['visualize-storage', '-P', 'tests/test-files/proto-files',
                  '--filename', 'tests/test-files/test-storage-area.bin'],
                 capture_output=True, encoding='utf8')
    assert 'boardVersion: "v0.7.2"' in result.stdout


def test_debug_storage_dump_invocation():
    """Test that a normal invocation against a dump works."""
    result = run(['visualize-storage', '-d', '-P', 'tests/test-files/proto-files',
                  '--filename', 'tests/test-files/test-storage-area.bin'],
                 capture_output=True, encoding='utf8')
    assert 'boardVersion: "v0.7.2"' in result.stdout
    assert 'length of content to look for footer in: 8192' in result.stderr


def test_storage_dump_json_invocation():
    """Test that a normal invocation against a dump works."""
    result = run(['visualize-storage', '-P', 'tests/test-files/proto-files', '--json',
                  '--filename', 'tests/test-files/test-storage-area.bin'],
                 capture_output=True, encoding='utf8')
    to_dict = json.loads(result.stdout)
    assert to_dict['boardVersion'] == 'v0.7.2'
