# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge

CLKS_PER_BIT = 434  # 50 MHz / 115200 baud
EXPECTED_BYTE = 0x4A


async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())  # 50 MHz
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)


def tx(dut):
    return int(dut.uo_out.value) & 1


def busy(dut):
    return (int(dut.uo_out.value) >> 1) & 1


async def pulse_start(dut):
    dut.ui_in.value = 1
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0


async def receive_byte(dut):
    """Wait for the start bit's falling edge, then sample mid-bit."""
    while tx(dut) == 1:
        await RisingEdge(dut.clk)
    # First clock where tx is low = start of the start bit.
    await ClockCycles(dut.clk, CLKS_PER_BIT // 2)
    assert tx(dut) == 0, "start bit should be 0"
    value = 0
    for i in range(8):
        await ClockCycles(dut.clk, CLKS_PER_BIT)
        value |= tx(dut) << i  # LSB first
    await ClockCycles(dut.clk, CLKS_PER_BIT)
    assert tx(dut) == 1, "stop bit should be 1"
    return value


@cocotb.test()
async def test_idle_after_reset(dut):
    await reset(dut)
    for _ in range(50):
        assert tx(dut) == 1, "line must idle high"
        assert busy(dut) == 0
        await RisingEdge(dut.clk)


@cocotb.test()
async def test_send_byte(dut):
    await reset(dut)
    rx = cocotb.start_soon(receive_byte(dut))
    await pulse_start(dut)
    got = await rx
    assert got == EXPECTED_BYTE, f"got {got:#04x}, expected {EXPECTED_BYTE:#04x}"


@cocotb.test()
async def test_busy_and_frame_length(dut):
    await reset(dut)
    await pulse_start(dut)
    await RisingEdge(dut.clk)
    # Wait for busy to rise (at most a couple of clocks after the pulse).
    n = 0
    while busy(dut) == 0:
        await RisingEdge(dut.clk)
        n += 1
        assert n < 5, "busy never asserted"
    # Count how long busy stays high: 10 bits * 434 clocks.
    cycles = 0
    while busy(dut) == 1:
        await RisingEdge(dut.clk)
        cycles += 1
        assert cycles < 10 * CLKS_PER_BIT + 20, "busy stuck high"
    assert abs(cycles - 10 * CLKS_PER_BIT) <= 2, f"frame took {cycles} clocks"
    assert tx(dut) == 1, "line must be high after the frame"


@cocotb.test()
async def test_start_ignored_while_busy_then_resend(dut):
    await reset(dut)
    rx = cocotb.start_soon(receive_byte(dut))
    await pulse_start(dut)
    await ClockCycles(dut.clk, 3 * CLKS_PER_BIT)
    await pulse_start(dut)  # should be ignored mid-frame
    assert await rx == EXPECTED_BYTE
    # Wait until idle, send again, expect a clean second frame.
    while busy(dut):
        await RisingEdge(dut.clk)
    await ClockCycles(dut.clk, 20)
    rx2 = cocotb.start_soon(receive_byte(dut))
    await pulse_start(dut)
    assert await rx2 == EXPECTED_BYTE
