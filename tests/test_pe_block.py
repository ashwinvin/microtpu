from pathlib import Path
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer
from cocotb_tools.runner import get_runner


def dec(num):
    return int(str(num), 2)


async def rest_dut(dut):
    dut.rst.value = 1
    await Timer(5, unit="ns")
    dut.rst.value = 0
    await Timer(5, unit="ns")


@cocotb.test
async def test_pe_block(dut):
    clk = Clock(dut.clk, 5, "ns")
    clk.start()

    await Timer(5, unit="ns")
    await rest_dut(dut)
    assert int(dut.current_state.value) == 0  # IDLE

    dut.el_exhst.value = 0
    dut.i_ready.value = 1
    await Timer(5, "ns")

    assert int(dut.current_state.value) == 1  # PROCESS

    acc = 0
    for i in range(1, 3):
        dut.i_north.value = i
        dut.i_west.value = i + 2
        acc += i * (i + 2)
        await Timer(5, "ns")

    dut.el_exhst.value = 1
    dut.i_ready.value = 0
    dut.i_north.value = 0
    dut.i_west.value = 5

    await Timer(10, "ns")
    assert int(dut.current_state.value) == 2  # FLUSH

    cocotb.log.info("RESULT: %s, Golden model: %s", dec(dut.o_east.value), acc)
    assert dec(dut.o_east.value) == acc

    await Timer(5, "ns")
    cocotb.log.info("Flushed value: %s, Actual: 5", dec(dut.o_east.value))

    dut.el_exhst.value = 0
    await Timer(5, "ns")
    assert int(dut.current_state.value) == 0  # IDLE


def test_pe_block_runner():
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "tests"))

    sources = [proj_path / "hdl" / "pe_block.sv"]

    runner = get_runner("verilator")

    runner.build(
        sources=sources,
        hdl_toplevel="pe_block",
        always=True,
    )

    runner.test(hdl_toplevel="pe_block", test_module="test_pe_block")
