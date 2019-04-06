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
*)
class List {
  is_empty(): Bool { true };
  head() : Int { {abort(); 1;} };
  tail() : List { {abort(); self;} };
  cons(i: Int): List {
    (new Cons).init(i, self)
  };
};

class Cons inherits List {
  car : Int;
  cdr : List;
  init(i : Int, rest : List) : List {
    {
      car <- i;
      cdr <- rest;
      self;
    }
  };

  is_empty(): Bool { false };
  head() : Int { car };
  tail() : List { cdr };
};

class Main inherits IO {
  mylist : List;

  print_list(l : List) : Object {
    if (l.is_empty())
    then out_string("\n")
    else {
      out_int(l.head());
      out_string(" ");
      print_list(l.tail());
    }
    fi
  };

  main() : Object {
    {
      mylist <- (new List).cons(1).cons(2).cons(3).cons(4).cons(5);
      while (not mylist.is_empty()) loop
      {
        print_list(mylist);
        mylist <- mylist.tail();
      }
      pool;
    }
  };
};
