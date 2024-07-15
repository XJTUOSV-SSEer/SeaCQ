import Accumulator
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple
import random


def setup(dataset:Dict[str,Set[str]]):
    '''
    用户初始化，加密索引。返回两个索引，并在函数内完成智能合约的调用。
    input:
        dataset - 数据集。一个字典。key为文件id，字符串类型。value为文件中的关键字集合，集合中元素为字符串类型。
    output:
        k1 - PRF的密钥，用于生成tag。bytes类型
        k2 - 对称加密密钥。bytes类型。bytes类型
        index1 - 一个字典。key为location（bytes类型）；value为一个元组(c_fid,t_fid)，c_fid为fid的密文（bytes类型），t_fid为fid的tag（bytes类型）
        index2 - 一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
        ST - 一个字典。key为w（str类型），value为w的计数器（int类型）
    '''

    # 索引，将会发送至服务器
    index1=dict()
    index2=dict()
    # 累加器
    msa=Accumulator.Accumulator(p=252533614457563255817176556954479732787,
                                q=326896810465200637570669519551882712907,
                                g=65537)
    # ADS，将会发送给区块链。key为w或fid（str类型），value为对应的Acc值（int类型）
    ADS=dict()
    # 一个字典，储存每个关键字对应的计数器。key为str类型，value为int类型
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
        # 计数器
        c=1
        # 素数集合X_w，保存w对应的id的素数
        X_w=set()

        # 遍历id集合
        aes=AES.new(key=k2)
        for fid in fid_set:
            # 生成location
            loc=hmac.new(key=t_w,msg=c.to_bytes(length=4,byteorder='big',signed=True),digestmod='sha256').digest()
            # fid的密文
            c_fid=aes.encrypt(fid.zfill(16).encode('utf-8'))
            # fid的tag
            t_fid=hmac.new(key=k1,msg=fid.encode('utf-8'),digestmod='sha256').digest()
            # 更新X_w
            x=Accumulator.str2prime(fid)
            X_w.add(x)
            c=c+1
            # 储存在索引中
            index1[loc]=(c_fid,t_fid)
        
        # 更新计数器
        c=c-1
        ST[w]=c
        # 计算X_w对应的Acc
        Acc_w, _=msa.genAcc(X_w)
        # 将Acc加入ADS
        ADS[w]=Acc_w
    
    # 计算每个文件对应的Acc_fid和x_p
    for fid,wset in dataset.items():
        # 计算fid的tag
        t_fid=hmac.new(key=k1,msg=fid.encode('utf-8'),digestmod='sha256').digest()
        # 计算文件中关键字对应的素数集合
        X_id=set()
        for w in wset:
            x=Accumulator.str2prime(w)
            X_id.add(x)
        Acc_fid,P_fid=msa.genAcc(X_id)
        # 将t_fid,P_fid加入索引
        index2[t_fid]=P_fid
        # 将Acc_fid加入ADS
        ADS[fid]=Acc_fid
    
    # 调用智能合约
        

    # 将密钥和构建的两个索引返回
    return k1,k2,index1,index2,ST





        
    


def search(Q:Set[str],ST:Dict[str,int]):
    '''
    生成查询token
    input:
        Q - 查询条件。一个集合，Set[str]类型，储存要查询的关键字
        ST - 一个字典，储存每个关键字的计数器。key为w（str类型），value为w的计数器（int类型）
    output:
        t_w - 从Q中选出的w
        P_Q - Q中除w之外，其余关键字对应素数的乘积
        c - w对应的计数器
    '''
    # 从Q中任选一个关键字作为w
    w=random.choice(list(Q))
    # 计算t_w
    t_w=hmac.new(key=k1,msg=w.encode('utf-8'),digestmod='sha256').digest()
    # 计算P_Q
    P_Q=1
    for s in Q:
        if s!=w:
            P_Q=P_Q * Accumulator.str2prime(s)
    
    # 返回token
    return t_w,P_Q,ST[w]

            




def update():
    '''
    
    '''

def verify():
    '''

    '''


if __name__ == "__main__":
    dataset={'f1':{'ab','cd'},'f2':{'ef','gh'}}
    k1,k2,I1,I2,ST=setup(dataset)
    print(k1)
    print(k2)
    print(I1)
    print(I2)
    print(ST)