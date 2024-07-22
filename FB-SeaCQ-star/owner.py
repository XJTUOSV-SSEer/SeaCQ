from distutils.command.install_egg_info import to_filename
from itertools import accumulate
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


def verify(w:str, P_Q:int, correctness_proof:Set[Tuple], pi4:int, web3, contract, k2:bytes):
    '''
    验证服务器返回的查询结果。
    input:
        w - 用户此前从Q中选定的关键字
        P_Q - Q中所有 关键字对应素数的乘积
        correctness_proof - 服务器返回的正确性证明，元素为元组类型(Acc_fid, c_fid,pi1,pi2,pi3,type[,p])。
                            Acc_fid为该文件的Acc
                            c_fid为密文。
                            pi1为该文件关于Acc_id的存在证明/不存在证明;
                            pi2为t_id关于Acc_id的存在证明；
                            pi3为Acc_id关于ADS的存在证明；
                            type标识pi1的类型：若是存在证明，type==1; 若是不存在证明，type==0。当是不存在证明时，额外返回p，即
                            p=P_Q/gcd(P_fid,P_Q)
        pi4 - 用于证明Acc_w属于ADS
        web3 - web3对象
        contract - 合约对象
        k2 - 密钥k2
    output:
        flag - 标识验证是否通过。若为True，验证通过；若为False，验证失败
        R - 查询结果的明文。一个集合，元素为str。
    '''

    # 解密密钥
    k1='XJTUOSV1'.zfill(16).encode('utf-8')
    k2='XJTUOSV2'.zfill(16).encode('utf-8')
    aes=AES.new(key=k2,mode=AES.MODE_ECB)
    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)

    # X_w储存w对应的fid的素数和t_w对应的素数
    X_w=set()
    t_w=hmac.new(key=k1,msg=w.encode('utf-8'),digestmod='sha256').digest()
    X_w.add(Accumulator.str2prime(str(t_w)))
    # 储存匹配查询条件的fid
    R=set()

    # 从区块链取回ADS
    ADS_bytes = contract.functions.get().call()
    ADS=Web3.toInt(ADS_bytes[0])
    
    # 对w对应的链进行解密，得到fid和t_fid
    for tup in correctness_proof:
        Acc_fid=tup[0]
        c_fid=tup[1]
        pi1=tup[2]
        pi2=tup[3]
        pi3=tup[4]
        type=tup[5]

        # 解密得到fid，并计算t_fid
        fid_bytes=aes.decrypt(c_fid).decode('utf-8')
        # 去掉填充，得到fid的字符串形式
        fid=fid_bytes.lstrip('0')
        t_fid=hmac.new(key=k1,msg=fid.encode('utf-8'),digestmod='shake128').digest()

        # 验证t_fid是否正确：
        # 使用pi2验证t_fid属于Acc_fid
        msa.verify_membership(pi2, Acc_fid, Accumulator.str2prime(str(t_fid)))
        # 使用pi3验证Acc_fid属于ADS
        msa.verify_membership(pi3, ADS, Accumulator.str2prime(str(Acc_fid)))

        # 验证fid中的关键字是否属于Acc_fid
        if type==0:
            # 取出p=P_Q/gcd(P_fid,P_Q)
            p=tup[6]
            # 验证不匹配P_Q
            if (P_Q%p!=0) or (not msa.verify_non_membership(pi1[0], pi1[1], Acc_fid, p)):
                print("correctness verification failed")
                return False,R
            else:
                X_w.add(Accumulator.str2prime(fid))
        elif type==1:
            # 验证P_Q存在
            if not msa.verify_membership(pi1, Acc_fid, P_Q):
                print("correctness verification failed")
                return False,R
            else:
                X_w.add(Accumulator.str2prime(fid))
                R.add(fid)
    
    # 验证完整性
    # 根据X_w计算Acc_w
    Acc_w, _ = msa.genAcc(X_w)
    # 验证Acc_w是否属于ADS
    if not msa.verify_membership(pi4, ADS, Accumulator.str2prime(str(Acc_w))):
        print("completeness verification failed")
        return False, R
    
    return True, R



def update(ST:Dict[str,bytes], op:str, w:str, fid:str, index2:Dict[bytes,int], index3:Dict[bytes,int],
           web3, contract):
    '''
    根据操作类型op对外包数据进行更新
    input:
        ST - 一个字典，储存每个关键字的st。key为w（str类型），value为对应的st_c（bytes类型）
        op - 操作类型。一个字符串，'add'或'del'
        w - 要插入的关键字。str类型。
        fid - w对应的fid。str类型
        index2 - 一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
        index3 - 一个字典。key为t_w(bytes类型)，value为w对应的P_w(大整数)。
    output:
        若op==add，返回一个元组：((loc,c_fid,c_st), (t_fid,P_fid_new), (t_w,P_w_new), P_new)
        若op==del，返回一个元组：(t_fid,P_fid)
    note:
        这里省略了对服务器返回的P_w,P_fid,Acc_w,Acc_fid验证的过程。
    '''
    # 根据op类型调用相应接口
    if op=='add':
        return update_add(ST, w, fid, index2, index3, web3, contract)
    elif op=='del':
        return update_del(w, fid, index2, index3, web3, contract)



def update_add(ST:Dict[str,bytes], w:str, fid:str, index2:Dict[bytes,int], index3:Dict[bytes,int], web3, contract):
    '''
    将(w,id)加入数据库。
    input:
        ST - 一个字典，储存每个关键字的st。key为w（str类型），value为对应的st_c（bytes类型）
        w - 要插入的关键字。str类型。
        fid - w对应的fid。str类型
        index2 - 用于获取P_fid。若fid尚不存在，设置P_fid_old=1
        index3 - 用于获取P_w。若w尚不存在，设置P_w_old=1
    output:
        (loc,c_fid,c_st) - loc为储存位置，c_fid为fid的密文（bytes类型），c_st为逻辑指针（bytes）类型
        (t_fid,P_fid_new) - t_fid为fid的tag，P_fid为fid对应的新素数乘积。
        (t_w,P_w_new) - t_w为w的tag，P_w为w对应的新素数乘积
        P_new - 对应于ADS的新素数乘积
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
    # fid的tag
    t_fid=hmac.new(key=k1,msg=fid.encode('utf-8'),digestmod='shake128').digest()

    # 从index2中读取P_fid。若fid尚不存在，设置P_fid_old=1
    P_fid_old=1
    if t_fid in index2:
        P_fid_old=index2[t_fid]
    # 从index3中读取P_w。若w尚不存在，设置P_w_old=1
    P_w_old=1
    if t_w in index3:
        P_w_old=index3[t_w]
    


    # 计算旧的Acc_w和Acc_fid
    Acc_w_old=msa.genAcc2(P_w_old)
    Acc_fid_old=msa.genAcc2(P_fid_old)


    # 从区块链中读取ADS和P
    l_bytes = contract.functions.get().call()
    ADS_old=Web3.toInt(l_bytes[0])
    P_old=Web3.toInt(l_bytes[1])
    



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
    
    # 生成c_st
    # H(t_w,st_new)
    part1=hmac.new(key=t_w, msg=st_new, digestmod='sha256').digest()
    # st_old || t_fid
    part2=st_old+t_fid
    # 异或
    c_st=bytes(a^b for a,b in zip(part1,part2))


    # 更新P_fid，并计算Acc_fid
    # 若不存在t_fid对应的条目，则需要新建P_fid    
    P_fid_new=P_fid_old*Accumulator.str2prime(w)
    if P_fid_old==1:
        P_fid_new=P_fid_new*Accumulator.str2prime(str(t_fid))
    Acc_fid_new=msa.genAcc2(P_fid_new)

    # 更新P_w，并计算Acc_w
    # 若不存在t_w对应的条目，则需要新建P_w
    P_w_new=P_w_old*Accumulator.str2prime(fid)
    if P_w_old==1:
        P_w_new=P_w_new*Accumulator.str2prime(str(t_w))
    Acc_w_new=msa.genAcc2(P_w_new)


    # 更新P
    # 先将P除去(H_p(Acc_w_old)*H_p(Acc_fid_old))，要求P_w_old和P_fid_old不为1
    a=1
    if P_w_old!=1:
        a=Accumulator.str2prime(str(Acc_w_old))
    b=1
    if P_fid_old!=1:
        b=Accumulator.str2prime(str(Acc_fid_old))

    P_new=P_old // (a*b)

    # 乘以(H_p(Acc_w_new)*H_p(Acc_fid_new))
    P_new=P_new*(Accumulator.str2prime(str(Acc_w_new)) * Accumulator.str2prime(str(Acc_fid_new)))

    # 更新ADS，并将ADS,P都发送到区块链
    ADS=msa.genAcc2(P_new)
    tx_hash=contract.functions.set(Web3.toBytes(ADS), Web3.toBytes(P_new)).transact({
            'from':web3.eth.accounts[0], 
            'gasPrice': web3.eth.gasPrice, 
            'gas': web3.eth.getBlock('latest').gasLimit})
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
    gas = tx_receipt['gasUsed']

    # 更新ST
    ST[w]=st_new

    # 返回对server索引的更新
    return (loc, c_fid, c_st), (t_fid, P_fid_new), (t_w, P_w_new), P_new







def update_del(w:str, fid:str, index2:Dict[bytes,int], index3:Dict[bytes,int], web3, contract):
    '''
    将(w,id)从数据库中删除。
    input:
        w - 要删除的关键字。str类型。
        fid - w对应的fid。str类型
        index2 - 用于获取P_fid。若fid尚不存在，设置P_fid_old=1
        index3 - 用于获取P_w。若w尚不存在，设置P_w_old=1
    output:
        (t_fid,P_fid_new) - t_fid为fid的tag，P_fid为fid对应的新素数乘积。
        P_new - 对应于ADS的新素数乘积
    '''

    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)
    # 生成对称加密密钥k1,k2
    k1='XJTUOSV1'.zfill(16).encode('utf-8')
    k2='XJTUOSV2'.zfill(16).encode('utf-8')

    # 从区块链中读取ADS和P
    l_bytes = contract.functions.get().call()
    ADS_old=Web3.toInt(l_bytes[0])
    P_old=Web3.toInt(l_bytes[1])


    # fid的tag
    t_fid=hmac.new(key=k1,msg=fid.encode('utf-8'),digestmod='shake128').digest()
    # 从index2中读取P_fid
    P_fid_old=index2[t_fid]
    # 计算旧的Acc_fid
    Acc_fid_old=msa.genAcc2(P_fid_old)

    # 计算新的P_fid
    P_fid_new=P_fid_old // Accumulator.str2prime(w)
    # 计算新的Acc_fid
    Acc_fid_new=msa.genAcc2(P_fid_new)

    # 更新P
    P_new = P_old * Accumulator.str2prime(str(Acc_fid_new)) // Accumulator.str2prime(str(Acc_fid_old))
    # 更新ADS
    ADS=msa.genAcc2(P_new)

    # 将ADS,P都发送到区块链
    tx_hash=contract.functions.set(Web3.toBytes(ADS), Web3.toBytes(P_new)).transact({
            'from':web3.eth.accounts[0], 
            'gasPrice': web3.eth.gasPrice, 
            'gas': web3.eth.getBlock('latest').gasLimit})
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
    gas = tx_receipt['gasUsed']

    # 返回
    return (t_fid, P_fid_new), P_new