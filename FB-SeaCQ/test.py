import hmac

# k1=b'sdj'
# digest=hmac.new(key=k1, msg='fid'.encode('utf-8'), digestmod='shake128').digest()
# print(len(digest))

a=bytes(16)
b=bytes(16)

print(a==b)