from distutils.command.install_egg_info import to_filename
import Accumulator
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple,Any
import random
from web3 import Web3
import json
import math
import os


def setup(dataset:Dict[str,Set[str]], web3, contract):
    '''
    用户初始化，加密索引。返回两个索引，并在函数内完成智能合约的调用。
    input:
        dataset - 数据集。一个字典。key为文件id，字符串类型。value为文件中的关键字集合，集合中元素为字符串类型。
        web3 - web3对象
        contract - 智能合约对象
    output:
        k1 - PRF的密钥，用于生成tag。bytes类型
        k2 - 对称加密密钥。bytes类型。bytes类型
        index1 - 一个字典。key为location（bytes类型）；value为一个元组(c_fid,c_st)，c_fid为fid的密文（bytes类型），
                 c_st为逻辑指针（bytes）类型
        index2 - 一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
        index3 - 一个字典。key为t_w(bytes类型)，value为w对应的P_w(大整数)
        P - ADS对应的素数乘积
        ST - 一个字典。key为w（str类型），value为对应的st_c（bytes类型）
        gas - 消耗的gas
    '''

    # 参数长度：
    # st_c - 16bytes
    # loc - 16bytes
    # t_id - 16bytes

    # 索引，将会发送至服务器
    index1=dict()
    index2=dict()
    index3=dict()

    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)

    # ADS，一个大整数，将发送给区块链
    ADS=0
    # 对应于ADS的素数乘积，将发送给区块链
    P=0
    # 储存所有的Acc_w和Acc_fid对应的素数
    acc_list=set()

    # 一个字典，储存每个关键字对应的st。key为str类型，value为bytes类型
    ST=dict()

    # 生成对称加密密钥k1,k2
    k1='XJTUOSV1'.zfill(16).encode('utf-8')
    k2='XJTUOSV2'.zfill(16).encode('utf-8')

    # 根据数据集，构造倒排索引（字典类型,Dict[str,Set[str]]）
    inv_index=dict()
    for fid,w_set in dataset.items():
        for w in w_set:
            # 关键字尚不存在，需要创建一个k-v pair
            if w not in inv_index:
                # 创建一个空集合
                inv_index[w]=set()
            inv_index[w].add(fid)

    # 遍历倒排索引，计算密文和Acc_w
    for w, fid_set in inv_index.items():
        # 生成w的tag
        t_w=hmac.new(key=k1,msg=w.encode('utf-8'),digestmod='sha256').digest()
        # 素数集合X_w，保存w对应的id的素数和t_w对应的素数
        X_w=set()
        X_w.add(Accumulator.str2prime(str(t_w)))
        # 初始化st为全0的16字节bytes
        st_old=bytes(16)

        # 遍历id集合
        aes=AES.new(key=k2,mode=AES.MODE_ECB)
        for fid in fid_set:
            # 随机生成新的st
            st_new=os.urandom(16)
            # 生成location
            loc=hmac.new(key=t_w,msg=st_new,digestmod='shake128').digest()
            # fid的密文cfid
            c_fid=aes.encrypt(fid.zfill(16).encode('utf-8'))
            # fid的tag
            t_fid=hmac.new(key=k1,msg=fid.encode('utf-8'),digestmod='shake128').digest()

            # 生成c_st
            # H(t_w,st_new)
            part1=hmac.new(key=t_w, msg=st_new, digestmod='sha256').digest()
            # st_old || t_fid
            part2=st_old+t_fid
            # 异或
            c_st=bytes(a^b for a,b in zip(part1,part2))

            # 更新X_w
            x=Accumulator.str2prime(fid)
            X_w.add(x)

            # 储存在索引中
            index1[loc]=(c_fid,c_st)

            # 更新st_c
            st_old=st_new

        # 更新ST
        ST[w]=st_old

        # 计算X_w对应的Acc和素数乘积P_w
        Acc_w, P_w=msa.genAcc(X_w)
        acc_list.add(Accumulator.str2prime(str(Acc_w)))
        # 将P_w加入index3
        index3[t_w]=P_w
    
    # 计算每个文件对应的Acc_fid和x_p
    for fid,wset in dataset.items():
        # 计算fid的tag
        t_fid=hmac.new(key=k1,msg=fid.encode('utf-8'),digestmod='shake128').digest()
        # X_id，储存fid对应所有w对应的素数和t_fid对应的素数
        X_id=set()
        X_id.add(Accumulator.str2prime(str(t_fid)))

        for w in wset:
            x=Accumulator.str2prime(w)
            X_id.add(x)
        Acc_fid,P_fid=msa.genAcc(X_id)

        # 将t_fid,P_fid加入索引
        index2[t_fid]=P_fid
        # 将Acc_fid加入acc_list
        acc_list.add(Accumulator.str2prime(str(Acc_fid)))    

    # 对Acc_list，计算对应的素数乘积和Acc
    ADS, P=msa.genAcc(acc_list)
    
    # 调用智能合约，储存ADS和P。获取消耗的Gas
    tx_hash=contract.functions.set(Web3.toBytes(ADS), Web3.toBytes(P)).transact({
            'from':web3.eth.accounts[0], 
            'gasPrice': web3.eth.gasPrice, 
            'gas': web3.eth.getBlock('latest').gasLimit})
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
    gas = tx_receipt['gasUsed']

    # 返回参数
    return k1,k2,index1,index2,index3,P,ST,gas


def search(Q:Set[str],ST:Dict[str,int], k1:bytes):
    '''
    生成查询token
    input:
        Q - 查询条件。一个集合，Set[str]类型，储存要查询的关键字
        ST - 一个字典，储存每个关键字的st。key为w（str类型），value为对应的st_c（bytes类型）
        k1 - 密钥k1
    output:
        w - 从Q中选出的w
        t_w - 从Q中选出的w的tag
        P_Q - Q中所有关键字对应素数的乘积
        st - w对应的st
    '''
    
    # 从Q中任选一个关键字作为w
    w=random.choice(list(Q))
    # 计算t_w
    t_w=hmac.new(key=k1,msg=w.encode('utf-8'),digestmod='sha256').digest()

    # 计算P_Q
    P_Q=1
    for s in Q:
        P_Q=P_Q * Accumulator.str2prime(s)

    # 返回token
    return w, t_w,P_Q,ST[w]