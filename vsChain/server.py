from web3 import Web3
from web3.exceptions import ContractLogicError
from Crypto.Cipher import AES
import hmac
from typing import Dict,Set,Tuple,Any, List, Optional
import random
import binSearchTree
import round
import time


class server:
    '''
    服务器
    '''

    # CMAP，储存 k->v 的映射。k,v都是32字节bytes
    CMAP: Dict[bytes, bytes] = dict()

    # trees，储存每个w对应的二叉搜索树
    # tau_w->tree。静态储存树，将树结点储存在数组中
    trees: Dict[bytes, List[binSearchTree.binSearchTree]] = dict()

    # 储存每棵树树根在数组中的下标
    # tau_w->root_index
    root_pos: Dict[bytes, int] = dict()

    # 合约对象
    web3 = None
    contract = None

    def __init__(self, web3, contract) -> None:
        self.web3 = web3
        self.contract = contract
        self.root_pos = dict()
        self.trees = dict()
        self.CMAP = dict()



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
            round_list - 储存搜索的所有轮次
            merkle_proof - 对应所有bound结点的merkle proof。一个字典，键为tau_w，值为tau_w对应的Merkel子树
            t1 - search find result time
            t2 - search generate VO time
            t3 - update generate ADS time
            t4 - update transact time
            gas - 更新时花费的gas
        '''

        # 令牌
        
        t1_s = time.time()
        t2 = 0
        t3 = 0
        t4 = 0
        gas = 0
        
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
                # 设置root index
                self.root_pos[tau_w] = len(tree)-1


        ##################### 将上一批次的更新写入CMAP和trees，并生成更新证明 ###################
        # 储存每个tau_w对应的被更新的ids
        w_upd_id:Dict[bytes, List[int]] = dict()
        # 储存每个tau_w对应的merkle proof，用于向区块链证明更新路径正确
        # proofs_for_bc:Dict[bytes, List[binSearchTree.binSearchTree]] = dict()

        for tau_w, k_w, tau_w_upd, k_w_upd in token:
            # 获取tau_w对应的二叉搜索树
            tree = self.trees[tau_w]

            t3_s = time.time()

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
                id = int( bytes(a ^ b for a, b in zip(tmp, v)).decode('utf-8').lstrip('0') )

                # 将id加入upd_id_list
                upd_id_list.append(id)

                # 将id写入二叉搜索树
                binSearchTree.binSearchTree.update_tree(tree, id)

                # 更新beta
                beta += 1

                # 将k-v从CMAP中删除
                del self.CMAP[k]
            
            # 若upd_id_list为空，说明当前w没有更新，直接跳过
            if len(upd_id_list)==0:
                continue
        
            w_upd_id[tau_w] = upd_id_list

            # 先为w_upd_id生成merkle证明
            proof:List[binSearchTree.binSearchTree]=[]
            binSearchTree.binSearchTree.gen_proof(tree, upd_id_list, proof, self.root_pos[tau_w])
            # 将证明加入proofs_for_bc
            # proofs_for_bc[tau_w] = proof

            # 然后更新树结点中的hash
            binSearchTree.binSearchTree.update_hash(tree, self.root_pos[tau_w])

            t3_e = time.time()
            t3 = t3+t3_e-t3_s
        
            t4_s = time.time()

            # 将proofs和upd_id_list发送至区块链进行验证和更新hash_root
            # 注意，部分proof可能为空，因为对应关键字未被更新。
            # 使用列表推导的技巧构造函数参数
            # 智能合约可能会抛出异常
            tx_hash=self.contract.functions.update_tree(tau_w, 
                                                tau_w_upd, 
                                                [n.id for n in proof],
                                                [n.lchild if n.lchild is not None else -1 for n in proof],
                                                [n.rchild if n.rchild is not None else -1 for n in proof],
                                                [n.lhash for n in proof],
                                                [n.rhash for n in proof],
                                                len(proof),
                                                upd_id_list,
                                                len(upd_id_list)).transact({
                'from':self.web3.eth.accounts[0], 
                'gasPrice': self.web3.eth.gasPrice, 
                'gas': 3000000000})
            tx_receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            if tx_receipt['status'] != 1:
                print("transaction status:",tx_receipt['status'])
            gas = gas+tx_receipt['gasUsed']
 
            t4_e = time.time()
            t4 = t4+t4_e-t4_s
            



        ############################ JOIN QUERY ####################################
        round_list, merkle_proof, t2 = self.join_query(token)

        t1_e = time.time()
        t1 = t1_e - t1_s -t2 -t3 -t4
        

        # 返回
        return round_list, merkle_proof, t1, t2, t3, t4, gas






    def join_query(self, token:Set[Tuple[bytes, bytes, bytes, bytes]]):
        '''
        JOIN QUERY
        input:
            token - 搜索令牌，每个元素为一个四元组 (tau_w, k_w, tau_w_upd, k_w_upd)，对应于一个查询的关键字
        output:
            round_list - 储存搜索的所有轮次
            merkle_proof - 对应所有bound结点的merkle proof。一个字典，键为tau_w，值为tau_w对应的Merkel子树
            t - generate VO time
        '''

        # 储存搜索的所有轮次
        round_list:List[round.round] = []
        
        # 储存每棵树对应的merkle proof，本质是一棵子树，使用静态数组储存。key为tau_w
        merkle_proof:Dict[bytes, List[binSearchTree.binSearchTree]] = dict()

        # 目标id
        target_id=0
        # 作为目标的树对应的tau_w
        target_tau_w=None
        # 目标结点在tree数组中的下标
        target_pos = None

        # 选择第一轮次的target。找到每棵树中最小的id，然后取其中最大的作为第一轮target
        for tau_w, _, _, _ in token:
            # 获取tau_w对应的二叉搜索树
            tree = self.trees[tau_w]
            # 找到树中最小的id
            pos = binSearchTree.binSearchTree.find_min_id(tree, self.root_pos[tau_w])
            id = tree[pos].id
            if id > target_id:
                target_id=id
                target_tau_w = tau_w
                target_pos = pos
        


        ############################### 迭代所有轮次 ###############################
        # 为每个tau_w对应的树创建一个栈，用于中序遍历
        # key为tau_w, value为对应的栈，栈中每个元素为结点在tree数组中的下标index和flag，标识左子结点是否被访问过
        # 每个结点的格式为 [index, flag]
        stack_w:Dict[bytes, List[List]] = dict()

        # 键为tau_w，值为tau_w对应树的所有bound结点在数组中的下标。
        w_bounds:Dict[bytes, Set[int]] = dict()


        # 标识搜索是否结束。
        is_finish = False
        # 当某棵树无法找到upper bound时，搜索结束
        while not is_finish:

            # 构造round对象，储存当前轮次的信息
            r = round.round(target_id, target_tau_w)

            # 将pos信息加入w_bounds
            if target_tau_w not in w_bounds:
                w_bounds[target_tau_w]=set()
            w_bounds[target_tau_w].add(target_pos)

            # 在当前轮次中，根据target_id，搜索每棵树
            for tau_w, _, _, _ in token:
                # 判断tau_w对应的栈是否存在。若不存在，在stack_w中增加新条目，初始为根结点
                if tau_w not in stack_w:
                    stack_w[tau_w] = [[self.root_pos[tau_w], False]]
                # 当前tau_w的栈
                st = stack_w[tau_w]

                # 若是target_id所在的树，跳过
                # if tau_w == target_tau_w:
                    # continue
                
                # 获取tau_w对应的二叉搜索树
                tree = self.trees[tau_w]

                # 搜索target_id，得到lb，ub。中序遍历，将遍历到的结点暂存在栈中
                lb, ub = self.find_bound(tree, target_id, st)

                # 将tau_w对应的lb, ub加入round对象
                r.bound[tau_w] = (lb, ub)
                
                # 若ub==None，则JOIN QUERY结束
                if ub is None:
                    is_finish = True
                
                # 将round_list中每一轮次中的lb,ub按照tau_w分类
                if tau_w not in w_bounds:
                    w_bounds[tau_w] = set()
                if lb is not None:
                    w_bounds[tau_w].add(lb)
                if ub is not None:
                    w_bounds[tau_w].add(ub)
            
            # 对本轮所有树的ub取最大值作为下一轮的target_id
            for tau_w, (lb,ub) in r.bound.items():
                if (ub is not None) and (self.trees[tau_w][ub].id>target_id):
                    target_id = self.trees[tau_w][ub].id
                    target_tau_w = tau_w
                    target_pos = ub


            # 将r加入round_list
            round_list.append(r)

        ################################ 生成merkle proof ###############################
        t_s = time.time()

        # 根据w_bounds中，每个tau_w对应的bound结点，计算每棵树的merkle proof
        # 同时建立一个映射，将原树中结点的下标映射到merkle子树中结点的下标。例如，原树中某内部结点的下标为m，merkle
        # 子树中仍然包含这个节点，且该结点在merkle子树中的下标为n，则建立映射m->n

        # 键为tau_w，值为两棵树结点下标的映射关系
        
        for tau_w, bounds_set in w_bounds.items():
            tree = self.trees[tau_w]
            # 当前二叉树和merkle子树间结点的映射关系
            index_map:Dict[int, int] = dict()
            # 为bounds_set中的结点生成merkle proof，且得到结点间的映射关系
            proof=[]
            binSearchTree.binSearchTree.merkle_prove(tree, proof, bounds_set, self.root_pos[tau_w], index_map)

            # 将proof加入结果
            merkle_proof[tau_w] = proof

            # 根据映射关系，修改round_list中tau_w对应的lb和ub为merkle子树中的结点index
            for r in round_list:
                lb, ub = r.bound[tau_w]
                if lb is not None:
                    lb = index_map[lb]
                if ub is not None:
                    ub = index_map[ub]
                r.bound[tau_w] = (lb, ub)
        
        t_e = time.time()
        t=t_e-t_s

        # 返回
        return round_list, merkle_proof, t










    def find_bound(self, tree:List[binSearchTree.binSearchTree], target_id:int, st:List[List]):
        '''
        给定target_id和栈，在树中搜索并获取lb, ub。
        用栈进行中序遍历。栈pop出的元素恰好符合中序遍历。
        具体的顺序：每一轮循环中，首先判断栈顶元素是否存在左子结点且未被访问，若是，则将左子结点入栈；否则pop，并将
                   右子结点入栈（若存在右子结点）。栈空时说明遍历结束。
                   将查询得到的ub留在st顶部，暂时不pop
        input:

        output:
            lb - lower bound结点在tree中的下标
            ub - lower bound结点在tree中的下标。若ub为None，说明这棵树的搜索结束
        '''

        # 储存中序遍历顺序中，前一个结点（即前一个出栈的结点）在tree数组的下标
        pre_ptr=None

        # 利用栈遍历树结点
        while len(st)>0:
            # 获取栈顶元素，当前结点在tree数组的下标和flag（标识左子结点是否已被访问过）
            current_ptr, flag = st[-1]
            # 左子结点存在且未被访问过，将左子结点压入栈
            if (not flag) and (tree[current_ptr].lchild is not None):
                # 修改flag
                st[-1][1] = True
                st.append([tree[current_ptr].lchild, False])
            # 否则pop，然后将右子结点入栈
            else:
                # 判断当前结点是否是第一个大于target的。若是，结束迭代。
                if tree[current_ptr].id > target_id:
                    return pre_ptr, current_ptr
                
                st.pop()
                if tree[current_ptr].rchild is not None:
                    st.append([tree[current_ptr].rchild, False])

                # 更新pre_ptr
                pre_ptr = current_ptr
        

        # 未找到ub，返回pre_ptr, None
        return pre_ptr, None

                