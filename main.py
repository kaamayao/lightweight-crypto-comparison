from DES.index import DES_encrypt

# Read all data messages
with open('data/short_message.txt', 'r') as f:
    short_message = f.read()

with open('data/medium_message.txt', 'r') as f:
    medium_message = f.read()

with open('data/long_message.txt', 'r') as f:
    long_message = f.read()

with open('data/very_long_message.txt', 'r') as f:
    very_long_message = f.read()

# Print all messages
print("=== SHORT MESSAGE ===")
print(short_message)
print("\n=== MEDIUM MESSAGE ===")
print(medium_message)
print("\n=== LONG MESSAGE ===")
print(long_message)
print("\n=== VERY LONG MESSAGE ===")
print(very_long_message)

DES_encrypt()
