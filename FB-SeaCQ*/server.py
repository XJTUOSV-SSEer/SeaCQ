import Accumulator
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple, type_check_only
from web3 import Web3
import json
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
        correctness_proof - 查询结果及正确性证明。一个集合，其中元素为元组类型(Acc_fid, c_fid,pi1,pi2,pi3,type[,p])。c_fid为密文。
                 Acc_fid为该文件的Acc
                 pi1为该文件关于Acc_id的存在证明/不存在证明;
                 pi2为t_id关于Acc_id的存在证明；
                 pi3为Acc_id关于ADS的存在证明；
                 type标识pi1的类型：若是存在证明，type==1; 若是不存在证明，type==0。当是不存在证明时，额外返回p，即
                 p=P_Q/gcd(P_fid,P_Q)
        completeness_proof - 完整性证明pi4，Acc_w关于ADS的存在证明。
    '''

    # 正确性证明
    correctness_proof=set()

    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)

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

        # 找到fid对应的P_fid
        P_fid=index2[t_fid]
        # 计算Acc_fid
        Acc_fid=msa.genAcc2(P_fid)
        # 生成证明pi2，证明t_fid属于Acc_fid
        pi2 = msa.prove_membership(Accumulator.str2prime(str(t_fid)), P_fid)
        # 生成证明pi1，证明Acc_fid属于ADS
        pi3 = msa.prove_membership(Accumulator.str2prime(str(Acc_fid)), P)

        # 判断P_fid能否整除P_Q
        type=0
        pi=None
        if P_fid % P_Q==0:
            # 该文件匹配查询条件Q，生成存在证明
            pi1=msa.prove_membership(P_Q,P_fid)
            type=1

            # 将密文与证明加入结果
            t=(Acc_fid, c_fid, pi1, pi2, pi3, type)
        else:
            
