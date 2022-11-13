import subprocess
with open("output.txt", "w+") as output:
    subprocess.call(["python", "./train_rnn.py", "-gru", "-i" "data2"], stdout=output);