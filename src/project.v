/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_pepito (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire tx;
  wire busy;

  // ui_in[0] pulse sends the fixed byte 0x4A
  uart_tx uart (
      .clk  (clk),
      .rst_n(rst_n),
      .start(ui_in[0]),
      .data (8'h4A),
      .tx   (tx),
      .busy (busy)
  );

  assign uo_out  = {6'b0, busy, tx};  // uo_out[0] = tx, uo_out[1] = busy
  assign uio_out = 0;
  assign uio_oe  = 0;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, ui_in[7:1], uio_in, 1'b0};

endmodule
