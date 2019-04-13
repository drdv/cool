"""Utests for :class:`~automaton.Automaton` class."""
from os.path import join
import sys
import unittest
import logging

sys.path.append('..')
from automaton import State, Automaton
import utils

class TestAutomaton(unittest.TestCase):
    """Utests for :class:`~automaton.Automaton` class."""

    def setUp(self):
        """Define data and setup environment."""
        # disable logging at all levels
        logging.disable(logging.CRITICAL)

    def test_1(self):
        """Example 1.35, p. 52.
        Michael Sipser, Introduction to the theory of computation, 3-rd ed.
        """
        q1, q2, q3 = map(State, ['q1', 'q2', 'q3'])

        q1.add_transition('b', q2)
        q1.add_transition('$', q3)
        q2.add_transition('a', [q2, q3])
        q2.add_transition('b', q3)
        q3.add_transition('a', q1)

        M = Automaton('M', [q1, q2, q3], ['a', 'b'], q1, [q1])

        self.assertListEqual(M.active_states, [q1, q3])
        M.transition('b')
        self.assertListEqual(M.active_states, [q2])
        M.transition('a')
        self.assertListEqual(M.active_states, [q2, q3])
        M.transition('b')
        self.assertListEqual(M.active_states, [q3])
        M.transition('a')
        self.assertListEqual(M.active_states, [q1, q3])
        self.assertTrue(M.is_accepted())

        M.reset()

        self.assertListEqual(M.active_states, [q1, q3])
        M.transition('b')
        self.assertListEqual(M.active_states, [q2])
        M.transition('a')
        self.assertListEqual(M.active_states, [q2, q3])
        M.transition('b')
        self.assertListEqual(M.active_states, [q3])
        M.transition('b')
        self.assertListEqual(M.active_states, [])
        M.transition('a')
        self.assertListEqual(M.active_states, [])
        self.assertTrue(not M.is_accepted())

    def test_2(self):
        """Example 1.30, p. 51 (extension with epsilon transitions).
        Michael Sipser, Introduction to the theory of computation, 3-rd ed.
        """
        q1, q2, q3, q4 = map(State, ['q1', 'q2', 'q3', 'q4'])

        q1.add_transition('1', [q1, q2])
        q1.add_transition('0', q1)
        q2.add_transition('0', q3)
        q2.add_transition('1', q3)
        q2.add_transition('$', q3)
        q3.add_transition('0', q4)
        q3.add_transition('1', q4)
        q3.add_transition('$', q4)

        M = Automaton('M', [q1, q2, q3, q4], ['0', '1'], q1, [q4])

        self.assertListEqual(M.active_states, [q1])
        M.transition('0')
        self.assertListEqual(M.active_states, [q1])
        M.transition('1')
        self.assertListEqual(M.active_states, [q1, q2, q3, q4])
        M.transition('0')
        self.assertListEqual(M.active_states, [q1, q3, q4])
        M.transition('0')
        self.assertListEqual(M.active_states, [q1, q4])
        M.transition('1')
        self.assertListEqual(M.active_states, [q1, q2, q3, q4])
        M.transition('0')
        self.assertListEqual(M.active_states, [q1, q3, q4])
        M.transition('0')
        self.assertListEqual(M.active_states, [q1, q4])

        self.assertTrue(M.is_accepted())

    def test_nfa_nfa_1(self):
        """Convertion from NFA to DFA."""
        q1, q2, q3 = map(State, ['q1', 'q2', 'q3'])

        q1.add_transition('b', q2)
        q1.add_transition('$', q3)
        q2.add_transition('a', [q2, q3])
        q2.add_transition('b', q3)
        q3.add_transition('a', q1)

        M = Automaton('M', [q1, q2, q3], ['a', 'b'], q1, [q1])
        D = M.to_dfa()

        self.assertTrue('q1' in D.Q[0].ready)
        self.assertTrue('q3' in D.Q[0].ready)
        self.assertEqual(len(D.Q[0].ready), 2)

        self.assertTrue('q2' in D.Q[1].ready)
        self.assertEqual(len(D.Q[1].ready), 1)

        self.assertTrue('q2' in D.Q[2].ready)
        self.assertTrue('q3' in D.Q[2].ready)
        self.assertEqual(len(D.Q[2].ready), 2)

        self.assertTrue('q3' in D.Q[3].ready)
        self.assertEqual(len(D.Q[3].ready), 1)

        self.assertTrue('q1' in D.Q[4].ready)
        self.assertTrue('q2' in D.Q[4].ready)
        self.assertTrue('q3' in D.Q[4].ready)
        self.assertEqual(len(D.Q[4].ready), 3)

        self.assertEqual(len(D.Q[5].ready), 0)

class TestUtils(unittest.TestCase):
    """Utests for utils."""

    def setUp(self):
        """Define data and setup environment."""
        # disable logging at all levels
        logging.disable(logging.CRITICAL)

    def test_infix2postfix_1(self):
        """Test infix2postfix."""
        infix = '(a+b)*(a+c)+a+b*c'
        self.assertEqual(utils.infix2postfix(infix), 'ab+ac+*a+bc*+')

    def test_infix2postfix_2(self):
        """Test infix2postfix."""
        infix = utils.add_explicit_concatenation('a|b*abb')
        postfix = utils.infix2postfix(infix,
                                      priority={'*': 2, '.': 1, '|': 0})

        self.assertEqual(postfix, 'ab*a.b.b.|')

    def test_postfix_eval(self):
        """Test postfix_eval."""
        def op_apply(op, x, y):
            if op == '*': return int(x) * int(y)
            elif op == '+': return int(x) + int(y)

        postfix = utils.infix2postfix('((2 + 3) * (4 + 5) + 1)*2 + 1')
        self.assertEqual(utils.postfix_eval(postfix, op_apply), 93)

    def test_explicit_concatenation(self):
        """Test adding explicit concatenation."""
        self.assertEqual(utils.add_explicit_concatenation('a|b*abb'),
                         'a|b*.a.b.b')

        self.assertEqual(utils.add_explicit_concatenation('a|b*ab.b'),
                         'a|b*.a.b.b')
