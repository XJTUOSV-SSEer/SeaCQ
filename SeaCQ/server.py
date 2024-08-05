import Accumulator
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple
from web3 import Web3
import json
import numbthy
import time


def search(t_w:bytes,P_Q,c,index1:Dict[bytes,Tuple[bytes,bytes]],index2:Dict[bytes,int]):
    '''
    服务器根据用户提供的token，执行搜索。
    input:
        t_w - 从Q中选出的w的tag
        P_Q - Q中除w之外，其余关键字对应素数的乘积
        c - w对应的计数器
        index1 - 索引1，一个字典。key为location（bytes类型）；value为一个元组(c_fid,t_fid)，c_fid为fid的密文（bytes类型），
                 t_fid为fid的tag（bytes类型）
        index2 - 索引2，一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
    output:
        result - 查询结果及证明。一个集合，其中元素为元组类型(c_fid,pi,type[,p])。c_fid为密文，pi为该文件对应的存在证明/不存在证明，
                 type标识pi的类型：若是存在证明，type==1; 若是不存在证明，type==0。当是不存在证明时，额外返回p，即
                 p=P_Q/gcd(P_fid,P_Q)
        t1 - find result time
        t2 - generate VO time
    '''
    # 结果
    result=set()

    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)

    t1_s = time.time()
    t2 = 0
    # 遍历w对应的链
    while c>0:
        # 计算location
        loc=hmac.new(key=t_w,msg=c.to_bytes(length=4,byteorder='big',signed=True),digestmod='sha256').digest()
        # 取出location处的数据
        c_fid,t_fid=index1[loc]
        # 找到fid对应的P_fid
        P_fid=index2[t_fid]
        # 判断P_fid能否整除P_Q
        type=0
        pi=None
        if P_fid%P_Q==0:
            t2_s = time.time()
            # 该文件匹配查询条件Q，生成存在证明
            pi=msa.prove_membership(P_Q,P_fid)
            t2_e = time.time()
            t2 = t2+t2_e-t2_s
            type=1
            # 将密文与证明加入结果
            t=(c_fid,pi,type)
            result.add(t)
        else:
            # 求解P_fid和P_Q的最大公约数
            gcd=numbthy.gcd(P_fid,P_Q)

            # P_Q / gcd
            p=P_Q//gcd

            t2_s = time.time()

            # 该文件不匹配Q，生成不存在证明
            pi=msa.prove_non_membership(p,P_fid)

            t2_e = time.time()
            t2 = t2+t2_e-t2_s

            type=0

            t=(c_fid,pi,type,p)
            result.add(t)
        
        # 更新计数器
        c=c-1
    

    t1_e = time.time()
    t1 = t1_e - t1_s -t2
    # 返回结果
    return result, t1, t2