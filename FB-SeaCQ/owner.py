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

    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)

    # ADS_w，将会发送给区块链。key为w（str类型），value为对应的Acc值（int类型）
    ADS_w=dict()
    # ADS_fid，将会发送给区块链。key为fid（str类型），value为对应的Acc值（int类型）
    ADS_fid=dict()

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
        # 素数集合X_w，保存w对应的id的素数
        X_w=set()
        # 初始化st为全0的16字节bytes
        st_old=bytes(16)

        # 遍历id集合
        aes=AES.new(key=k2,mode=AES.MODE_ECB)
        for fid in fid_set:
            # 随机生成新的st
            st_new=os.urandom(16)
            # 生成location
            loc=hmac.new(key=t_w,msg=st_new,digestmod='shake128').digest()
            # fid的密文
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

        # 计算X_w对应的Acc
        Acc_w, _=msa.genAcc(X_w)
        # 将Acc_w加入ADS
        ADS_w[w]=Acc_w
    
    # 计算每个文件对应的Acc_fid和x_p
    for fid,wset in dataset.items():
        # 计算fid的tag
        t_fid=hmac.new(key=k1,msg=fid.encode('utf-8'),digestmod='shake128').digest()
        # 计算文件中关键字对应的素数集合
        X_id=set()
        for w in wset:
            x=Accumulator.str2prime(w)
            X_id.add(x)
        Acc_fid,P_fid=msa.genAcc(X_id)

        # 将t_fid,P_fid加入索引
        index2[t_fid]=P_fid
        # 将Acc_fid加入ADS
        ADS_fid[fid]=Acc_fid

    # 调用智能合约
    batch_size=200
    # 将ADS_w批量存入区块链
    gas_w=batch_add(ADS_w, 1, batch_size,web3,contract)
    gas_fid=batch_add(ADS_fid, 2, batch_size,web3,contract)
    # 总的gas
    gas=gas_w+gas_fid

    # 将密钥和构建的两个索引返回
    return k1,k2,index1,index2,ST,gas




def batch_add(ADS:Dict[str,int], type:int, batch_size:int, web3, contract):
    '''
    setup阶段，调用智能合约，将生成的ADS字典分批加入区块链。可能存在一部分元素不足batch_size，最后当作一个batch处理。
    input:
        ADS_w -  setup阶段生成的字典，key为w或fid，value为对应的Acc
        type - 若type==1，字典的key为w；若type==2，字典的key为w
        batch_size - 每个batch的大小
        web3 - Web3对象
        contract - 合约对象
    output:
        gas - 花费的gas
    '''
    # 计算ADS的size
    total_size=len(ADS)

    # 计算要分多少个batch
    math.ceil(total_size/batch_size)

    # 将数据按照batch_size分组
    # 剩余未被处理的k-v pair数
    remain_size=total_size
    # 消耗的gas
    gas=0
    while remain_size>0:
        # 当前批次的大小
        current_size=0
        if remain_size>=batch_size:
            current_size=batch_size
        else:
            current_size=remain_size
        
        # 将current_size大小的数据从ADS中取出，并转换为两个list，分别储存key和value
        # 从ADS中取出current_size个k-v pair
        k_list=random.sample(list(ADS.keys()),current_size)
        v_list=[ADS[k] for k in k_list]
        # 从ADS中删除这些数据
        for k in k_list:
            ADS.pop(k)
        
        # 调用智能合约，将两个list发送至合约，从而设置合约中的mapping
        # 首先将两个list中的元素转换为ABI要求的数据类型
        _k_list=[Web3.toBytes(text=k.zfill(16)) for k in k_list]
        _v_list=[Web3.toBytes(int(v)) for v in v_list]
        # 调用合约，并await，得到gas消耗
        # 通过type参数指定存入合约的哪个mapping
        tx_hash=contract.functions.batch_setADS(_k_list, _v_list, current_size, type).transact({
            'from':web3.eth.accounts[0], 
            'gasPrice': web3.eth.gasPrice, 
            'gas': web3.eth.getBlock('latest').gasLimit})
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
        gas += tx_receipt['gasUsed']

        # 更新剩余数量
        remain_size=remain_size-current_size

    return gas




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




def verify(w:str, P_Q:int, result:Set[Tuple[bytes,Any,int]], web3, contract, k2:bytes):
    '''
    验证服务器返回的查询结果。
    input:
        w - 用户此前从Q中选定的关键字
        P_Q - Q中所有 关键字对应素数的乘积
        result - 服务器返回的查询结果
        web3 - web3对象
        contract - 合约对象
        k2 - 密钥k2
    output:
        flag - 标识验证是否通过。若为True，验证通过；若为False，验证失败
        R - 查询结果的明文。一个集合，元素为str。
    '''

    # 解密密钥
    k2='XJTUOSV2'.zfill(16).encode('utf-8')
    aes=AES.new(key=k2,mode=AES.MODE_ECB)
    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)
    
    # X_w储存w对应的fid的素数
    X_w=set()
    # 储存匹配查询条件的fid
    R=set()

    # 对w对应的链进行解密，得到fid和t_fid
    for tup in result:
        c_fid=tup[0]
        pi=tup[1]
        type=tup[2]
        # 解密c_fid，得到fid的16字节形式
        fid_bytes=aes.decrypt(c_fid).decode('utf-8')
        # 去掉填充，得到fid的字符串形式
        fid=fid_bytes.lstrip('0')

        # 从区块链中读取Acc_fid的字节形式，并转换为大整数
        Acc_fid_bytes=contract.functions.getADS(Web3.toBytes(text=fid.zfill(16)), 2).call()
        Acc_fid=Web3.toInt(Acc_fid_bytes)

        # 验证
        if type==0:
            # 取出p=P_Q/gcd(P_fid,P_Q)
            p=tup[3]

            # 验证不匹配P_Q
            if (P_Q%p!=0) or (not msa.verify_non_membership(pi[0],pi[1],Acc_fid,p)):
                print("correctness verification failed")
                return False,R
            else:
                X_w.add(Accumulator.str2prime(fid))
        elif type==1:
            # 验证P_Q存在
            if not msa.verify_membership(pi,Acc_fid,P_Q):
                print("correctness verification failed")
                return False,R
            else:
                X_w.add(Accumulator.str2prime(fid))
                R.add(fid)

    # 验证完整性
    # 从区块链中读取Acc_w的字节形式，
    Acc_w_bytes=contract.functions.getADS(Web3.toBytes(text=w.zfill(16)), 1).call()
    Acc_w=Web3.toInt(Acc_w_bytes)

    # 根据X_w计算Acc，并于Acc_w对比，判断是否相等
    Acc,_=msa.genAcc(X_w)
    if Acc!=Acc_w:
        print("completeness verification failed")
        return False, R

    return True, R


def update(ST, op, w, fid, P_fid, web3, contract):
    '''
    根据操作类型op对外包数据进行更新
    input:
        ST - 一个字典，储存每个关键字的st。key为w（str类型），value为对应的st_c（bytes类型）
        op - 操作类型。一个字符串，'add'或'del'
        w - 要插入的关键字。str类型。
        fid - w对应的fid。str类型
        P_fid - 服务器端保存的fid对应的素数乘积
    '''
    # 根据op类型调用相应接口
    if op=='add':
        update_add()
    elif op=='del':
        update_del()



def update_add(ST, w, fid, P_fid, web3, contract):
    '''
    将(w,id)加入数据库
    input:
        ST - 一个字典，储存每个关键字的st。key为w（str类型），value为对应的st_c（bytes类型）
        w - 要插入的关键字。str类型。
        fid - w对应的fid。str类型
        P_fid - 服务器端保存的fid对应的素数乘积
    '''

    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)
    # 生成对称加密密钥k1,k2
    k1='XJTUOSV1'.zfill(16).encode('utf-8')
    k2='XJTUOSV2'.zfill(16).encode('utf-8')

    aes=AES.new(key=k2,mode=AES.MODE_ECB)

    # 生成w对应的tag
    t_w=hmac.new(key=k1,msg=w.encode('utf-8'),digestmod='sha256').digest()

    # 获取w对应的旧的st
    # 若数据库中尚不存在w，则在ST中创建新条目
    st_old=bytes(16)
    if w in ST:
        st_old=ST[w]

    # 为(w,id)生成新的st
    st_new=os.urandom(16)

    # 计算插入的location
    loc=hmac.new(key=t_w,msg=st_new,digestmod='shake128').digest()
    # fid的密文
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

    # 从区块链中取回Acc_w和Acc_fid
    Acc_w_bytes=contract.functions.getADS(Web3.toBytes(text=w.zfill(16)), 1).call()
    Acc_w=Web3.toInt(Acc_w_bytes)
    Acc_fid_bytes=contract.functions.getADS(Web3.toBytes(text=fid.zfill(16)), 2).call()
    Acc_fid=Web3.toInt(Acc_fid_bytes)

    #  更新Acc_w和Acc_fid
    Acc_w=msa.add_element(Acc_w, Accumulator.str2prime(w))
    Acc_fid=msa.add_element(Acc_fid,Accumulator.str2prime(fid))

    # 更新P_fid


    # 调用智能合约，更新区块链状态
    











def update_del():
    '''

    '''
    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)
    # 生成对称加密密钥k1,k2
    k1='XJTUOSV1'.zfill(16).encode('utf-8')
    k2='XJTUOSV2'.zfill(16).encode('utf-8')