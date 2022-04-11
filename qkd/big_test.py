import subprocess
list_res = []
for i in range(100):
    subprocess.run(["qne", "experiment", "run", "exp", "--timeout",  "30"])

    with open("/root/qne-qchack-2022/qkd/exp/raw_output/LAST/results.yaml",'r') as f:
        f.readline()
        f.readline()
        ok = f.readline()
    list_res.append(float(ok[22:27]))
    print(i)
    print(max(list_res))
print('finish!')
