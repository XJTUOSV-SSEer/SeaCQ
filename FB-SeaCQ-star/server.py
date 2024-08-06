from pickletools import UP_TO_NEWLINE
import Accumulator
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple
from web3 import Web3
import json
import time
import numbthy


def search(t_w:bytes, P_Q, st, index1:Dict[bytes,Tuple[bytes,bytes]], index2:Dict[bytes,int], 
            index3:Dict[bytes,int], P:int):
    '''
    服务器根据用户提供的token，执行搜索。
    input:
        t_w - 从Q中选出的w的tag
        P_Q - Q中除w之外，其余关键字对应素数的乘积
        st - w对应的st
        index1 - 索引1，一个字典。key为location（bytes类型）；value为一个元组(c_fid,c_st)，c_fid为fid的密文（bytes类型），
                 c_st为fid的st（bytes类型）
        index2 - 索引2，一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
        index3 - 索引3，一个字典。key为t_w（bytes），value为w对应的P_w(一个大整数)
        P - ADS对应的素数乘积
    output:
        correctness_proof - 查询结果及正确性证明。一个集合，其中元素为元组类型(Acc_fid, c_fid,pi1,pi2,pi3,type[,p])。
                 Acc_fid为该文件的Acc
                 c_fid为密文。
                 pi1为该文件关于Acc_id的存在证明/不存在证明;
                 pi2为t_id关于Acc_id的存在证明；
                 pi3为Acc_id关于ADS的存在证明；
                 type标识pi1的类型：若是存在证明，type==1; 若是不存在证明，type==0。当是不存在证明时，额外返回p，即
                 p=P_Q/gcd(P_fid,P_Q)
        pi4 - 完整性证明pi4，Acc_w关于ADS的存在证明。
        t1 - find result time
        t2 - generate VO time
    '''

    # 正确性证明
    correctness_proof=set()

    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)
    
    t1_s = time.time()
    t2 = 0

    st_new=st
    # 遍历w对应的链
    while st_new!=bytes(16):
        # 计算location
        loc=hmac.new(key=t_w, msg=st_new, digestmod='shake128').digest()
        # 取出location处的数据
        c_fid,c_st=index1[loc]

        # 根据c_st，得到 st_old||t_fid
        # 异或
        tmp=bytes(a ^ b for a, b in zip(c_st, hmac.new(key=t_w, msg=st_new, digestmod='sha256').digest() ))
        # 切分，前16字节为st_old，后16字节为fid的tag
        st_old=tmp[:16]
        t_fid=tmp[16:]

        t2_s = time.time()

        # 找到fid对应的P_fid
        P_fid=index2[t_fid]
        # 计算Acc_fid
        Acc_fid=msa.genAcc2(P_fid)
        # 生成证明pi2，证明t_fid属于Acc_fid
        pi2 = msa.prove_membership(Accumulator.str2prime(str(t_fid)), P_fid)
        # 生成证明pi3，证明Acc_fid属于ADS
        pi3 = msa.prove_membership(Accumulator.str2prime(str(Acc_fid)), P)

        t2_e = time.time()
        t2 = t2+t2_e-t2_s

        # 判断P_fid能否整除P_Q
        type=0
        pi=None
        if P_fid % P_Q==0:
            t2_s = time.time()

            # 该文件匹配查询条件Q，生成存在证明
            pi1=msa.prove_membership(P_Q,P_fid)

            t2_e = time.time()
            t2 = t2+t2_e-t2_s

            type=1

            # 将密文与证明加入结果
            t=(Acc_fid, c_fid, pi1, pi2, pi3, type)
            correctness_proof.add(t)
        else:
            # 求解P_fid和P_Q的最大公约数
            gcd=numbthy.gcd(P_fid,P_Q)

            # P_Q / gcd
            p=P_Q//gcd

            t2_s = time.time()

            # 该文件不匹配Q，生成不存在证明
            pi1=msa.prove_non_membership(p,P_fid)

            t2_e = time.time()
            t2 = t2+t2_e-t2_s

            type=0

            # 将密文与证明加入结果
            t=(Acc_fid, c_fid, pi1, pi2, pi3, type, p)
            correctness_proof.add(t)
        # 更新st_new
        st_new=st_old

    t2_s = time.time()

    # 生成完整性证明，证明Acc_w属于ADS
    # 首先根据p_w计算Acc_w
    P_w=index3[t_w]
    Acc_w=msa.genAcc2(P_w)
    pi4=msa.prove_membership(Accumulator.str2prime(str(Acc_w)), P)

    t2_e = time.time()
    t2 = t2+t2_e-t2_s

    t1_e = time.time()
    t1 = t1_e - t1_s -t2

    # 返回
    return correctness_proof, pi4, t1, t2



def update(op:str, updtk: Tuple, index1:Dict[bytes,Tuple[bytes,bytes]], index2:Dict[bytes,int], index3:Dict[bytes,int]):
    '''
    根据op类型和owner返回的update token，对储存的索引进行更新
    input:
        op - 操作类型。一个字符串，'add'或'del'
        tpdtk - 若op==add，元组为((loc,c_fid,c_st), (t_fid,P_fid_new), (t_w, P_w_new), P_new)；
                若op==del，元组为((t_fid,P_fid),P)
        index1 - 索引1，一个字典。key为location（bytes类型）；value为一个元组(c_fid,c_st)，c_fid为fid的密文（bytes类型），
                 c_st为fid的st（bytes类型）
        index2 - 索引2，一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
        index3 - 索引3，一个字典。key为t_w（bytes），value为w对应的P_w(一个大整数)
    output:
        P - 更新后的P
    '''
    P=None
    if op == 'add':
        # 更新index1
        loc=updtk[0][0]
        c_fid=updtk[0][1]
        c_st=updtk[0][2]
        index1[loc]=(c_fid, c_st)
        # 更新index2
        t_fid=updtk[1][0]
        P_fid=updtk[1][1]
        index2[t_fid]=P_fid
        # 更新index3
        t_w=updtk[2][0]
        P_w=updtk[2][1]
        index3[t_w]=P_w
        # 更新后的P
        P=updtk[3]
    elif op=='del':
        # 更新index2
        t_fid=updtk[0][0]
        P_fid=updtk[0][1]
        index2[t_fid]=P_fid
        # 更新P
        P=updtk[1]
    
    return P