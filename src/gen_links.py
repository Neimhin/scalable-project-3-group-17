
print("ssh \\")
for i in range(33000,33200):
    print(f"-L {i}:127.0.0.1:{i} \\")
for i in range(33900,34000):
    print(f"-L {i}:127.0.0.1:{i} \\")
print("pi")
