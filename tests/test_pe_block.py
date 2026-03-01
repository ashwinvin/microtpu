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

    dut.w_shift.value = 1
    await Timer(5, "ns")

    dut.i_weight.value = 10

    await Timer(5, "ns")
    dut.i_weight.value = 5

    await Timer(5, "ns")
    assert int(dut.o_weight.value) == 10

    dut.w_shift.value = 0
    dut.pe_en.value = 1
    await Timer(5, "ns")

    dut.i_weight.value = 0 
    dut.i_psum.value = 0
    dut.i_input.value = 6
    await Timer(5, "ns")

    assert int(dut.o_psum.value) == 30
    dut.i_input.value = 0
    dut.pe_en.value = 0
    await Timer(10, "ns")

    assert int(dut.state.value) == 0  # IDLE


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
