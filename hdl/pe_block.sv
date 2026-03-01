module pe_block #(parameter N_WIDTH=8)
  (
    input logic clk,
    input logic rst,
    input logic pe_en,
    input logic w_shift,
    input logic signed [N_WIDTH-1:0] i_input,
    input logic signed [N_WIDTH-1:0] i_weight,
    input logic signed [N_WIDTH-1:0] i_psum,
    output logic signed [N_WIDTH-1:0] o_input,
    output logic signed [N_WIDTH-1:0] o_weight,
    output logic signed [N_WIDTH-1:0] o_psum
  );

  logic signed [N_WIDTH-1:0] weight;

  typedef enum logic [2:0] {IDLE, LOAD_WEIGHT, PROCESS} state_t;

  state_t state;

  always @(posedge clk or posedge rst)
  begin
    o_weight <= 0;

    if (rst)
    begin
      state <= IDLE;
      weight <= {N_WIDTH{1'b0}};
    end
    case (state)
      IDLE:
      begin
        if (w_shift)
          state <= LOAD_WEIGHT;

        weight <= {N_WIDTH{1'b0}};
        o_weight <= {N_WIDTH{1'b0}};
        o_psum <= {N_WIDTH{1'b0}};
        o_input <= {N_WIDTH{1'b0}};
      end

      LOAD_WEIGHT:
      begin
        if (pe_en)
          state <= PROCESS;

        weight <= i_weight;
        o_weight <= weight;
      end

      PROCESS:
      begin
        if (pe_en == 1'b0)
          state <= IDLE;

        o_weight <= {N_WIDTH{1'b0}};
        o_psum <= i_psum + weight * i_input;
        o_input <= i_input;
      end

      default:
        state <= IDLE;
    endcase
  end

endmodule
