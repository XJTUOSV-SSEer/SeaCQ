from web3 import Web3

a=Web3.keccak(5)
print(a)
print(type(a))
b=bytes(a)
print(b)
print(type(b))