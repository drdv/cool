(*
  Implement a list using only a Cons class.

  A void Cons is used to denote an empty list element,
  which is used to indicate the end of the list.
  The problem with this implmentation is that we
  cannot rely on a method cons_instance.is_empty()
  since cons_instance could be void (and we cannot
  have a dispatch with it). This leads to some
  inconveniences with initialization as well (see then
  two options in main()). What we need is an object
  that denotes an empty element. And this is precisely
  what is done in test_list3.cl (which is based on
  the original example in cooldist/examples/list.cl).
*)
class Cons {
  car : Int;
  cdr : Cons;

  head() : Int { car };
  tail() : Cons { cdr };
  init(i : Int, rest : Cons) : Cons {
    {
      car <- i;
      cdr <- rest;
      self;
    }
  };

  cons(i: Int): Cons {
    (new Cons).init(i, self)
  };
};

class Main inherits IO {
  mylist : Cons;
  nil: Cons; -- do not initialize

  print_list(l : Cons) : Object {
    if (isvoid l)
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
      -- initialize in two different ways
      if true
      then mylist <- (new Cons).init(1, nil).cons(2).cons(3).cons(4).cons(5)
      else mylist <-
        (new Cons).init(1,
          (new Cons).init(2,
            (new Cons).init(3,
              (new Cons).init(4,
                (new Cons).init(5, nil)))))
      fi;

      while (not isvoid mylist) loop
      {
        print_list(mylist);
        mylist <- mylist.tail();
      }
      pool;
    }
  };
};
