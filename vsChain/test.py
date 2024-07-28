from web3 import Web3

# a=Web3.keccak(5)
# print(a)
# print(type(a))
# b=bytes(a)
# print(b)
# print(type(b))


# a=(1,2,3)
# b,c,d=a
# print(b)
# print(c)

# b=dict()
# a=[1,2]
# b['a']=a
# a=[3,4]
# b['b']=a
# print(b)
# a.append(5)
# print(b)


a={1:(0,1), 2:(3,4), 3:(4,5)}
for x, (y,z) in a.items():
    print(y,z)