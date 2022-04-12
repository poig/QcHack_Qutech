from netqasm.logging.glob import get_netqasm_logger
from netqasm.sdk.external import NetQASMConnection, Socket

from netqasm.sdk.classical_communication.message import StructuredMessage
from dataclasses import dataclass
from typing import Optional
import random
import logging

from epr_socket import DerivedEPRSocket as EPRSocket

logger = get_netqasm_logger()

def estimate_error_rate(socket, key):
    test_indices = socket.recv_structured().payload
    start,end = test_indices
    test_outcomes = key[start:end]

    #logger.info(f"bob test indices: {test_indices}")
    #logger.info(f"bob test outcomes: {test_outcomes}")

    socket.send_structured(StructuredMessage("Test outcomes", test_outcomes))
    target_test_outcomes = socket.recv_structured().payload
    #logger.info(f"bob target_test_outcomes: {target_test_outcomes}")

    num_error = 0
    for (i1, i2) in zip(test_outcomes, target_test_outcomes):
        #assert i1 == i2
        if i1 != i2:
            num_error += 1

    return (num_error / (end-start))*100

def main(app_config=None, key_length=16):
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

    with bob:
        key = []
        qubitt=0
        # IMPLEMENT YOUR SOLUTION HERE
        while len(key) < key_length*2:
            basis_name = random.randint(1, 3) # string b of Alice
            #Alice makes a measurement with a direction randomly chosen between {0, π/8 , π/4}, 
            q = epr_socket.recv_keep()[0]
            bob.flush()
            if basis_name == 1: #X basis
                q.H()
            elif basis_name == 2: #W basis
                q.S()
                q.H()
                q.T()#q.rot_Z(1,2) # same as q.T() z-rotation angle pi/4
                q.H()
            elif basis_name == 3: #Z basis
                pass
            #conn.flush()
            m = q.measure()
            bob.flush()
            measurement = int(m)
            # Wait for Alice's basis
            
            alice_basis = socket.recv()
            # Bob sends his basis second
            basis_name = str(basis_name)
            socket.send(basis_name)
            #basis = bases[basis_name]

            if alice_basis == basis_name:
                key.append(measurement)
            #else:
            #    socket.send(str(measurement))
            #    bob.flush()
            qubitt +=1
        error_rate = estimate_error_rate(socket, key)
    
    return {
        # Number of times measured in the same basis as Bob.
        #"same_basis_count": same_basis_count,
        # Number of pairs chosen to compare measurement outcomes for.
        #"outcome_comparison_count": outcome_comparison_count,
        #"diff_outcome_count": diff_outcome_count,
        'qubit use': qubitt,
        "error_rate" : error_rate,
        # Raw key.
        # ('Result' of this application. In practice, there'll be post-processing to produce secure shared key.)
        "secret_key": key[:16],
    }


if __name__ == "__main__":
    print('start')
    main()