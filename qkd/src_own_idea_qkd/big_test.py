import subprocess
list_qubit = []
list_res = []
for i in range(10):
    subprocess.run(["qne", "experiment", "run", "exp", "--timeout",  "30"])

    with open("/root/qne-qchack-2022/qkd/exp/raw_output/LAST/results.yaml",'r') as f:
        f.readline()
        f.readline()
        okk = f.readline()
        #print(okk)
    with open("/root/qne-qchack-2022/qkd/exp/raw_output/LAST/results.yaml",'r') as f:
        f.readline()
        ok = f.readline()
        #print(ok)
    list_qubit.append(float(okk[14:19]))
    list_res.append(float(ok[16:21]))
    #print(ok)
    print(i)
print(list_qubit)
print(list_res)
print('max:',max(list_res))
print('avg:',sum(list_res)/len(list_res))
print('min:',min(list_res))
print('finish!')