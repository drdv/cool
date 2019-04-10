"""Finate automaton implementation."""
from collections import defaultdict
import logging
log = logging.getLogger(__name__)

class State:
    """A state of a finate automaton."""
    def __init__(self, name):
        """Constructor.

        Parameters
        -----------
        name : :obj:`str`
            Name of the state.

        """
        self.name = name
        self.transitions = defaultdict(list)

        self.active = False
        self.newly_activated = False

    def is_active(self):
        return self.active

    def add_transition(self, letter, state):
        """Add a transition.

        Parameters
        -----------
        letter : :obj:`str`
            A letter from the alphabet of '$' (denoting an epsilon transition)

        state : :obj:`State` or :obj:`list(State)`
            A state or list of states.

        """
        if isinstance(state, list):
            self.transitions[letter].extend(state)
        else:
            self.transitions[letter].append(state)

    def _is_newly_activated(self):
        return self.newly_activated

    def _reset_new_activation(self):
        self.newly_activated = False

    def _activate(self):
        """Activate the state.

        In addition, recursively activate states reachable by epsilon transitions.
        """
        self.active = self.newly_activated = True
        log.info('activate: {}'.format(self.name))
        # it this check is not performed, '$' is added to the defaultdict transitions
        if '$' in self.transitions:
            for s in self.transitions['$']:
                s._activate()

    def _deactivate(self, where=None):
        """Deactivate the state."""
        self.active = self.newly_activated = False
        log.info('deactivate: {} ({})'.format(self.name, where))

    def __repr__(self):
        """Describe object."""
        out = '{}:\n'.format(self.name)
        for letter, states in self.transitions.items():
            out += ' {}: {}\n'.format(letter, [state.name for state in states])

        return out

    def _verify_alphabet(self, Sigma):
        """Verify that the letters in the transitions are contained in the alphabet.

        Parameters
        -----------
        Sigma : :obj:`list(str)`
            The alphabet.

        Returns
        --------
        `True` if letters are contained in Sigma else `False`

        """
        for letter in self.transitions.keys():
            if letter not in Sigma:
                return False

        return True

class Automaton:
    """A finate automaton.

    Note
    -----
    Can be used both as a nondeterministic or deterministic
    finate automaton (i.e., DFA, or NFA).
    """
    def __init__(self, name, Q, Sigma, q0, F):
        """Constructor.

        name : :obj:`str`
            Name of the automaton

        Q : :obj:`list(State)`
            List of states.

        Sigma : :obj:`list(str)`
            The alphabet.

        q0 : :obj:`State`
            Initial state.

        F : :obj:`list(State)`
            Accepting states.

        """
        self.name = name
        self.Q = Q
        self.Sigma = Sigma
        self.q0 = q0
        if not isinstance(F, list):
            raise ValueError('Accepted states should be a list.')
        self.F = F

        self._verify_states()

        self.q0._activate()
        self._reset_new_activations()

    def reset(self):
        """Reset the automaton."""
        for s in self.Q:
            s._deactivate()

        self.q0._activate()
        self._reset_new_activations()

    @property
    def active_states(self):
        """Return active stetas."""
        return [q for q in self.Q if q.is_active()]

    def transition(self, letter):
        """Perform a transition from the active states given a letter.

        letter : :obj:`str`
            A letter from :obj:`Sigma`.

        """
        log.info('transition with letter {}'.format(letter))
        self._deactivate_states(letter)
        for state in self.active_states:
            target_states = state.transitions[letter]
            if target_states and not state._is_newly_activated():
                state._deactivate('transition')

            log.info('[{}] {} target states: {}'.format(letter,
                                                        state.name,
                                                        [t.name for t in target_states]))
            for s in target_states:
                # prevent re-activating a state if it has been newly activated
                if not s._is_newly_activated():
                    s._activate()

        self._reset_new_activations()

    def is_accepted(self):
        """Return `True` if the automaton accepts the processed input."""
        A = self.active_states
        return any([True if s in A else False for s in self.F])

    def _reset_new_activations(self):
        """Reset new state activations (after a transition has been completed)."""
        for s in self.Q:
            s._reset_new_activation()

    def _deactivate_states(self, letter):
        """Deactivate states that don't have a transition with the current letter."""
        for s in self.active_states:
            if letter not in s.transitions:
                s._deactivate('_deactivate_states')

    def _verify_states(self):
        """Verify validity of states."""
        for s in self.Q:
            s._verify_alphabet(self.Sigma)

    def __repr__(self):
        """Describe object."""
        return '{}: {}'.format(self.name,
                               sorted([s.name for s in self.active_states]))
