#Runpod Dataset Creator
#Read data file 55 
import csv
import math
import subprocess
start = 0
datasetIndex = 0
validCount = 0
validTarget = 25
validBound = 231.5
cadoFolder = "/home/cado-nfs/build/c65b414053c9"
cadoScript = "cado-nfs.py"
logsPath = "/home/murage/p95.parameters_snapshot.1"
filename = f'dataset135_0_volume_0.csv'
storage  = f'storage135_0_volume_0.csv'

def CadoSnapshotLog(cadoFolder, cadoScript, logsPath, target,ell, primeNumber):
    cmd = [f"./{cadoScript}", logsPath, f"target={target}"]
    #print("Running command:", " ".join(cmd))
    #print("From folder:", cadoFolder)
    process = subprocess.Popen(cmd,cwd=cadoFolder,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    # Handle output line by line
    for line in process.stdout:
        logbase_ = line.split("logbase = ")
        logtarget_ = line.split("log(target) = ")
        if len(logbase_) > 1:
            logbase = int(logbase_[-1])
        if len(logtarget_) > 1:
            logtarget = int(logtarget_[-1].split()[0])
        #print(line, end="")
    process.wait()  
    assert 1 == pow(pow(logbase, logtarget, primeNumber) * pow(target, -1, primeNumber), (primeNumber-1)//ell, primeNumber)
    return logbase, logtarget

def ConvertToBaseC(target_log_base_unkown):
    ell =205115282021455665897114700593932402728804164701536103180137503955397371
    c_projection_log = 102244747668944059439837329676977903860279320016288084564987016428661784
    return (target_log_base_unkown * pow(c_projection_log, -1, ell)) % ell

bit_lengths = []
total_bits = []
random_multipliers = []
rhs_values = []

ell =205115282021455665897114700593932402728804164701536103180137503955397371
primeNumber = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    for row in csvreader:
        bit_lengths.append(int(row[0]))        
        total_bits.append(int(row[1]))        
        random_multipliers.append(int(row[2])) 
        rhs_values.append(int(row[3]))        
print(f"Read {len(bit_lengths)} rows")

with open(storage, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    for i in range(start, len(bit_lengths)):
        logbase, rhs_projection_log_base_unkown  = CadoSnapshotLog(cadoFolder, cadoScript, logsPath, rhs_values[i], ell, primeNumber)
        rhs_projection_log_base_c  = ConvertToBaseC(rhs_projection_log_base_unkown)
        #print(f"{bit_lengths[i]}, {total_bits[i]} : {random_multipliers[i]},{math.log(rhs_projection_log_base_c,2)} ,{rhs_values[i]},{rhs_projection_log_base_c}")
        rhs_log = math.log(rhs_projection_log_base_c, 2)
        if(rhs_log < validBound):
            validCount += 1
        print(f"{i}: found {rhs_log} bits, validCount: {validCount} / {validTarget}")
        csvwriter.writerow([i, rhs_projection_log_base_c])
        if(validCount == validTarget):
            break

