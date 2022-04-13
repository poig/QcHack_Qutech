from netqasm.sdk.external import NetQASMConnection, Socket

from netqasm.logging.glob import get_netqasm_logger

from epr_socket import DerivedEPRSocket as EPRSocket

logger = get_netqasm_logger()

############### Added myself

from netqasm.sdk.classical_communication.message import StructuredMessage
from math import pi, sqrt, log2
import random
from fractions import Fraction
from collections import defaultdict, Counter

class Basis(Fraction):
    def rotate(self, qubit):
        num, den = self.as_integer_ratio()
        n = num if num >= 0 else 2*den - num
        d = int(log2(den))
        # theta = pi * (self if self > 0 else (2-self))

        qubit.rot_X(n, d)

bases = {
    'a1': Basis(1, 4),
    'a2': Basis(1, 8),
    'a3': Basis(0, 1),

    'b1': Basis(1, 8),
    'b2': Basis(0, 1),
    'b3': Basis(-1, 8),
}

def E(measurement_pairs):
    P = Counter(measurement_pairs)
    N = sum(P.values())

    if N == 0:
        return 0

    return (P[0, 0] + P[1, 1] - P[1, 0] - P[0, 1]) / N

def get_S(mismatched):
    a1, a3 = bases['a1'], bases['a3']
    b1, b3 = bases['b1'], bases['b3']
    return (
        E(mismatched[a1, b1])
        - E(mismatched[a1, b3])
        + E(mismatched[a3, b1])
        + E(mismatched[a3, b3])
    )

ACCEPT_THRESHOLD = 2.1

def estimate_error_rate(socket,key,start,end):

    #using not same basis as testpair G1
    test_outcomes = key[start:end]
    test_indices = start,end

    socket.send_structured(StructuredMessage("Test indices", test_indices))
    target_test_outcomes = socket.recv_structured().payload
    socket.send_structured(StructuredMessage("Test outcomes", test_outcomes))
    #logger.info(f"alice target_test_outcomes: {target_test_outcomes}")

    num_error = 0
    for (i1, i2) in zip(test_outcomes, target_test_outcomes):
        #assert i1 == i2
        if i1 != i2:
            num_error += 1
            

    return (num_error / (end - start))*100
###############


def main(app_config=None, key_length=16):
    # Socket for classical communication
    socket = Socket("alice", "bob", log_config=app_config.log_config)
    # Socket for EPR generation
    epr_socket = EPRSocket("bob")

    alice = NetQASMConnection(
        app_name=app_config.app_name,
        log_config=app_config.log_config,
        epr_sockets=[epr_socket],
    )

    with alice:
        # IMPLEMENT YOUR SOLUTION HERE
        # logger.info("IMPLEMENT YOUR SOLUTION HERE - ALICE")

        key = []
        mismatched = defaultdict(list)
        n=16  
        qubitt=0
        while len(key) < key_length + n:

            # Create EPR pair
            qubit = epr_socket.create_keep()[0]

            basis_name = random.choice(['a1', 'a2', 'a3'])
            basis = bases[basis_name]
            basis.rotate(qubit)

            measurement = qubit.measure()
            alice.flush()
            measurement = int(measurement)

            # Alice sends her basis first
            socket.send(basis_name)
            # Wait for Bob's basis
            bob_basis_name = socket.recv()
            bob_basis = bases[bob_basis_name]

            if bob_basis == basis:
                key.append(measurement)
            else:
                bob_measurement = int(socket.recv())
                alice.flush()
                mismatched[basis, bob_basis].append(
                    (measurement, bob_measurement)
                )
            qubitt +=1
        error_rate = estimate_error_rate(socket, key,key_length,key_length + n)


        S = get_S(mismatched)
        accept_key = (S >= ACCEPT_THRESHOLD)

        socket.send('1' if accept_key and error_rate<=0.0 else '0')
        alice.flush()


    # RETURN THE SECRET KEY HERE
    return {
        "qubit use": qubitt,
        "error_rate": error_rate,
        "secret_key": key[:key_length] if (accept_key and error_rate==0.0) else None,
    }


if __name__ == "__main__":
    main()