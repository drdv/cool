(*
  Factorial example.
*)
class Main {

  str: A2I <- new A2I;
  io: IO <- new IO;

  -- Compute factorial using a recursion.
  fact(x: Int): Int {
    if x = 0 then 1 else x * fact(x-1) fi
  };

  -- Compute factorial using a loop.
  fact_loop(x: Int): Int {
    let a: Int <- 1 in {
      while (not x = 0) loop {
        a <- a * x;
        x <- x - 1;
      }
      pool;
      a;
    }
  };

  main(): Object {
    let
    n: Int <- 6
    in
    io.out_string("factorial of ".
      concat(str.i2a(n)).
      concat(" is ").
      concat(str.i2a(fact_loop(n))).
      concat("\n"))
  };
};
