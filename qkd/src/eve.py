from netqasm.sdk.qubit import Qubit
import random
from netqasm.sdk.external import NetQASMConnection
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

        #no_one_time_pad
        q = qubit
        n=1
        #bit_flips = [None for _ in range(n)]
        key_string = [random.randint(1, 3) for i in range(n)]
        for i in range(n):
            if key_string[i] == 1:
                q.H()
            elif key_string[i] == 2:
                q.S()
                q.H()
                q.T()
                q.H()
            #q.flush()
            
            m = q.measure(inplace=True)
            #bit_flips[i] = int(m)
            #q.flush()
        return q
        #pass
