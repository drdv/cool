"""Finate automaton implementation."""
import os
from collections import defaultdict
import subprocess
import logging

log = logging.getLogger(__name__)

class State:
    """A state of a finate automaton."""
    def __init__(self, name):
        """Constructor.

        Parameters
        -----------
        name : imutable object (e.g., :obj:`str`, :obj:`frozenset`)
            Name of the state.

        """
        self.name = name
        self.transitions = defaultdict(list)

        self.active = False
        self._newly_activated = False

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

    def epsilon_closure(self):
        """Return the epsilon closure of the state."""
        U = set([self])
        if '$' in self.transitions:
            U = U.union(set(self.transitions['$']))
            for s in self.transitions['$']:
                U = U.union(s.epsilon_closure())
            return U

        return U

    def _is_newly_activated(self):
        return self._newly_activated

    def _reset_new_activation(self):
        self._newly_activated = False

    def _activate(self):
        """Activate the state.

        In addition, recursively activate states reachable by epsilon transitions.
        """
        self.active = self._newly_activated = True
        log.info('activate: {}'.format(self.name))
        # if this check is not performed, '$' is added to the defaultdict transitions
        if '$' in self.transitions:
            for s in self.transitions['$']:
                s._activate()

    def _deactivate(self, where=None):
        """Deactivate the state."""
        self.active = self._newly_activated = False
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

        self.edges = self._identify_multiple_edges()

        self.q0._activate()
        self._reset_new_activations()

    def reset(self):
        """Reset the automaton."""
        for s in self.Q:
            s._deactivate()

        self.q0._activate()
        self._reset_new_activations()

    def epsilon_closure(self, states):
        """Compute the epsilon closure of the fiven states."""
        E = set()
        for s in states:
            E = E.union(s.epsilon_closure())

        return E

    def reachable_states(self, start_states, letter):
        """Return set of reachable states from start_states uppon a move letter."""
        if letter not in self.Sigma:
            raise ValueError('Unknown letter: {}'.format(letter))

        R = set()
        for s in start_states:
            if letter in s.transitions:
                R = R.union(s.transitions[letter])

        return R

    def to_dfa(self, summary=False):
        """Return an equivalent deterministic automaton.

        Parameters
        -----------
        summary : :obj:`str`
            Print summary if `True`.

        Note
        -----
        Clear example: Dragon book, Section 3.7.1.

        """
        if self.is_dfa():
            log.warning('The automaton is already deterministic.')
            return

        dfa_states = dict()

        E = self.q0.epsilon_closure()
        new_state = State('0'); new_state.ready = False
        dfa_states[frozenset(E)] = new_state

        to_process = [(key, state) for key, state in dfa_states.items()
                      if not state.ready]
        counter = 1
        while any(to_process):
            nfa_states, current_dfa_state = to_process[0]

            for letter in self.Sigma:
                E = self.epsilon_closure(self.reachable_states(nfa_states, letter))
                key = frozenset(E)
                if key not in dfa_states:
                    new_state = State(str(counter)); new_state.ready = False
                    dfa_states[key] = new_state
                    current_dfa_state.add_transition(letter, new_state)
                    counter += 1
                else:
                    current_dfa_state.add_transition(letter, dfa_states[key])

            current_dfa_state.ready = True
            to_process = [(key, state) for key, state in dfa_states.items()
                          if not state.ready]

        F = []
        for idx, (key, state) in enumerate(dfa_states.items()):
            state.ready = [k.name for k in key]  # store the corresponding dfa states
            if summary:
                print('{}: {}'.format(idx, state.ready))

            if any([f in key for f in self.F]):
                F.append(state)

        D = list(dfa_states.values())
        return Automaton('D', D, self.Sigma.copy(), D[0], F)

    def is_dfa(self):
        """Verify whether the automaton is deterministic."""
        for s in self.Q:
            if '$' in s.transitions:
                return False

            for letter in self.Sigma:
                if letter not in s.transitions:
                    return False

        return True

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

    def show_dot(self, filename=None, rankdir='LR'):
        """Display the dot diagram."""
        if filename is None:
            filename = '_fa.png'
        tmp_name, extension = os.path.splitext(os.path.basename(filename))
        extension = extension[1:]

        with open(tmp_name + '.dot', 'w') as h:
            h.write(self.to_dot(rankdir))

        subprocess.call(['dot',
                         '-T{}'.format(extension),
                         tmp_name + '.dot',
                         '-o',
                         filename])
        subprocess.call(['rm', tmp_name + '.dot'])

    def to_dot(self, rankdir='LR', dpi=300):
        """Visualize with graphviz dot."""
        dot_str = 'digraph FA {\n'
        dot_str += 'graph [dpi={}]\n'.format(dpi)
        dot_str += 'edge [arrowhead="empty"]\n'
        dot_str += 'rankdir={}\n'.format(rankdir)

        # nodes
        for state in self.Q:
            s = '"{0}"[label="{0}", shape={1} {2}]\n'
            color = ', fillcolor=lightgray, style=filled'
            dot_str += s.format(state.name,
                                'doublecircle' if state in self.F else 'circle',
                                color if state.is_active() else '')

        # edges
        for (state1, state2), letters in self.edges.items():
            if '$' in letters:
                letters = ['&#949;' if l=='$' else l for l in letters]
            dot_str += '"{}" -> "{}"[label="{}"]\n'.format(state1.name,
                                                           state2.name,
                                                           ', '.join(letters))

        dot_str += '}\n'

        return dot_str

    def _identify_multiple_edges(self):
        """Identify multiple edges between two nodes (for plotting purposes)."""
        edges = defaultdict(list)
        for state in self.Q:
            for letter, next_states in state.transitions.items():
                for s in next_states:
                    edges[(state, s)].append(letter)

        return edges

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

        # names of states should be unique
        assert len(self.Q) == len(set([s.name for s in self.Q]))

    def __repr__(self):
        """Describe object."""
        return '{}: {}'.format(self.name,
                               sorted([s.name for s in self.active_states]))
