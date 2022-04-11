# QcHack_Qutech
1) Create python venv
2) `pip3 install -e "git+https://github.com/QuTech-Delft/qne-adk.git@a125b2d27f1e5fef2822329cf824b18e22e9d00e#egg=qne-adk"`<br>
(need to register)`pip3 install squidasm==0.8.4 --extra-index-url https://pypi.netsquid.org`<br>
(if any install problem happen)`pip3 install "netsquid==1.1.5" "pydynaa==1.0.0" "netsquid-nv>=9.2.0" --extra-index-url https://pypi.netsquid.org -e "git+https://gitlab.com/wkozlowski-tudelft/netsquid-magic.git@57bb20a206704ee1a4885b60e059ae9660bc7890#egg=netsquid-magic"`
3) (create the application)`qne application create qkd alice bob`    
and then copy over the necessary files from the template directory:   
`cp template/src/app_alice.py template/src/app_bob.py template/src/epr_socket.py template/src/eve.py qkd/src
cp template/config/application.json qkd/config`
5) (run the application)`qne experiment run exp --timeout 30`

**Part 1** basic protocol && Eavesdropper

For Part 1 of the challenge, we have implemented E91 protocol. Below is the summary of how the protocol works. 
- [x] In noiseless channel if error percentage is less than 20 there is no eve.py active, so autocheck.py will fail if eve is there.  
- [ ] In noise channel, but small noise won't have big effect.

1) Making entangled bell state
The source centre chooses the EPR pair(Entangled Bell State) |φ+⟩=(1/√2)(|00⟩+|11⟩), sends the first particle |φ+⟩₁ to Alice and second particle |φ+⟩₂ to Bob.

2) Alice makes a measurement with a direction randomly chosen between {0, π/8 , π/4}, whereas Bob makes a measurement with a direction randomly chosen between {−π/8 , 0, π/8}. They record the measurement result and broadcast the measurement basis which they used, through the classical channel.

3) Thus, Alice and Bob now know each other's choice. They divide the measurement result into two groups: one is the decoy qubits G₁ where they choose different measurement basis and another is the raw key qubits G₂ where they choose the same measurement basis.

4) The group G₁ is used to detect whether there is an eavesdropping. To detect eavesdropping, they can compute the test statistic S using the correlation coefficients between Alice’s bases and Bob’s, similar to that shown in the Bell test experiments. If there is an error in the value of S, which means that there is also a eavesdropper, Alice and Bob will conclude that the quantum channel is not safe and they will interrupt this communication and start a new one.

5) If the quantum channel is safe, G₂ can be used as the raw keys because Alice and Bob can receive the same measurements. Both Alice and Bob agree on that the measurement |0⟩ represents the classical bit 0, while the measurement |1⟩ represents the classical bit 1, and thus get their key string.

**Part 2** Noisy qubits
 
Noise is inherent part of the current NISQ hardware. Our idea is to implement the protocol with for error correction. Surface code is a 2D error correcting code that can error correct both bit-flip and phase-flip errors and it is quite robust. It has the advantage that the size of the surface code can be varied based on the availability of number of physical qubits, thus can make use of available qubits to the maximum extent. Finding simulator results by extending our implementation of E91 protocol with surface code can be promising to work with NISQ computers.


**Open Question**

For open question, we believe extending the procedure of the paper by [Mario Mastani](https://www.researchgate.net/publication/337901106_Non-ambiguity_quantum_teleportation_protocol) on Non-ambiguity teleportation protocol for entanglement pair generation and communication can lead to a better protocol with no or very minimal classical communication required.
