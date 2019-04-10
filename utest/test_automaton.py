"""Utests for :class:`~automaton.Automaton` class."""
from os.path import join
import sys
import unittest
import logging

sys.path.append('..')
from automaton import State, Automaton

class TestAutomaton(unittest.TestCase):
    """Perform utests for :class:`~automaton.Automaton` class."""

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
