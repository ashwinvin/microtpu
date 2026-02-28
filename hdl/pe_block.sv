module pe_block(
    input logic clk,
    input logic rst,
    input logic el_exhst,
    input logic i_ready,
    input logic signed [7:0] i_north,
    input logic signed [7:0] i_west,
    output logic signed [7:0] o_south,
    output logic signed [7:0] o_east
  );

  logic signed [7:0] acc;

  typedef enum logic [3:0]{
            IDLE,
            PROCESS,
            FLUSH
          } fsm_t;

  fsm_t current_state;


  always @(posedge clk or posedge rst)
  begin

    if (rst)
    begin
      current_state <= IDLE;
    end

    case (current_state)
      IDLE: begin
        if (i_ready)
            current_state <= PROCESS;

        o_south <= {8{1'b0}};
        o_east <= {8{1'b0}};
        acc <= 8'b0;   
      end

      PROCESS: begin 
        if (el_exhst)
          current_state <= FLUSH;

        o_east <= i_west;
        o_south <= i_north;
        acc <= acc + i_west * i_north;
      end

      FLUSH: begin
        if (el_exhst == 1'b0)
          current_state <= IDLE;

        acc <= i_west;
        o_east <= acc;
      end

      default:
        current_state <= IDLE;

    endcase
  end


endmodule
