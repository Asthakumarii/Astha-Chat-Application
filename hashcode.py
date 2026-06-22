import hashlib

print(hashlib.sha256("1234".encode()).hexdigest())
print(hashlib.sha256("abcd".encode()).hexdigest())
print(hashlib.sha256("admin123".encode()).hexdigest())