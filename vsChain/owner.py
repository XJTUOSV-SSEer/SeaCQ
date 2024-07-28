from web3 import Web3
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple,Any, List
import random
import binSearchTree



class onwer:
    '''
    owner类
    '''

    # 密钥K1, K2
    k1='XJTUOSV1'.zfill(16).encode('utf-8')
    k2='XJTUOSV2'.zfill(16).encode('utf-8')

    # DMAP，本地储存w的一些状态信息
    # 一个字典，键为关键字，值为一个元组，分别为alpha, beta, H_w_upd, flag
    # 其中，H_w_upd使用keccak256计算，为32字节
    DMAP: Dict[str, Tuple[int, int, bytes, bool]]=dict()



    def setup(self, dataset: Dict[str, Set[int]]):
        '''
        初始化数据库。
        input:
            dataset - 倒排索引数据集。一个字典，关键字为字符串类型，文件id为正整数类型
        output:
            CMAP - CMAP储存 k->v 的映射。k，v都为32字节bytes类型
        '''

        # BMAP储存 w->hash_root 的映射
        BMAP:Dict[str, bytes] = dict()
        # CMAP储存 k->v 的映射
        CMAP=dict()

        # 遍历每个关键字w
        for w, w_set in dataset.items():
            ################ 首先初始化DMAP中w的对应条目 ####################
            alpha=0
            beta=0
            H_w_upd=bytes(32)
            flag=False
            self.DMAP[w]=(alpha, beta, H_w_upd, flag)

            ############## 为w对应的所有id构造二叉搜索树，并为每个结点生成k-v pair ####################
            # 首先计算tau_w和k_w
            # w和alpha分别填充为16字节，然后再拼接并编码
            tau_w=hmac.new(key=self.k1, msg= (w.zfill(16)+str(alpha).zfill(16)).encode('utf-8'), digestmod='sha256').digest()
            k_w=hmac.new(key=self.k2, msg= (w.zfill(16)+str(alpha).zfill(16)).encode('utf-8'), digestmod='sha256').digest()

            # 构造二叉搜索树
            # 将w_set转换为有序的列表id_list
            id_list = sorted(w_set)
            # 得到树根与根哈希
            # 使用tree静态地储存树的结点
            tree:List[binSearchTree.binSearchTree]=[]
            root, root_hash = binSearchTree.binSearchTree.construct_tree(tree, id_list, 0, len(id_list)-1, '', '*')

            # 更新BMAP
            BMAP[w] = root_hash

            # 根据结点中的路径，计算k-v
            # 遍历tree数组中所有结点
            for node in tree:
                # node中的id
                id=node.id
                # 计算k=f(tau_w, path)
                k=hmac.new(key=tau_w, msg=node.path.encode('utf-8'), digestmod='sha256').digest()
                # 计算v=f(k_w, path) xor id，id填充到32字节
                tmp=hmac.new(key=k_w, msg=node.path.encode('utf-8'), digestmod='sha256').digest()
                v = bytes(a ^ b for a, b in zip(tmp, str(id).zfill(32).encode('utf-8')))

                # 将k,v加入CMAP
                CMAP[k]=v
        

        ################## 调用智能合约，将BMAP发送至区块链 ########################



        ################## 返回 #######################################
        return CMAP

    
    def update(self, w:str, id:int):
        '''
        将(w,id)插入数据库
        input:
            w - 关键字，str类型
            id - 文件id，int类型
        output:
            k - 32字节bytes
            v - 32字节bytes
        '''

        # 从DMAP中取出state信息
        alpha, beta, H_w_upd, flag = self.DMAP[w]

        ################### 判断flag #############################
        if flag:
            alpha += 1
            beta = 1
            H_w_upd = bytes(32)
            flag = False
        else:
            beta += 1
        
        ################## 计算k,v ################################
        # tau_w_upd=f(k1, w||alpha)
        # k_w_upd=f(k2, w||alpha)
        # w和alpha分别填充为16字节，然后再拼接并编码
        tau_w_upd = hmac.new(key=self.k1, msg= (w.zfill(16)+str(alpha).zfill(16)).encode('utf-8'), digestmod='sha256').digest()
        k_w_upd = hmac.new(key=self.k2, msg= (w.zfill(16)+str(alpha).zfill(16)).encode('utf-8'), digestmod='sha256').digest()

        # k=f(tau_w_upd, beta)
        k = hmac.new(key=tau_w_upd, msg = str(beta).encode('utf-8'), digestmod='sha256').digest()
        # v=f(k_w_upd, beta) xor id，id填充为32字节
        tmp = hmac.new(key=k_w_upd, msg=str(beta).encode('utf-8'), digestmod='sha256').digest()
        v = bytes(a ^ b for a, b in zip(tmp, str(id).zfill(32).encode(32)))

        ######################### 更新H_w_upd ############################
        # 使用keccak256计算id的哈希值，然后与旧的H_w_upd异或
        h_id = bytes(Web3.keccak(id))
        H_w_upd = bytes(a^b for a,b in zip(h_id, H_w_upd))

        ########################## 更新DMAP ############################
        self.DMAP[w] = (alpha, beta, H_w_upd, flag)


        ########################## 调用智能合约，将<tau_w_upd, H_w_upd>发送至区块链 ######################




        return k, v




    def verify(self):
        '''
        用户验证服务器返回的查询结果，并得到结果
        '''