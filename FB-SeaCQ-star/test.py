import Accumulator
import time

msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)

# w_set={'1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20'}
w_set={str(i) for i in range(5000)}
X_set=set()
for w in w_set:
    X_set.add(Accumulator.str2prime(w))

# gen
start_time = time.time()
acc, x_p=msa.genAcc(X_set)
end_time = time.time()
print("genAcc time cost:", float(end_time - start_time) * 1000.0, "ms")

# prove membership
start_time = time.time()
pi=msa.prove_membership(Accumulator.str2prime('2'), x_p)
end_time = time.time()
print("membership_prove time cost:", float(end_time - start_time) * 1000.0, "ms")

# verify membership
start_time = time.time()
msa.verify_membership(pi, acc, Accumulator.str2prime('2'))
end_time = time.time()
print("membership_verify time cost:", float(end_time - start_time) * 1000.0, "ms")


# prove non-membership
start_time = time.time()
a,d=msa.prove_non_membership(Accumulator.str2prime('5001'), x_p)
end_time = time.time()
print("non-membership_prove time cost:", float(end_time - start_time) * 1000.0, "ms")


# verify non-membership
start_time = time.time()
msa.verify_non_membership(a, d, acc, Accumulator.str2prime('5001'))
end_time = time.time()
print("non-membership_verify time cost:", float(end_time - start_time) * 1000.0, "ms")