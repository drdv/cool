(*
  A simple List class for testing COOL features.
*)
class List {
  item: Object;
  next: List;

  init(in_item: Object, in_next: List): List {
    {
      item <- in_item;
      next <- in_next;
      self;
    }
  };

  flatten(): String {
    let
    string: String <-
      case item of
        i: Int => (new A2I).i2a(i);
        s: String => s;
        o: Object => { abort(); ""; };
      esac
    in
      if (isvoid next) then
        string
      else
        string.concat(next.flatten())
      fi
  };
};

class Main {
  io: IO <- new IO;

  main(): Object {
    let
    hello: String <- "The ultimate ",
    world: String <- "answer is: ",
    number: Int <- 42,
    nil: List,
    list: List <-
      (new List).init(hello,
        (new List).init(world,
          (new List).init(number, nil)))
    in
      io.out_string(list.flatten().concat("\n"))
  };
};
