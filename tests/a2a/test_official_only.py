import os
import pathlib

def test_no_custom_proto_files():
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    protos = list(repo_root.rglob("*.proto"))
    # No custom protos allowed in this repository per official A2A channel requirement
    assert len(protos) == 0
