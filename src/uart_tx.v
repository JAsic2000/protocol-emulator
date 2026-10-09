/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * 8N1 UART transmitter. One frame = start(0), d0..d7 (LSB first), stop(1).
 */

`default_nettype none

module uart_tx #(
    parameter CLKS_PER_BIT = 434  // 50 MHz / 115200 baud
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       start,   // pulse: begin sending `data` (ignored while busy)
    input  wire [7:0] data,
    output wire       tx,
    output wire       busy
);

  reg        sending;  // 0 = IDLE, 1 = SEND (this is the whole state machine)
  reg [9:0]  shreg;    // {stop, d7..d0, start}; bit 0 is on the wire
  reg [8:0]  baud;     // counts clocks inside one bit: 0 .. CLKS_PER_BIT-1
  reg [3:0]  bitcnt;   // bits finished so far: 0 .. 9

  wire bit_done = (baud == CLKS_PER_BIT - 1);

  always @(posedge clk) begin
    if (!rst_n) begin
      sending <= 1'b0;
      shreg   <= 10'h3FF;  // all ones, so tx idles high
      baud    <= 9'd0;
      bitcnt  <= 4'd0;
    end else if (!sending) begin
      if (start) begin
        sending <= 1'b1;
        shreg   <= {1'b1, data, 1'b0};  // stop, data, start
        baud    <= 9'd0;
        bitcnt  <= 4'd0;
      end
    end else begin
      if (bit_done) begin
        baud  <= 9'd0;
        shreg <= {1'b1, shreg[9:1]};  // next bit to the wire, fill with 1s
        if (bitcnt == 4'd9) sending <= 1'b0;  // stop bit just finished
        else bitcnt <= bitcnt + 4'd1;
      end else begin
        baud <= baud + 9'd1;
      end
    end
  end

  assign tx   = shreg[0];
  assign busy = sending;

endmodule
