# Project rules

## Project
Protocol emulator ASIC for the Jane Street x Tiny Tapeout competition.
- Process: IHP 130nm CMOS5L, 6x4 tiles, 50 MHz clock
- Deadline: Jan 18, 2027
- Solo project; the author is learning RTL.

## Layout
- RTL: `src/` (top module `src/project.v`, UART TX in `src/uart_tx.v`)
- Tests: cocotb in `test/` (`test.py`, `tb.v`)

## Running tests
- `cd test && make -B`
- Waveforms: `test/tb.fst`

## Pins
- `uio[7:0]` is the protocol bus (only pins with output enables).
- `ui_in` / `uo_out` are the host interface.

## Working rules
- Do not edit RTL in `src/` unless explicitly asked. Explain proposed changes first; the author wants to understand every line.
- Write tests from the spec, not by reading the RTL.
- Synthesizable Verilog only: no latches, synchronous reset, single clock domain.
- After changes, run the tests and report results honestly, including failures.
- Do not commit or push. The author handles git.
