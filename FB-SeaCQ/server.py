import Accumulator
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple
from web3 import Web3
import json
import numbthy


def search(t_w:bytes, P_Q, st, index1:Dict[bytes,Tuple[bytes,bytes]], index2:Dict[bytes,int]):
    '''
    服务器根据用户提供的token，执行搜索。
    input:
        t_w - 从Q中选出的w的tag
        P_Q - Q中除w之外，其余关键字对应素数的乘积
        st - w对应的st
        index1 - 索引1，一个字典。key为location（bytes类型）；value为一个元组(c_fid,c_st)，c_fid为fid的密文（bytes类型），
                 c_st为fid的st（bytes类型）
        index2 - 索引2，一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
    output:
        result - 查询结果及证明。一个集合，其中元素为元组类型(c_fid,pi,type[,p])。c_fid为密文，pi为该文件对应的存在证明/不存在证明，
                 type标识pi的类型：若是存在证明，type==1; 若是不存在证明，type==0。当是不存在证明时，额外返回p，即
                 p=P_Q/gcd(P_fid,P_Q)
    '''
    
    # 结果
    result=set()

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

        # 判断P_fid能否整除P_Q
        type=0
        pi=None
        if P_fid%P_Q==0:
            # 该文件匹配查询条件Q，生成存在证明
            pi=msa.prove_membership(P_Q,P_fid)
            type=1
            # 将密文与证明加入结果
            t=(c_fid,pi,type)
            result.add(t)
        else:
            # 求解P_fid和P_Q的最大公约数
            gcd=numbthy.gcd(P_fid,P_Q)

            # P_Q / gcd
            p=P_Q//gcd

            # 该文件不匹配Q，生成不存在证明
            pi=msa.prove_non_membership(p,P_fid)
            type=0

            t=(c_fid,pi,type,p)
            result.add(t)
        
        # 更新st_new
        st_new=st_old
    
    # 返回结果
    return result



def update(op:str, updtk: Tuple, index1:Dict[bytes,Tuple[bytes,bytes]], index2:Dict[bytes,int]):
    '''
    根据op类型和owner返回的update token，对储存的索引进行更新
    input:
        op - 操作类型。一个字符串，'add'或'del'
        tpdtk - 若op==add，元组为((loc,c_fid,c_st),(t_fid,P_fid))；
                若op==del，元组为(t_fid,P_fid)
        index1 - 索引1，一个字典。key为location（bytes类型）；value为一个元组(c_fid,c_st)，c_fid为fid的密文（bytes类型），
                 c_st为fid的st（bytes类型）
        index2 - 索引2，一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
    '''
    if op=='add':
        #  更新index1和index2
        e1=updtk[0]
        e2=updtk[1]
        index1[e1[0]]=(e1[1], e1[2])
        index2[e2[0]]=e2[1]
    elif op=='del':
        e2=updtk
        index2[e2[0]]=e2[1]
