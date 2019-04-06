class Main {
  io: IO <- new IO;

  (*
    Verify whether a string is a palindrome.
  *)
  palindrome(s: String): Bool {
    if s.length() < 2
    then true
    else
      if s.substr(0, 1) = s.substr(s.length()-1, 1)
      then palindrome(s.substr(1, s.length()-2))
      else
        false
      fi
    fi
  };

  main(): Object {
    {
      io.out_string("Enter a string:\n");
      if (palindrome(io.in_string()))
      then io.out_string("palindrome.\n")
      else io.out_string("NOT a palindrome.\n")
      fi;
    }
  };
};
