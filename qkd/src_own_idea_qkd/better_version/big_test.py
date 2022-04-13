import subprocess
list_res = []
qubitt = []
error_rate = []

for i in range(10):
    subprocess.run(["qne", "experiment", "run", "exp", "--timeout",  "30"])
    with open("/root/qne-qchack-2022/qkd/exp/raw_output/LAST/results.yaml",'r') as f:
        f.readline()
        okk = f.readline()
        error_rate.append(float(okk[16:19]))

    with open("/root/qne-qchack-2022/qkd/exp/raw_output/LAST/results.yaml",'r') as f:
        f.readline()
        f.readline()
        ok = f.readline()
        qubitt.append(float(ok[15:21]))
        
    with open("/root/qne-qchack-2022/qkd/exp/raw_output/LAST/results.yaml",'r') as f:
        f.readline()
        f.readline()
        f.readline()
        ok = f.readline()
        if 'null' in ok:
            list_res.append('eve')
        else:
            list_res.append('no_eve')
    print(i)
ii = 0
for i in range(len(list_res)):
    if list_res[i] == 'no_eve':
        ii+=1
print("eve_check:",list_res)
print('eve success:',ii)
print("EPR_pair_consume:",qubitt)
print("error_rate:",error_rate)
print('max(error_rate):',max(error_rate))
print('avg(error_rate):',sum(error_rate)/len(error_rate))
print('min(error_rate):',min(error_rate))
#print(max(list_res))
print('finish!')