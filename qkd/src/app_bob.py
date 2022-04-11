from netqasm.logging.glob import get_netqasm_logger
from netqasm.sdk.external import NetQASMConnection, Socket

from netqasm.sdk.classical_communication.message import StructuredMessage
from dataclasses import dataclass
from typing import Optional
import random
import logging

from epr_socket import DerivedEPRSocket as EPRSocket

logger = get_netqasm_logger()

ALL_MEASURED = "All qubits measured"

#Making entangled bell state The source centre chooses the EPR pair(Entangled Bell State) |φ+⟩=(1/√2)(|00⟩+|11⟩), 
#sends the first particle |φ+⟩₁ to Alice and second particle |φ+⟩₂ to Bob.

#one-time pad technique 

def receive_E91_states(conn, epr_socket, socket, n): ###
    '''Making entangled bell state The source centre chooses the EPR pair(Entangled Bell State) |φ+⟩=(1/√2)(|00⟩+|11⟩), 
        sends the first particle |φ+⟩₁ to Alice and second particle |φ+⟩₂ to Bob.'''
    bit_flips = [None for _ in range(n)]
    key_string = [random.randint(1, 3) for i in range(n)] # string b of Alice
    
    for i in range(n):
        q = epr_socket.recv_keep(1)[0]
        if key_string[i] == 1:
            q.H()
        elif key_string[i] == 2:
            q.S()
            q.H()
            q.rot_Z(1,2) # same as q.T() z-rotation angle pi/4
            q.H()
        elif key_string[i] == 3:
            pass
        #conn.flush()
        m = q.measure()
        conn.flush()
        bit_flips[i] = int(m)
    return bit_flips, key_string

# function that calculates CHSH correlation value
def chsh_corr(n,aliceMeasurementChoices,bobMeasurementChoices):
    pass

def filter_bases(socket, pairs_info):
    bases = [(i, pairs_info[i].basis) for (i, pair) in enumerate(pairs_info)]

    remote_bases = socket.recv_structured().payload
    socket.send_structured(StructuredMessage("Bases", bases))

    for (i, basis), (remote_i, remote_basis) in zip(bases, remote_bases):
        assert i == remote_i
        if basis == 1 and remote_basis == 1:
            pairs_info[i].same_basis = True
        elif basis == 2 and remote_basis == 2:
            pairs_info[i].same_basis = True
        elif basis == 3 and remote_basis == 3:
            pairs_info[i].same_basis = True
        else:
            pairs_info[i].same_basis = False

    #corr = chsh_corr(n, pairs_info.basis,remote_bases)
    return pairs_info#, corr

def estimate_error_rate(socket, pairs_info, num_test_bits):
    test_indices = socket.recv_structured().payload
    for pair in pairs_info:
        pair.test_outcome = pair.index in test_indices

    test_outcomes = [(i, pairs_info[i].outcome) for i in test_indices]

    #logger.info(f"bob test indices: {test_indices}")
    #logger.info(f"bob test outcomes: {test_outcomes}")

    socket.send_structured(StructuredMessage("Test outcomes", test_outcomes))
    target_test_outcomes = socket.recv_structured().payload
    #logger.info(f"bob target_test_outcomes: {target_test_outcomes}")

    num_error = 0
    for (i1, t1), (i2, t2) in zip(test_outcomes, target_test_outcomes):
        assert i1 == i2
        if t1 != t2:
            num_error += 1
            pairs_info[i1].same_outcome = False
        else:
            pairs_info[i1].same_outcome = True

    return pairs_info, (num_error / num_test_bits)

@dataclass
class PairInfo:
    """Information that Alice has about one generated pair.
    The information is filled progressively during the protocol."""

    # Index in list of all generated pairs.
    index: int

    # Basis Alice measured in. 0 = Z, 1 = X.
    basis: int

    # Measurement outcome (0 or 1).
    outcome: int

    # Whether Bob measured his qubit in the same basis or not.
    same_basis: Optional[bool] = None

    # Whether to use this pair to estimate errors by comparing the outcomes.
    test_outcome: Optional[bool] = None

    # Whether measurement outcome is the same as Bob's. (Only for pairs used for error estimation.)
    same_outcome: Optional[bool] = None


def main(app_config=None, key_length=16):
    print('start_prog')
    '''fileHandler = logging.FileHandler("bob_logfile.log")
    logger.setLevel(logging.INFO)
    logger.addHandler(fileHandler)'''

    # Socket for classical communication
    socket = Socket("bob", "alice", log_config=app_config.log_config)
    # Socket for EPR generation
    epr_socket = EPRSocket("alice")

    bob = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )

    secret_key = None
    n = key_length * 3

    with bob:
        # IMPLEMENT YOUR SOLUTION HERE
        bit_flips,basis = receive_E91_states(bob, epr_socket, socket, n)
    bits = [int(b) for b in bit_flips]
    bases = [int(b) for b in basis]

    pairs_info = []
    for i in range(n):
        pairs_info.append(
            PairInfo(
                index=i,
                basis=int(bases[i]),
                outcome=int(bits[i]),
            )
        )


    socket.send(ALL_MEASURED)

    pairs_info = filter_bases(socket, pairs_info)
    
    pairs_info, error_rate = estimate_error_rate(socket, pairs_info, n)
    #logger.info(f"alice error rate: {error_rate}")
    
    raw_key = [pair.outcome for pair in pairs_info if not pair.test_outcome]

    same_basis_count = sum(pair.same_basis for pair in pairs_info)

    outcome_comparison_count = sum(pair.test_outcome for pair in pairs_info if pair.same_basis)

    diff_outcome_count = outcome_comparison_count - sum(pair.same_outcome for pair in pairs_info if pair.test_outcome)

    key = [pair.outcome for pair in pairs_info if pair.same_basis]

    my_key = ''.join(map(str,key))[:key_length]
    
    return {
        'qubit_num':n,
        # Number of times measured in the same basis as Bob.
        "same_basis_count": same_basis_count,
        # Number of pairs chosen to compare measurement outcomes for.
        "outcome_comparison_count": outcome_comparison_count,
        "diff_outcome_count": diff_outcome_count,
        # Raw key.
        # ('Result' of this application. In practice, there'll be post-processing to produce secure shared key.)
        "secret_key": my_key,
    }


if __name__ == "__main__":
    print('start')
    main()
