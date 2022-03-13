import os, sys

if len(sys.argv) < 2:
    print("Usage: sendall.py <COM_PORT>")
    exit(1)

for file in os.listdir("."):
    if file.endswith(".py") and file != "sendall.py":
        print(file)
        os.system(f"ampy -p  {sys.argv[1]} -d 1 put {file}")

