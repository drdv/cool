class List {
  item: String;
  next: List;

  init(in_item: String, in_next: List): List {
    {
      item <- in_item;
      next <- in_next;
      self;
    }
  };

  flatten(): String {
    if (isvoid next) then
      item
    else
      item.concat(next.flatten())
    fi
  };

};

class Main {

  io: IO <- new IO;

  main(): Object {
    let
    hello: String <- "Hello ",
    world: String <- "world!\n",
    nil: List,
    list: List <-
      (new List).init(hello,
        (new List).init(world, nil))
    in
      io.out_string(list.flatten())
  };
};
