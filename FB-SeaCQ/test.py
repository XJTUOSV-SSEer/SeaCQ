import hmac
import Accumulator
import time

# k1=b'sdj'
# digest=hmac.new(key=k1, msg='fid'.encode('utf-8'), digestmod='shake128').digest()
# print(len(digest))

# a=bytes(16)
# b=bytes(16)

# print(a==b)


msa= Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)

w_set = {'1', '2', '3', '4', '5'}
x_set = set()
for w in w_set:
    x_set.add(Accumulator.str2prime(w))

# 
acc, p = msa.genAcc(x_set)
# 
x = Accumulator.str2prime('2')
start_time = time.time()

pi = msa.prove_membership(x, p)
end_time = time.time()
print("search time cost:", end_time - start_time, "s")
print(msa.verify_membership(pi, acc, x))
# print(pi)