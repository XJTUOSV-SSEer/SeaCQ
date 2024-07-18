import numbthy
import hashlib


def str2prime(str:str):
    '''
    将字符串映射为1个素数
    '''
    # 求str的哈希对应的整数
    d=hashlib.sha256(str.encode('utf-8')).digest()
    d=d[0:4]
    n=int.from_bytes(d, byteorder='big')
    # 求素数
    while True:
        if numbthy.is_prime(n):
            break
        else:
            n=n+1
    return n

class Accumulator:
    # RSA参数，对应于累加器的参数
    p=0
    q=0
    n=0
    g=0

    
    def __init__(self,p,q,g):
        '''
        构造函数
        '''         
        self.p=p
        self.q=q
        self.n=p*q
        self.g=g
    
    def genAcc(self, x_set):
        '''
        生成Acc值。
        input:
            x_set - 一个set，储存若干素数

        output:
            acc - Acc值
            x_p - 
        '''
        # 首先计算phi_n=(p-1)(q-1)
        phi_n=(self.p-1)*(self.q-1)

        # 计算x_p
        x_p=1
        tmp=1

        for x in x_set:
            x_p=x_p*x
            tmp=((x% phi_n) * tmp)% (phi_n)

        # 计算acc
        acc=numbthy.power_mod(self.g, tmp, self.n)
        return acc,x_p
    
    
    def prove_non_membership(self, x, x_p):
        '''
        证明不存在性。若返回None，则无法证明元素不存在（即元素实际上存在）
        input:
            x - 要证明不存在的元素，一个素数
            x_p - 预先发送给服务器的乘积
        output:
            a - 
            d - g^b mod n
        '''

        # 判断x_p%x==0
        if x_p%x==0:
            return None

        # 利用拓展欧几里得定理求满足方程a*x_p+b*x=1的解a, b
        _, a, b=numbthy.xgcd(x_p,x)

        # 计算证明，并用phi_n优化
        # 若b为负数，则计算g^b mod n时需要先求逆元，即(inv(g))^(-b mod phi_n) mod n
        phi_n=(self.q-1)*(self.p-1)
        if b<0:
            return a, numbthy.power_mod(numbthy.inverse_mod(self.g,self.n), (-b)%phi_n, self.n)
        else:
            return a, numbthy.power_mod(self.g, b%phi_n, self.n)
    

    def verify_non_membership(self, a, d, acc, x):
        '''
        验证不存在性
        input:
            a - 证明的第一部分
            d - 证明的第二部分
            acc - acc值
            x - 要验证不存在的元素，一个素数
        output:
            flag - 若为True，验证通过；若为False，验证未通过，说明proof是伪造的
        '''

        # 计算phi_n，加速幂模运算
        phi_n=(self.q-1)*(self.p-1)
        # 验证
        if ((numbthy.power_mod(acc, a%phi_n, self.n)) * (numbthy.power_mod(d, x%phi_n, self.n)))% (self.n) == self.g :
            return True
        else:
            return False
        
    
    def prove_membership(self, x, x_p):
        '''
        证明元素的存在性
        input:
            x - 要证明存在的元素，一个素数
            x_p - 预先发送给服务器的乘积
        output:
            pi - 证明。若返回None，说明str其实不存在于x_p对应的集合。
        '''        

        # 检查x是否被x_p整除
        if x_p%x != 0:
            return None

        # 计算指数x_p/x
        e=x_p//x
        phi_n=(self.p-1)*(self.q-1)

        # 生成证明pi，并用phi_n优化
        pi=numbthy.power_mod(self.g, e%phi_n, self.n)
        return pi
    

    def verify_membership(self, pi, acc, x):
        '''
        验证存在性证明
        input:
            pi - 证明
            acc - acc值
            x - 要验证存在的元素，字符串形式
        output:
            flag - 若为True，验证通过；若为False，验证未通过，说明proof是伪造的
        '''

        # 验证，并用phi_n优化
        phi_n=(self.p-1)*(self.q-1)
        if numbthy.power_mod(pi, x%phi_n, self.n)==acc:
            return True
        else:
            return False