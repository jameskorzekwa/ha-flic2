"""Tests for the standalone Flic 2 protocol implementation."""

from __future__ import annotations

import struct

import pytest

from custom_components.flic2.protocol import (
    Flic2Session,
    NoPairingSlotsError,
    PairingData,
    PairingTimeoutError,
    SessionState,
    button_events_need_ack,
    chaskey_16,
    chaskey_signature,
    chaskey_subkeys,
    decode_button_events,
)


def _event_item(encoded: int, *, queued: bool = False, timestamp: int = 32768) -> bytes:
    raw = timestamp | (encoded << 48) | (int(queued) << 52)
    return raw.to_bytes(7, "little")


def test_chaskey_subkeys_are_deterministic() -> None:
    keys = chaskey_subkeys(bytes(range(16)))
    assert len(keys) == 12
    assert keys[:4] == (0x03020100, 0x07060504, 0x0B0A0908, 0x0F0E0D0C)
    assert chaskey_subkeys(bytes(range(16))) == keys


def test_chaskey_operations_have_expected_lengths_and_avalanche() -> None:
    key = bytes(range(16))
    block = bytes(range(16, 32))
    first = chaskey_16(key, block)
    second = chaskey_16(key, block[:-1] + bytes([block[-1] ^ 1]))
    assert len(first) == 16
    assert first != second
    signature = chaskey_signature(key, 1, 0x1122334455667788, bytes(range(37)))
    assert len(signature) == 5
    assert signature != chaskey_signature(key, 0, 0x1122334455667788, bytes(range(37)))


def test_decode_single_double_and_hold() -> None:
    payload = b"".join(
        [
            _event_item(0b1010),  # up + single
            _event_item(0b1011),  # up + double
            _event_item(0b0011),  # hold
        ]
    )
    events = decode_button_events(payload, 12)
    assert [event.event_type for event in events] == ["single", "double", "hold"]
    assert all(event.timestamp_ms == 1000 for event in events)
    assert button_events_need_ack(payload)


def test_plain_up_down_do_not_create_user_event() -> None:
    assert decode_button_events(_event_item(0) + _event_item(1), 2) == []
    assert not button_events_need_ack(_event_item(0) + _event_item(1))


@pytest.mark.asyncio
async def test_quick_verify_request_is_fragmented_for_default_mtu() -> None:
    writes: list[bytes] = []

    async def send(value: bytes) -> None:
        writes.append(value)

    session = Flic2Session(
        "01:02:03:04:05:06",
        send,
        pairing=PairingData(0x01020304, bytes(range(16))),
        mtu=23,
    )
    await session.start()
    assert session.state is SessionState.WAIT_QUICK_VERIFY
    assert len(writes) == 1
    assert writes[0][1] == 5
    assert writes[0][9] == 0  # Do not negotiate the unsupported Duo extension.
    assert struct.unpack_from("<I", writes[0], 14)[0] == 0x01020304


@pytest.mark.asyncio
async def test_no_pairing_slots_has_specific_error() -> None:
    writes: list[bytes] = []

    async def send(value: bytes) -> None:
        writes.append(value)

    session = Flic2Session("01:02:03:04:05:06", send)
    await session.start()
    temporary_id = struct.unpack_from("<I", writes[0], 2)[0]

    with pytest.raises(NoPairingSlotsError):
        await session.feed_gatt(bytes([0, 2]) + struct.pack("<I", temporary_id))


def test_pairing_timeout_preserves_protocol_state() -> None:
    error = PairingTimeoutError(SessionState.ESTABLISHED)

    assert error.state is SessionState.ESTABLISHED
    assert str(error) == "Timed out in protocol state ESTABLISHED"


def test_multiple_packet_notification() -> None:
    """The outer header is also the first packet header."""

    async def send(_: bytes) -> None:
        return None

    session = Flic2Session("AA:BB:CC:DD:EE:FF", send)
    value = bytes([0x40, 2, 0x10, 0x11, 0x01, 3, 0x20, 0x21, 0x22])

    assert session._defragment(value) == [
        (0x40, bytes([0x10, 0x11])),
        (0x01, bytes([0x20, 0x21, 0x22])),
    ]
