from netqasm.sdk.qubit import Qubit
from math import pi, sqrt, log2
import random
from fractions import Fraction
from collections import defaultdict, Counter
#from epr_socket import DerivedEPRSocket as EPRSocket

class Eve:

    def __init__(self):
        pass
    
    def eavesdrop(self, qubit: Qubit):
        # IMPLEMENT YOUR EAVESDROPPING CODE HERE
        #
        # This method is called for each qubit individually at both ends of the
        # connection. However, note that these will be actually two separate
        # instances of Eve - one at each end. Thus, whilst you can share state
        # from qubit to qubit, this state cannot be shared between the two ends
        # of the connection.
        #
        # When measuring make sure to use `inplace=True` when calling
        # `qubit.measure(inpace=True)` so that the qubit is still available when
        # delivered to the application. Otherwise, the qubit is released.
        #bit_flips = [None for _ in range(n)]
        key_string = random.randint(1, 3)
        if key_string == 1:
            qubit.H()
        elif key_string == 2:
            qubit.S()
            qubit.H()
            qubit.T()
            qubit.H()
        #q.flush()
        #
        #m = qubit.measure(inplace=True)
        #bit_flips[i] = int(m)
        #q.flush()
        #return qubit

        pass
        
        
