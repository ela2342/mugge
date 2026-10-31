"""Unit tests for the virtual-stack gate guard (F-394, AE Q2 C1).

The service-integration mute tests open the D-063 gate. That is only
allowed in the local-demo stack with no ALSA hardware in its graph. These
tests pin the refusal, so a Pi run (PI_AUDIO_BACKEND=pi-*) or a stack with
a real sound card can never get the gate opened.
"""

import sys
from pathlib import Path

import pytest

_tests_dir = str(Path(__file__).resolve().parent.parent)
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

from fixtures.backend import virtual_stack_refusal  # noqa: E402


def _node(**props):
    return {"id": 1, "type": "PipeWire:Interface:Node", "info": {"props": props}}


# The local-demo graph: a null-sink source and a filter-chain node, both
# named after the real USBStreamer.
LOCAL_DEMO_GRAPH = [
    _node(**{"factory.name": "support.null-audio-sink",
             "node.name": "alsa_input.usb-MiniDSP_USBStreamer",
             "media.class": "Audio/Source"}),
    _node(**{"node.name": "alsa_output.usb-MiniDSP_USBStreamer-local-demo",
             "media.class": "Audio/Sink"}),
]


def test_local_demo_graph_is_allowed():
    assert virtual_stack_refusal("local-demo", LOCAL_DEMO_GRAPH) is None


@pytest.mark.parametrize("backend", ["pi-loopback", "pi-full", "", "mock"])
def test_non_local_demo_backend_refuses(backend):
    assert virtual_stack_refusal(backend, LOCAL_DEMO_GRAPH) is not None


def test_empty_graph_refuses():
    # pw-dump failed or saw nothing: cannot prove there is no hardware.
    assert virtual_stack_refusal("local-demo", []) is not None


@pytest.mark.parametrize("props", [
    {"factory.name": "api.alsa.pcm.sink", "node.name": "anything"},
    {"device.api": "alsa", "device.name": "alsa_card.usb-MiniDSP"},
    {"api.alsa.path": "hw:2", "node.name": "virtual-looking-name"},
])
def test_alsa_object_refuses(props):
    graph = LOCAL_DEMO_GRAPH + [_node(**props)]
    assert virtual_stack_refusal("local-demo", graph) is not None
