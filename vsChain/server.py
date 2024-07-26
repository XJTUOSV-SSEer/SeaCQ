from web3 import Web3
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple,Any, List
import random
import binSearchTree


class server:
    '''
    服务器
    '''

    # CMAP，储存 k->v 的映射。k,v都是32字节bytes
    CMAP: Dict[bytes, bytes]

    # trees，储存每个w对应的二叉搜索树
    # tau_w->tree。静态储存树，将树结点储存在数组中
    trees: Dict[bytes, List[binSearchTree.binSearchTree]]

    