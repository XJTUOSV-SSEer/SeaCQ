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

    # 储存每棵树树根在数组中的下标
    root_pos: Dict[bytes, int]



    def update_CMAP(self, k:bytes, v:bytes):
        '''
        将用户更新的k-v加入CMAP
        '''
        self.CMAP[k]=v


    def search(self, token:Set[Tuple[bytes, bytes, bytes, bytes]]):
        '''
        首先将查询集合Q中关键字的上一批次的更新写入数据库，然后执行可验证的JOIN QUERY
        默认搜索的关键字已经在setup阶段被写入
        input:
            token - 搜索令牌，每个元素为一个四元组 (tau_w, k_w, tau_w_upd, k_w_upd)，对应于一个查询的关键字

        output:

        '''

        # 令牌
        
        
        ########################### 为token中每个tau_w建立树（第一次搜索时） #########################
        # 首先判断tau_w是否存在于trees数组
        # 若是setup后第一次搜索，那么tau_w一定不存在于trees数组，因此需要构造树并写入trees
        for tau_w, k_w, tau_w_upd, k_w_upd in token:
            if tau_w not in self.trees:
                # 根据path重建二叉搜索树
                tree=[]
                binSearchTree.binSearchTree.construct_from_path(tree, self.CMAP, tau_w, k_w, '*')
                # 将tree加入trees
                self.trees[tau_w] = tree
                self.root_pos[tau_w] = len(tree)-1


        ##################### 将上一批次的更新写入CMAP和trees，并生成更新证明 ###################
        # 储存每个tau_w对应的被更新的ids
        w_upd_id=dict()
        # 储存每个tau_w对应的merkle proof
        proofs=dict()

        for tau_w, k_w, tau_w_upd, k_w_upd in token:
            # 获取tau_w对应的二叉搜索树
            tree = self.trees[tau_w]

            # 储存w对应的更新的id
            upd_id_list = []
            beta = 1
            # 遍历w对应的所有更新
            while True:
                # 计算k=f(tau_w_upd, beta)，判断k是否在CMAP中
                k = hmac.new(key=tau_w_upd, msg = str(beta).encode('utf-8'), digestmod='sha256').digest()
                if k not in self.CMAP:
                    break

                # v和id
                v = self.CMAP[k]
                tmp = hmac.new(key=k_w_upd, msg=str(beta).encode('utf-8'), digestmod='sha256').digest()
                id = int( str(bytes(a ^ b for a, b in zip(tmp, v))).lstrip('0') )

                # 将id加入upd_id_list
                upd_id_list.append(id)

                # 将id写入二叉搜索树
                binSearchTree.binSearchTree.update_tree(tree, id)

                # 更新beta
                beta += 1
            
            w_upd_id[tau_w] = upd_id_list

            # 先为w_upd_id生成merkle证明
            proof=[]
            binSearchTree.binSearchTree.gen_proof(tree, upd_id_list, proof, self.root_pos[tau_w])
            # 将证明加入proofs
            proofs[tau_w] = proof

            # 然后更新树结点中的hash
            binSearchTree.binSearchTree.update_hash(tree, self.root_pos[tau_w])
        

        # 将proofs和upd_id_list发送至区块链进行验证和更新hash_root



        ############################ JOIN QUERY ####################################
        # 选择第一轮次的target。

















        