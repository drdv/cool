(*
  A list implementation.

  The List class implements an empty list element.
  It is specilized by the Cons class to handle non-
  empty elements. The dispatch is responsible for
  identifying whether we are dealing with an empty
  element of not. Note that (new List).cons(1) returns
  an instance of Cons that contains an empty list element
  in its cdr. Hence, when a recursion reaches this element
  it would hit on the base case.

  In addition, there is the possibility to:
   - reverse the list: using rev()
   - append elements: using rcons(element)
   - insert element at a place where element < car: insert(element)
   - sort the slit: sort()
*)
class List {
  io: IO <- new IO;

  is_empty(): Bool { true };
  head(): Int { {abort(); 1;} };
  tail(): List { {abort(); self;} };

  cons(i: Int): List {
    (new Cons).init(i, self)
  };

  rcons(i: Int): List {
    -- Append an element whose cdr points to the empty list.
    (new Cons).init(i, self)
  };

  rev(): List {
    -- Return the empty list which will be used in rcons()
    self
  };

  insert(i: Int): List {
    rcons(i)
  };

  sort(): List {
    self
  };

  print(): Object {
    io.out_string(" NULL \n")
  };
};

class Cons inherits List {
  car: Int;
  cdr: List;
  init(i: Int, rest: List): List {
    {
      car <- i;
      cdr <- rest;
      self;
    }
  };

  is_empty(): Bool { false };
  head(): Int { car };
  tail(): List { cdr };

  rcons(i: Int): List {
    -- Append element to list
    -- basically, postpone insertion until we hit the base case
     (new Cons).init(car, cdr.rcons(i))
   };

  rev(): List {
    -- Reverse the list.
    -- append the car to the reversed cdr
    -- the base returns an empty list and we do (empty list).rcons(car)
    (cdr.rev()).rcons(car)
  };

  insert(i: Int): List {
    if i < car
    then (new Cons).init(i, self)
    else (new Cons).init(car, cdr.insert(i))
    fi
  };

  sort(): List {
    -- Sort the list
    (cdr.sort()).insert(car)
  };

  print(): Object {
    {
      io.out_int(head());
      io.out_string(" -> ");
      tail().print();
    }
  };
};

class Main inherits IO {
  list: List;

  iota(start: Int, end: Int): List {
    -- Return a list with increasing values in the range [start, end).
      let
      l: List <- new List
      in {
        while start < end loop {
          end <- end - 1;
          l <- l.cons(end);
        }
        pool;
        l;
      }
  };

  main(): Object {
    {
      --list <- iota(1, 6);
      --list <- (new List).cons(1).cons(2).cons(3).cons(4).cons(5);
      --list <- (new List).rcons(1).rcons(2).rcons(3).rcons(4).rcons(5);
      --list <- (new List).insert(4).insert(5).insert(1).insert(3).insert(2);
      list <- (new List).rcons(4).rcons(5).rcons(1).rcons(3).rcons(2);

      out_string("original: ");
      list.print();

      out_string("reversed: ");
      list.rev().print();

      out_string("sorted  : ");
      list.sort().print();

      out_string("pop car :\n");
      while (not list.is_empty()) loop
      {
        list.print();
        list <- list.tail();
      }
      pool;
    }
  };
};
