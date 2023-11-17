
print("ssh \\")
for i in range(33000,33200):
    print(f"-L {i}:localhost:{i} \\")
for i in range(33900,34000):
    print(f"-L {i}:localhost:{i} \\")
print("pi")
