import Accumulator
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple,Any
import random
from web3 import Web3
import json
import math


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
        index1 - 一个字典。key为location（bytes类型）；value为一个元组(c_fid,t_fid)，c_fid为fid的密文（bytes类型），t_fid为fid的tag（bytes类型）
        index2 - 一个字典。key为t_fid（bytes类型），value为该文件对应的P_fid（一个大整数）。
        ST - 一个字典。key为w（str类型），value为对应的st_c（bytes类型）
        gas - 消耗的gas
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

    
