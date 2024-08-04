from web3 import Web3
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple,Any, List
import random
import binSearchTree
import round
import re
import math


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

    # 合约对象
    web3 = None
    contract = None

    def __init__(self, web3, contract) -> None:
        self.web3 = web3
        self.contract = contract





    def setup(self, dataset: Dict[str, Set[int]]):
        '''
        初始化数据库。
        input:
            dataset - 倒排索引数据集。一个字典，关键字为字符串类型，文件id为正整数类型
        output:
            CMAP - CMAP储存 k->v 的映射。k，v都为32字节bytes类型
        '''

        # BMAP储存 tau_w->hash_root 的映射
        BMAP:Dict[bytes, bytes] = dict()
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
            BMAP[tau_w] = root_hash

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
        gas = self.batch_add(BMAP, 1)


        ################## 返回 #######################################
        return CMAP
    

    def batch_add(self, BMAP:Dict[bytes,bytes], batch_size:int):
        '''
        setup阶段，调用智能合约，将生成的ADS字典分批加入区块链。可能存在一部分元素不足batch_size，最后当作一个batch处理。
        input:
            BMAP - 
            batch_size - 每个batch的大小
            web3 - Web3对象
            contract - 合约对象
        output:
            gas - 花费的gas
        '''
        # 计算ADS的size
        total_size=len(BMAP)

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
            k_list=random.sample(list(BMAP.keys()),current_size)
            v_list=[BMAP[k] for k in k_list]
            # 从ADS中删除这些数据
            for k in k_list:
                BMAP.pop(k)
            
            # 调用智能合约，将两个list发送至合约，从而设置合约中的mapping
            # 首先将两个list中的元素转换为ABI要求的数据类型
            # _k_list=[Web3.toBytes(text=k.zfill(16)) for k in k_list]
            # _v_list=[Web3.toBytes(int(v)) for v in v_list]
            _k_list = k_list
            _v_list = v_list
            # 调用合约，并await，得到gas消耗
            # 通过type参数指定存入合约的哪个mapping
            tx_hash=self.contract.functions.batch_setBMAP(_k_list, _v_list, current_size).transact({
                'from':self.web3.eth.accounts[0], 
                'gasPrice': self.web3.eth.gasPrice, 
                'gas': self.web3.eth.getBlock('latest').gasLimit})
            tx_receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            gas += tx_receipt['gasUsed']

            # 更新剩余数量
            remain_size=remain_size-current_size

        return gas

    
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
        v = bytes(a ^ b for a, b in zip(tmp, str(id).zfill(32).encode('utf-8')))

        ######################### 更新H_w_upd ############################
        # 使用keccak256计算id的哈希值，然后与旧的H_w_upd异或
        h_id = bytes(Web3.keccak(str(id).encode('utf-8')))
        H_w_upd = bytes(a^b for a,b in zip(h_id, H_w_upd))

        ########################## 更新DMAP ############################
        self.DMAP[w] = (alpha, beta, H_w_upd, flag)


        ########################## 调用智能合约，将<tau_w_upd, H_w_upd>发送至区块链 ######################
        self.contract.functions.set_UMAP(tau_w_upd, H_w_upd).transact({
            'from':self.web3.eth.accounts[0], 
            'gasPrice': self.web3.eth.gasPrice, 
            'gas': self.web3.eth.getBlock('latest').gasLimit})



        return k, v


    def gen_token(self, Q:Set[str]):
        '''
        生成查询token。为Q中的关键字，生成四元组 (tau_w, k_w, tau_w_upd, k_w_upd)
        '''
        # token
        token:Set[Tuple[bytes, bytes, bytes, bytes]] = set()

        for w in Q:
            alpha, beta, H_w_upd, flag =self.DMAP[w]
            # tau_w
            tau_w=hmac.new(key=self.k1, msg= (w.zfill(16)+str(0).zfill(16)).encode('utf-8'), digestmod='sha256').digest()
            # k_w
            k_w=hmac.new(key=self.k2, msg= (w.zfill(16)+str(0).zfill(16)).encode('utf-8'), digestmod='sha256').digest()
            # tau_w_upd
            tau_w_upd = hmac.new(key=self.k1, msg= (w.zfill(16)+str(alpha).zfill(16)).encode('utf-8'), digestmod='sha256').digest()
            # k_w_upd
            k_w_upd = hmac.new(key=self.k2, msg= (w.zfill(16)+str(alpha).zfill(16)).encode('utf-8'), digestmod='sha256').digest()

            token.add((tau_w, k_w, tau_w_upd, k_w_upd))

            # 修改DMAP中flag为True
            self.DMAP[w] = (alpha, beta, H_w_upd, True)
        
        return token

            






    def verify(self, round_list:List[round.round], merkle_proof:Dict[bytes, List[binSearchTree.binSearchTree]]):
        '''
        用户验证服务器返回的查询结果，并得到结果
        '''

        # 储存查询结果，若干个id
        result:Set[int] = set()


        ###################### 验证每个轮次 ################################
        # 包括几个check point：
        # (1)第一轮的target必须是target_tau_w对应树的left most结点
        # (2)每一轮中，每棵树的lb和ub必须是相邻的，且lb.id<= target_id <= ub.id
        # (3)每一轮的target_id必须是前一轮所有ub.id中最大的
        # (4)最后一轮，必须存在某棵树的lb为right most结点，ub为None

        # round_order为r在round_list中的下标
        for round_order, r in enumerate(round_list):
            target_id = r.target_id
            target_tau_w = r.target_w

            # 判断r是否为第一轮
            if round_order == 0:
                # 判断target是target_tau_w对应树的的left most结点
                tree = merkle_proof[target_tau_w]
                # 找到left most结点
                left_most_pos = binSearchTree.binSearchTree.find_min_id(tree, len(tree)-1)
                if tree[left_most_pos].id != target_id:
                    print("target id in 1st round is wrong")
                    return False, None


            # 判断r是否为最后一轮
            if round_order == len(round_list)-1:
                # 判断是否存在某棵树的lb为right most结点，ub为None
                for tau_w, (lb, ub) in r.bound.items():
                    tree = merkle_proof[tau_w]
                    if ub is None:
                        # 判断lb的路径是否为'*[1..1]'形式，且lb没有右子结点，rhash=bytes(32)
                        pattern = r'^\*1*$'
                        if not ( re.match(pattern, tree[lb].path) and (tree[lb].rchild is None) and (tree[lb].rhash== bytes(32)) ):
                            print("lower bound in last round is wrong")
                            return False, None



            # 判断每棵树的lb和ub是否相邻，且判断是否覆盖target_id。
            # 之后，判断lb.id是否等于target_id。若对所有tau_w，都有lb.id==target_id，则将target_id加入结果
            is_result = True           # 标识当前轮次的target_id是否为结果
            for tau_w, (lb, ub) in r.bound.items():
                tree = merkle_proof[tau_w]
                # 如果是最后一轮，可能存在ub==None，特判
                if (round_order == len(round_list)-1) and (ub is None):
                    if tree[lb].id > target_id:
                        print("target_id is larger than lb_id")
                        return False, None

                else:
                    # 判断lb和ub是否在中序遍历顺序上相邻
                    if not binSearchTree.binSearchTree.is_neighbor(tree, lb, ub):
                        print("ub is not the neighbor of lb")
                        return False, None

                    # 判断是否覆盖target_id
                    if not((tree[lb].id <= target_id) and (tree[ub].id > target_id)):
                        print("range[lb,ub) does not cover target_id")
                        return False, None

                # 判断lb.id == target_id?
                if tree[lb].id != target_id:
                    is_result = False
            
            # 判断当前轮次target_id是否为结果
            if is_result:
                result.add(target_id)


            # 判断每一轮（第一轮除外）的target_id是否为前一轮所有ub.id中最大的
            if round_order > 0:
                ub_old_id_max=0
                # 找到上一轮多个ub中最大的id值
                for tau_w_old,(_,ub_old) in round_list[round_order-1].bound.items():
                    tree = merkle_proof[tau_w_old]
                    if tree[ub_old].id > ub_old_id_max:
                        ub_old_id_max = tree[ub_old].id
                
                # 判断
                if target_id != ub_old_id_max:
                    print("target id is not the largest ub of last round")
                    return False, None
        

        # 对round的检验通过
        print("verification for round list passes")
        print("result:", result)
        print(len(result))




        ######################### merkle prove ###################################
        # 遍历merkle proof中每棵树，计算hash_root
        for tau_w, tree in merkle_proof.items():
            root_hash = binSearchTree.binSearchTree.cal_hash_root(tree, len(tree)-1)
            # 从区块链获取Q中每个tau_w的hash_root
            root_on_chain = self.contract.functions.get_BMAP(tau_w).call()

            # 判断是否相等
            if root_hash != root_on_chain:
                print('root hash error')
                return False, None


        return True, result




