# QcHack_Qutech
1) Create python venv
2) `pip3 install -e "git+https://github.com/QuTech-Delft/qne-adk.git@a125b2d27f1e5fef2822329cf824b18e22e9d00e#egg=qne-adk"`<br>
(need to register):   
`pip3 install squidasm==0.8.4 --extra-index-url https://pypi.netsquid.org`<br>
(if any install problem happen):   
`pip3 install "netsquid==1.1.5" "pydynaa==1.0.0" "netsquid-nv>=9.2.0" --extra-index-url https://pypi.netsquid.org -e "git+https://gitlab.com/wkozlowski-tudelft/netsquid-magic.git@57bb20a206704ee1a4885b60e059ae9660bc7890#egg=netsquid-magic"`
3) (create the application)`qne application create qkd alice bob`    
and then copy over the necessary files from the template directory:   
`cp template/src/app_alice.py template/src/app_bob.py template/src/epr_socket.py template/src/eve.py qkd/src
cp template/config/application.json qkd/config`
5) (run the application)`qne experiment run exp --timeout 30`
6) (see the result by going to qkd/exp/results/processed.json or qkd/exp/raw_output/LAST/results.yaml)

**Part 1** basic protocol && Eavesdropper

For Part 1 of the challenge, we have implemented E91 protocol. Below is the summary of how the protocol works. 
- [x] In noiseless channel if error percentage is less than 20(which can test with **big_test.py** that loop though 100time simulation and find the maximum error percentage) there is no **eve.py** active, so **autocheck.py** will fail if eve is there, the more code we do the more secure and more detailed we know if eve is there.the higher the qubit, the more accurate it is.
    
without eve 100 loop error percentage:(max: 27.5)(avg: 17.825)(16 over 20 percentage)   
[20.0, 22.5, 17.5, 15.0, 25.0, 16.25, 22.5, 15.0, 17.5, 20.0, 7.5, 17.5, 20.0, 18.75, 21.25, 13.75, 13.75, 18.75, 18.75, 21.25, 13.75, 17.5, 18.75, 12.5, 20.0, 13.75, 12.5, 17.5, 18.75, 16.25, 18.75, 11.25, 20.0, 18.75, 15.0, 18.75, 20.0, 11.25, 17.5, 21.25, 13.75, 20.0, 7.5, 22.5, 17.5, 20.0, 22.5, 26.25, 23.75, 20.0, 15.0, 15.0, 16.25, 16.25, 16.25, 17.5, 13.75, 22.5, 18.75, 16.25, 16.25, 21.25, 22.5, 23.75, 18.75, 20.0, 26.25, 25.0, 20.0, 21.25, 18.75, 11.25, 12.5, 15.0, 12.5, 25.0, 12.5, 8.75, 20.0, 8.75, 23.75, 13.75, 18.75, 18.75, 15.0, 10.0, 13.75, 17.5, 20.0, 11.25, 20.0, 22.5, 17.5, 27.5, 17.5, 20.0, 26.25, 13.75, 17.5, 20.0]  
   
with eve 100 loop error percentage:(max:38.75)(avg: 28.1492)(8 eve success lower 20 percentage)   
[31.25, 33.75, 23.75, 32.5, 31.25, 27.5, 20.0, 30.0, 23.75, 36.25, 36.25, 21.25, 31.25, 23.75, 26.25, 27.5, 35.0, 28.74, 27.5, 31.25, 30.0, 27.5, 30.0, 25.0, 23.75, 32.5, 28.74, 28.74, 31.25, 27.5, 28.74, 27.5, 26.25, 20.0, 35.0, 21.25, 38.75, 31.25, 27.5, 30.0, 27.5, 30.0, 30.0, 26.25, 21.25, 22.5, 26.25, 32.5, 27.5, 32.5, 37.5, 26.25, 28.74, 28.74, 30.0, 32.5, 30.0, 30.0, 23.75, 27.5, 23.75, 15.0, 18.75, 36.25, 25.0, 36.25, 28.74, 25.0, 25.0, 23.75, 37.5, 31.25, 23.75, 21.25, 20.0, 18.75, 31.25, 28.74, 20.0, 26.25, 31.25, 25.0, 21.25, 27.5, 37.5, 30.0, 26.25, 25.0, 32.5, 23.75, 31.25, 35.0, 30.0, 16.25, 32.5, 26.25, 37.5, 32.5, 25.0, 31.25]
- [ ] In noise channel, but small noise won't have big effect. (< 0.9)

1) Making entangled bell state
The source centre chooses the EPR pair(Entangled Bell State) |??+???=(1/???2)(|00???+|11???), sends the first particle |??+?????? to Alice and second particle |??+?????? to Bob.

2) Alice makes a measurement with a direction randomly chosen between {0, ??/8 , ??/4}, whereas Bob makes a measurement with a direction randomly chosen between {?????/8 , 0, ??/8}. They record the measurement result and broadcast the measurement basis which they used, through the classical channel.(can apply one-time-pad)

3) Thus, Alice and Bob now know each other's choice. They divide the measurement result into two groups: one is the decoy qubits G??? where they choose different measurement basis and another is the raw key qubits G??? where they choose the same measurement basis.

4) The group G??? is used to detect whether there is an eavesdropping. To detect eavesdropping, they can compute the test statistic S using the correlation coefficients between Alice???s bases and Bob???s, similar to that shown in the Bell test experiments. If there is an error in the value of S, which means that there is also a eavesdropper, Alice and Bob will conclude that the quantum channel is not safe and they will interrupt this communication and start a new one.

5) If the quantum channel is safe, G??? can be used as the raw keys because Alice and Bob can receive the same measurements. Both Alice and Bob agree on that the measurement |0??? represents the classical bit 0, while the measurement |1??? represents the classical bit 1, and thus get their key string.

**Part 2** Noisy qubits
 
Noise is inherent part of the current NISQ hardware. Our idea is to implement the protocol with for error correction. Surface code is a 2D error correcting code that can error correct both bit-flip and phase-flip errors and it is quite robust. It has the advantage that the size of the surface code can be varied based on the availability of number of physical qubits, thus can make use of available qubits to the maximum extent. Finding simulator results by extending our implementation of E91 protocol with surface code can be promising to work with NISQ computers.


**Open Question**

For open question, we believe extending the procedure of the paper by [Mario Mastani](https://www.researchgate.net/publication/337901106_Non-ambiguity_quantum_teleportation_protocol) on Non-ambiguity teleportation protocol for entanglement pair generation and communication can lead to a better protocol with no or very minimal classical communication required.
