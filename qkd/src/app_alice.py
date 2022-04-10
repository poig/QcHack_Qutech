from netqasm.logging.glob import get_netqasm_logger
from netqasm.sdk.external import NetQASMConnection, Socket
from typing import Optional
import random

from epr_socket import DerivedEPRSocket as EPRSocket

logger = get_netqasm_logger()

ALL_MEASURED = "All qubits measured"


def distribute_bb84_states(conn, epr_socket, socket, n): ###
    bit_flips = [None for _ in range(n)]
    key_string = [random.randint(1, 3) for i in range(n)] # string b of Alice

    for i in range(n):
        q = epr_socket.create_keep(1)[0]
        if key_string[i] == 1:
            q.H()
        elif key_string[i] == 2:
            q.S()
            q.H()
            q.T()
            q.H()
        m = q.measure()
        conn.flush()
        bit_flips[i] = int(m)
    return bit_flips, key_string

# function that calculates CHSH correlation value
def chsh_corr(n,aliceMeasurementChoices,bobMeasurementChoices):
    pass

def filter_bases(socket, pairs_info):
    bases = [(i, pairs_info[i].basis) for (i, pair) in enumerate(pairs_info)]

    msg = StructuredMessage(header="Bases", payload=bases)
    socket.send_structured(msg)
    remote_bases = socket.recv_structured().payload

    for (i, basis), (remote_i, remote_basis) in zip(bases, remote_bases):
        assert i == remote_i
        pairs_info[i].same_basis = basis == remote_basis

    #corr = chsh_corr(n, pairs_info.basis,remote_bases)
    return pairs_info#, corr

def estimate_error_rate(socket, pairs_info, num_test_bits):
    same_basis_indices = [pair.index for pair in pairs_info if pair.same_basis]
    test_indices = random.sample(
        same_basis_indices, min(num_test_bits, len(same_basis_indices))
    )
    for pair in pairs_info:
        pair.test_outcome = pair.index in test_indices

    test_outcomes = [(i, pairs_info[i].outcome) for i in test_indices]

    logger.info(f"alice finding {num_test_bits} test bits")
    logger.info(f"alice test indices: {test_indices}")
    logger.info(f"alice test outcomes: {test_outcomes}")

    socket.send_structured(StructuredMessage("Test indices", test_indices))
    target_test_outcomes = socket.recv_structured().payload
    socket.send_structured(StructuredMessage("Test outcomes", test_outcomes))
    logger.info(f"alice target_test_outcomes: {target_test_outcomes}")

    num_error = 0
    for (i1, t1), (i2, t2) in zip(test_outcomes, target_test_outcomes):
        assert i1 == i2
        if t1 != t2:
            num_error += 1
            pairs_info[i1].same_outcome = False
        else:
            pairs_info[i1].same_outcome = True

    return pairs_info, (num_error / num_test_bits)

class PairInfo:
    """Information that Bob has about one generated pair.
    The information is filled progressively during the protocol."""

    # Index in list of all generated pairs.
    index: int

    # Basis Alice measured in. 1/2/3
    basis: int

    # Measurement outcome (0 or 1).
    outcome: int

    # Whether Bob measured his qubit in the same basis or not.
    same_basis: Optional[int] = None

    # Whether to use this pair to estimate errors by comparing the outcomes.
    test_outcome: Optional[int] = None

    # Whether measurement outcome is the same as Bob's. (Only for pairs used for error estimation.)
    same_outcome: Optional[bool] = None

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
        bit_flips,basis = distribute_bb84_states(alice, epr_socket, socket, key_length)
    bits = [int(b) for b in bit_flips]
    bases = [int(b) for b in basis]

    pairs_info = []
    for i in range(key_length):
        pairs_info.append(
            PairInfo(
                index=i,
                basis=int(basis[i]),
                outcome=int(bits[i]),
            )
        )


    m = socket.recv()
    if m != ALL_MEASURED:
        logger.info(m)
        raise RuntimeError("Failed to distribute BB84 states")

    pairs_info = filter_bases(socket, pairs_info)
    
    pairs_info, error_rate = estimate_error_rate(socket, pairs_info, num_test_bits)
    logger.info(f"alice error rate: {error_rate}")
    
    raw_key = [pair.outcome for pair in pairs_info if not pair.test_outcome]
    logger.info(f"alice raw key: {raw_key}")

    table = []
    for pair in pairs_info:
        basis = "X" if pair.basis == 1 else "Z"
        check = pair.same_outcome if pair.test_outcome else "-"
        table.append([pair.index, basis, pair.same_basis, pair.outcome, check])

    x_basis_count = sum(pair.basis for pair in pairs_info)
    z_basis_count = num_bits - x_basis_count
    same_basis_count = sum(pair.same_basis for pair in pairs_info)

    outcome_comparison_count = sum(
        pair.test_outcome for pair in pairs_info if pair.same_basis
    )
    diff_outcome_count = outcome_comparison_count - sum(
        pair.same_outcome for pair in pairs_info if pair.test_outcome
    )
    if outcome_comparison_count == 0:
        qber = 1
    else:
        qber = (diff_outcome_count) / outcome_comparison_count
    key_rate_potential = 1 - 2 * h(qber)

    return {
        # Table with one row per generated pair.
        # Columns:
        #   - Pair number
        #   - Measurement basis ("X" or "Z")
        #   - Same basis as Bob ("True" or "False")
        #   - Measurement outcome ("0" or "1")
        #   - Outcome same as Bob ("True", "False" or "-")
        #       ("-" is when outcomes are not compared)
        "table": table,
        # Number of times measured in the X basis.
        "x_basis_count": x_basis_count,
        # Number of times measured in the Z basis.
        "z_basis_count": z_basis_count,
        # Number of times measured in the same basis as Bob.
        "same_basis_count": same_basis_count,
        # Number of pairs chosen to compare measurement outcomes for.
        "outcome_comparison_count": outcome_comparison_count,
        # Number of compared outcomes with equal values.
        "diff_outcome_count": diff_outcome_count,
        # Estimated Quantum Bit Error Rate (QBER).
        "qber": qber,
        # Rate of secure key that can in theory be extracted from the raw key.
        "key_rate_potential": key_rate_potential,
        # Raw key.
        # ('Result' of this application. In practice, there'll be post-processing to produce secure shared key.)
        "raw_key": raw_key,

        "secret_key": raw_key,
    }
    # RETURN THE SECRET KEY HERE


if __name__ == "__main__":
    main()
