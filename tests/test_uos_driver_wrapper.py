"""
tests/test_uos_driver_wrapper.py
=================================
Unit tests for UOS/driver_wrapper.py.

Covers:
  - HardwareChannel: construction, invalid device_type, latency clamp
  - DriverWrapper: register_device, translate, execute, channel_latencies, stats
  - _kk_projection_matrix: shape and content
  - Error paths: invalid channel_id, invalid resource_class
"""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from UOS.driver_wrapper import (
    HardwareChannel,
    DriverWrapper,
    RESOURCE_CLASSES,
    INTENT_DIM,
    SIGNAL_DIM,
)
from UOS.constants import UOS_DRIVER_CHANNELS, PHI_BACKGROUND, LAMBDA_COUPLING


# ---------------------------------------------------------------------------
# HardwareChannel
# ---------------------------------------------------------------------------

class TestHardwareChannel:
    def test_construction(self):
        ch = HardwareChannel(channel_id=0, device_type="cpu")
        assert ch.channel_id == 0
        assert ch.device_type == "cpu"

    def test_invalid_device_type_raises(self):
        with pytest.raises(ValueError):
            HardwareChannel(channel_id=0, device_type="quantum")

    def test_latency_clamped_high(self):
        ch = HardwareChannel(channel_id=0, device_type="cpu", latency=5.0)
        assert ch.latency == 1.0

    def test_latency_clamped_low(self):
        ch = HardwareChannel(channel_id=0, device_type="cpu", latency=-1.0)
        assert ch.latency == 0.0

    def test_all_resource_classes_valid(self):
        for i, rc in enumerate(RESOURCE_CLASSES):
            ch = HardwareChannel(channel_id=i, device_type=rc)
            assert ch.device_type == rc


# ---------------------------------------------------------------------------
# DriverWrapper — construction
# ---------------------------------------------------------------------------

class TestDriverWrapperConstruction:
    def test_default_channels(self):
        dw = DriverWrapper()
        assert dw.n_channels == UOS_DRIVER_CHANNELS

    def test_empty_channels_on_init(self):
        dw = DriverWrapper()
        assert len(dw._channels) == 0


# ---------------------------------------------------------------------------
# DriverWrapper — register_device
# ---------------------------------------------------------------------------

class TestRegisterDevice:
    def test_register_returns_channel(self):
        dw = DriverWrapper()
        ch = dw.register_device(0, "cpu")
        assert isinstance(ch, HardwareChannel)

    def test_register_stores_channel(self):
        dw = DriverWrapper()
        dw.register_device(5, "memory")
        assert 5 in dw._channels

    def test_register_invalid_channel_id_raises(self):
        dw = DriverWrapper()
        with pytest.raises(ValueError):
            dw.register_device(-1, "cpu")

    def test_register_out_of_range_raises(self):
        dw = DriverWrapper(n_channels=4)
        with pytest.raises(ValueError):
            dw.register_device(4, "cpu")

    def test_register_custom_latency(self):
        dw = DriverWrapper()
        ch = dw.register_device(0, "gpu", latency=0.3)
        assert abs(ch.latency - 0.3) < 1e-9


# ---------------------------------------------------------------------------
# DriverWrapper — translate
# ---------------------------------------------------------------------------

class TestTranslate:
    def test_signal_4d_shape(self):
        dw = DriverWrapper()
        dw.register_device(0, "cpu")
        intent = np.array([1.0, 0.5, 0.0, 0.0, 0.0])
        result = dw.translate(intent, "cpu")
        assert result["signal_4d"].shape == (SIGNAL_DIM,)

    def test_result_keys(self):
        dw = DriverWrapper()
        dw.register_device(0, "memory")
        intent = np.zeros(INTENT_DIM)
        result = dw.translate(intent, "memory")
        assert "signal_4d" in result
        assert "channel_id" in result
        assert "resource_class" in result
        assert "phi_scale" in result

    def test_invalid_resource_class_raises(self):
        dw = DriverWrapper()
        with pytest.raises(ValueError):
            dw.translate(np.zeros(INTENT_DIM), "quantum")

    def test_no_channel_returns_minus_one(self):
        dw = DriverWrapper()
        # No cpu channel registered
        result = dw.translate(np.ones(INTENT_DIM), "cpu")
        assert result["channel_id"] == -1

    def test_zero_intent_gives_zero_signal(self):
        dw = DriverWrapper()
        dw.register_device(0, "cpu", phi_scale=1.0)
        intent = np.zeros(INTENT_DIM)
        result = dw.translate(intent, "cpu")
        np.testing.assert_array_almost_equal(result["signal_4d"], 0.0)

    def test_phi_scale_affects_signal(self):
        dw = DriverWrapper()
        dw.register_device(0, "cpu", phi_scale=2.0)
        intent = np.ones(INTENT_DIM)
        result = dw.translate(intent, "cpu")
        assert result["phi_scale"] == 2.0
        assert np.any(result["signal_4d"] != 0.0)

    def test_intent_resize(self):
        """Short intent vector is resized to INTENT_DIM."""
        dw = DriverWrapper()
        dw.register_device(0, "cpu")
        short_intent = np.ones(2)
        result = dw.translate(short_intent, "cpu")
        assert result["signal_4d"].shape == (SIGNAL_DIM,)


# ---------------------------------------------------------------------------
# DriverWrapper — execute
# ---------------------------------------------------------------------------

class TestExecute:
    def test_execute_dispatched_status(self):
        dw = DriverWrapper()
        dw.register_device(0, "cpu", latency=0.05)
        result = dw.execute(np.ones(INTENT_DIM), "cpu")
        assert result["status"] == "dispatched"

    def test_execute_no_channel_status(self):
        dw = DriverWrapper()
        result = dw.execute(np.ones(INTENT_DIM), "gpu")
        assert result["status"] == "no_channel"

    def test_execute_increments_dispatch_count(self):
        dw = DriverWrapper()
        dw.register_device(0, "cpu")
        dw.execute(np.ones(INTENT_DIM), "cpu")
        dw.execute(np.ones(INTENT_DIM), "cpu")
        assert dw._dispatch_count == 2

    def test_execute_result_keys(self):
        dw = DriverWrapper()
        dw.register_device(0, "storage")
        result = dw.execute(np.zeros(INTENT_DIM), "storage")
        for key in ("status", "signal_4d", "channel_id", "latency", "dispatch_count"):
            assert key in result

    def test_execute_lowest_latency_channel_selected(self):
        dw = DriverWrapper(n_channels=10)
        dw.register_device(0, "cpu", latency=0.8)
        dw.register_device(1, "cpu", latency=0.1)
        result = dw.execute(np.ones(INTENT_DIM), "cpu")
        assert result["channel_id"] == 1  # lowest latency


# ---------------------------------------------------------------------------
# DriverWrapper — channel_latencies
# ---------------------------------------------------------------------------

class TestChannelLatencies:
    def test_empty_latencies(self):
        dw = DriverWrapper()
        assert dw.channel_latencies() == {}

    def test_latency_values(self):
        dw = DriverWrapper()
        dw.register_device(0, "cpu", latency=0.2)
        dw.register_device(1, "gpu", latency=0.5)
        lat = dw.channel_latencies()
        assert abs(lat[0] - 0.2) < 1e-9
        assert abs(lat[1] - 0.5) < 1e-9


# ---------------------------------------------------------------------------
# DriverWrapper — stats
# ---------------------------------------------------------------------------

class TestStats:
    def test_stats_keys(self):
        dw = DriverWrapper()
        s = dw.stats()
        assert "registered_channels" in s
        assert "total_channels" in s
        assert "dispatch_count" in s
        assert "average_latency" in s
        assert "channels_by_type" in s

    def test_stats_total_channels(self):
        dw = DriverWrapper(n_channels=10)
        assert dw.stats()["total_channels"] == 10

    def test_stats_registered_channels(self):
        dw = DriverWrapper()
        dw.register_device(0, "cpu")
        dw.register_device(1, "gpu")
        assert dw.stats()["registered_channels"] == 2

    def test_stats_dispatch_count_zero(self):
        dw = DriverWrapper()
        assert dw.stats()["dispatch_count"] == 0

    def test_stats_channels_by_type(self):
        dw = DriverWrapper()
        dw.register_device(0, "cpu")
        dw.register_device(1, "cpu")
        dw.register_device(2, "gpu")
        by_type = dw.stats()["channels_by_type"]
        assert by_type["cpu"] == 2
        assert by_type["gpu"] == 1


# ---------------------------------------------------------------------------
# _kk_projection_matrix
# ---------------------------------------------------------------------------

class TestKKProjectionMatrix:
    def test_shape(self):
        P = DriverWrapper._kk_projection_matrix(1.0)
        assert P.shape == (INTENT_DIM, SIGNAL_DIM)

    def test_identity_block(self):
        P = DriverWrapper._kk_projection_matrix(1.0)
        np.testing.assert_array_almost_equal(P[:SIGNAL_DIM, :], np.eye(SIGNAL_DIM))

    def test_fifth_row_coupling(self):
        phi = 2.0
        P = DriverWrapper._kk_projection_matrix(phi)
        expected_5th_row = np.full(SIGNAL_DIM, LAMBDA_COUPLING * phi)
        np.testing.assert_array_almost_equal(P[SIGNAL_DIM, :], expected_5th_row)

    def test_phi_zero_gives_zero_fifth_row(self):
        P = DriverWrapper._kk_projection_matrix(0.0)
        np.testing.assert_array_almost_equal(P[SIGNAL_DIM, :], 0.0)
