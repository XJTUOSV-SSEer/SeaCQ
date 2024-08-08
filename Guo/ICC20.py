import numpy as np
import time
import sys
import datetime
import os
from scipy.sparse import csr_matrix
import re
import random
import hmac
import hmac
import random
import pickle
from Crypto.Cipher import AES
import json
import string
from web3 import Web3
import json
from web3.middleware import geth_poa_middleware


abi_build_index = """
[
	{
		"constant": false,
		"inputs": [
			{
				"name": "enfile",
				"type": "bytes16[]"
			},
			{
				"name": "len",
				"type": "uint256"
			},
			{
				"name": "blocknum",
				"type": "uint256"
			}
		],
		"name": "batch_gethash",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "recordhash",
				"type": "bytes32"
			}
		],
		"name": "equal_or_not",
		"outputs": [
			{
				"name": "current_xor",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "totalnumber",
				"type": "uint256"
			}
		],
		"name": "getlastxor",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "ctoken",
				"type": "bytes16"
			},
			{
				"name": "dhash",
				"type": "bytes32"
			}
		],
		"name": "set",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "ctoken",
				"type": "bytes16[]"
			},
			{
				"name": "dhash",
				"type": "bytes32[]"
			},
			{
				"name": "len",
				"type": "uint256"
			}
		],
		"name": "setbatchs",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "token",
				"type": "bytes16"
			}
		],
		"name": "try_whether_equal",
		"outputs": [
			{
				"name": "current_xor",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "bytes16"
			}
		],
		"name": "blockindex",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "blockxor",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "check_",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "check_equal_or_not",
		"outputs": [
			{
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "current_xor",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "end_xor",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "filehash",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "finish_xor",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "get_computexor",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "token",
				"type": "bytes16"
			}
		],
		"name": "gettoken",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "is_equal",
		"outputs": [
			{
				"name": "",
				"type": "int256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "recordtoken",
		"outputs": [
			{
				"name": "",
				"type": "bytes32"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]
"""


sys.setrecursionlimit(100000)

# 使用ws provider创建一个Web3对象
w3 = Web3(Web3.WebsocketProvider("ws://127.0.0.1:8545"))
# 用于geth
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
# print(w3.eth.blockNumber)


# 私钥
# 主密钥k，用'chen'和hmac来生成。
secreat_key = hmac.new(b'chen').digest()
# 对称加密的模式
model = AES.MODE_ECB


####################################################### 建立索引####################################################
def Build_index(Kw_File_Use, web3, contract):
    # client端私钥k
    secreat_key = hmac.new(b'chen').digest()
    # print(secreat_key)
    model = AES.MODE_ECB

    # 建server端索引
    server_index = {}  # server索引。用一个字典，储存[ptr:P,V]
    blockchain_index = {}  # 发给blockchain的索引。用一个字典，储存[l_w:H() xor H()...]
    client_index = {}  # client索引yes。用一个字典，储存[kw:ptr1,u,v,s]
    w_f_addr_table = {}

    # index construct time
    t1 = 0
    # ADS generate time
    t2 = 0
    # transact time
    t3 = 0

    t1_s =time.time()

    # 遍历所有关键词kw
    for kw in Kw_File_Use:
        # 生成客户端索引
        start_file_id = Kw_File_Use[kw][len(
            Kw_File_Use[kw]) - 1]  # client存储的首文件id
        # print(start_file_id)
        # 计算首文件地址
        str1 = kw + start_file_id  # kw||f1
        st = str1.encode('utf-8')  # 连接的字符串
        # print(st)
        addr = hmac.new(st)
        start_file_addr = addr.digest()  # client存储的首文件地址
        server_upt_time = 0  # server 更新次数u
        block_upt_time = 0  # blockchain 更新次数v
        search_or_not = 0  # 是否搜索过s
        client_index[kw] = [server_upt_time,
                            block_upt_time, search_or_not, start_file_addr]
        # 生成token
        # client生成token（server端文件地址+文件内容）
        # 字符串连接
        tok_server_addr = (kw + str(server_upt_time) +
                           str(1)).zfill(16)  # w||u||1
        tok_server_enc = (kw + str(server_upt_time) +
                          str(2)).zfill(16)  # w||u||2
        tok_block = (kw+str(block_upt_time)).zfill(16)  # w||v

        # 转字节
        t_addr = tok_server_addr.encode('utf-8')
        t_enc = tok_server_enc.encode('utf-8')
        t_blo = tok_block.encode('utf-8')
        # 加密生成token
        aes = AES.new(secreat_key, model)
        # 生成token
        Toekn_S_Addr = aes.encrypt(t_addr)  # tw1
        Toekn_S_Enc = aes.encrypt(t_enc)  # tw2
        Token_block = aes.encrypt(t_blo)  # lw

        for i in range(len(Kw_File_Use[kw])):
            if i == 0:  # nonce块
                # 倒排索引中第一个是nonce值
                # 生成当前文件地址
                Kw_File_Use[kw][0]=Kw_File_Use[kw][0].encode('utf-8')
                str1 = kw.encode('utf-8') + \
                    Kw_File_Use[kw][0]  # kw||nonce
                addr = hmac.new(str1)		#
                addr_file = addr.digest()  # w_nonce地址 ptr_n+1
                w_f_addr_table[kw] = [addr_file]  # 用来储存下一个文件的ptr

                # 生成当前G
                # G(t1w,ptr n)
                aes_t1 = AES.new(Toekn_S_Addr, model)  # token做key进行加密
                G_token_S_addr = aes_t1.encrypt(addr_file)
                # G(t2w,ptr n)
                aes_t2 = AES.new(Toekn_S_Enc, model)
                G_token_S_enc = aes_t2.encrypt(addr_file)

                # 异或下一文件地址，nonce块异或b'NNNNNNNNNNNNNNNN'，得到P
                addr = bytes(a ^ b for a, b in zip(
                    G_token_S_addr, b'NNNNNNNNNNNNNNNN'))
                # 与nonce值异或，得到V
                enc_nonce = bytes(a ^ b for a, b in zip(
                    G_token_S_enc, Kw_File_Use[kw][0]))  # 与nonce直接异或
                server_index[addr_file] = [addr, enc_nonce]  # server端nonce块的数据
                # blockchain_index为每个token-所有文件hash的异或
                # print("Kw_File_Use[kw][0]")
                # print(Kw_File_Use[kw][0])
                # hashnonce=hmac.new(Kw_File_Use[kw][0]).digest()
                hashnonce = Web3.keccak(Kw_File_Use[kw][0])  # 求nonce的哈希值
                # print("hashnonce")
                # print(hashnonce)
                blockchain_index[Token_block] = hashnonce
            else:
                # 获得地址
                file_id = Kw_File_Use[kw][i]  # 对应文件名字
                str1 = kw + file_id  # 连接的字符串 kw||f_i
                st = str1.encode('utf-8')  # 转字节
                addr = hmac.new(st)
                addr_file = addr.digest()  # 得到kw连接file地址ptr
                w_f_addr_table[kw].append(addr_file)  # ptr添加到w_f_addr_table列表中

                # 生成当前G
                # G(t1w,ptr n)
                aes_t1 = AES.new(Toekn_S_Addr, model)
                G_token_S_addr = aes_t1.encrypt(addr_file)
                # G(t2w,ptr n)
                aes_t2 = AES.new(Toekn_S_Enc, model)
                G_token_S_enc = aes_t2.encrypt(addr_file)
                # 异或下一文件地址，所有nonce块都异或前一个块
                # 上一文件地址
                last_file_addr = w_f_addr_table[kw][i-1]
                # 异或上一文件地址
                addr = bytes(a ^ b for a, b in zip(
                    G_token_S_addr, last_file_addr))  # P

                # 获得文件ID的密文 Enc(k,fi)
                m = Kw_File_Use[kw][i]
                fileID_en = m.encode('utf-8')
                # print(fileID_en)
                enc_file_ID = aes.encrypt(fileID_en)

                enc_file = bytes(a ^ b for a, b in zip(
                    G_token_S_enc, enc_file_ID))  # V
                server_index[addr_file] = [addr, enc_file]  # server端nonce块的数据
                # blockchain index 累计异或
                # 当前密文的hash,对文件id密文hash
                # hash_fileID=hmac.new(enc_file_ID).digest()

                t2_s=time.time()

                hash_fileID = Web3.keccak(enc_file_ID)  # 对密文求哈希

                # # blockchain_index[dd]=cc.decode()
                # # blockchain_index[Token_block.decode()] = bytes(a ^ b for a, b in zip(blockchain_index[Token_block],hash_fileID)).decode()
                blockchain_index[Token_block] = bytes(
                    a ^ b for a, b in zip(blockchain_index[Token_block], hash_fileID))
                
                t2_e =time.time()
                t2 = t2+t2_e-t2_s

    t1_e = time.time()
    t1 = t1_e-t1_s-t2

    t3_s = time.time()
    gas = 0

    for toekn in blockchain_index:
        tx_hash = contract.functions.set(toekn,blockchain_index[toekn]).transact({
                    "from": web3.eth.accounts[0],
                    "gas": 300000000,
                    "gasPrice": web3.eth.gasPrice,
                })
    
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
        gas += tx_receipt['gasUsed']
    
    t3_e = time.time()
    t3 = t3_e-t3_s

        # 将三个字典返回
    return server_index, blockchain_index, client_index, t1, t2, t3, gas


# 搜索

# 确定要搜索的kw，以及发送到server和blockchain的token


def user_search_keyword(client_index):

    # inputKW=input("请输入要搜索的关键字")
    inputKW = "chen"
    server_upt_time, block_upt_time, search_or_not, start_file_addr = client_index[inputKW]

    # 判断这个关键字在server上之前是否换过toekn

    # if server_upt_time==0:
    # 生成搜索token
    tok_server_addr = (inputKW + str(server_upt_time) +
                       str(1)).zfill(16)  # w||u||1
    # print(tok_server_addr)
    tok_server_enc = (inputKW + str(server_upt_time) +
                      str(2)).zfill(16)  # w||u||2
    # print(tok_server_enc)
    tok_block = (inputKW + str(block_upt_time)).zfill(16)  # w||v
    # print(tok_block)
    t_addr = tok_server_addr.encode('utf-8')
    t_enc = tok_server_enc.encode('utf-8')
    t_blo = tok_block.encode('utf-8')
    aes = AES.new(secreat_key, model)
    Toekn_S_Addr = aes.encrypt(t_addr)
    Toekn_S_Enc = aes.encrypt(t_enc)
    Token_block = aes.encrypt(t_blo)
    # client_index[inputKW][search_or_not]=1  #设为搜索过
    client_index[inputKW][2] = 1
    return Toekn_S_Addr, Toekn_S_Enc, Token_block, start_file_addr


# client端搜索单个kw
def user_search_keyword_mutiple(client_index, inputKW):

    # 根据kw找到client的状态信息
    server_upt_time, block_upt_time, search_or_not, start_file_addr = client_index[inputKW]

    # 判断这个关键字在server上之前是否换过toekn

    # if server_upt_time==0:
    # 生成搜索token
    tok_server_addr = (inputKW + str(server_upt_time) +
                       str(1)).zfill(16)  # w||u||1
    # print(tok_server_addr)
    tok_server_enc = (inputKW + str(server_upt_time) +
                      str(2)).zfill(16)  # w||u||2
    # print(tok_server_enc)
    tok_block = (inputKW + str(block_upt_time)).zfill(16)  # w||v
    # print(tok_block)
    t_addr = tok_server_addr.encode('utf-8')
    t_enc = tok_server_enc.encode('utf-8')
    t_blo = tok_block.encode('utf-8')
    aes = AES.new(secreat_key, model)
    Toekn_S_Addr = aes.encrypt(t_addr)  # tw1
    Toekn_S_Enc = aes.encrypt(t_enc)  # tw2
    Token_block = aes.encrypt(t_blo)  # lw
    # client_index[inputKW][search_or_not]=1  #设为搜索过
    client_index[inputKW][2] = 1  # 设置s
    # 返回tw1,tw2,lw,ptr1
    return Toekn_S_Addr, Toekn_S_Enc, Token_block, start_file_addr


# server根据收到的token，返回文件结果
def Server_search(Toekn_S_Addr, Toekn_S_Enc, start_file_addr, server_index, list_search_file_ID):
    # 根据ptr找到P,V
    addr, enc_file = server_index[start_file_addr]
    # 生成当前G
    # G(t1w,ptr n)
    aes_t1 = AES.new(Toekn_S_Addr, model)  # token做key进行加密
    G_token_S_addr = aes_t1.encrypt(start_file_addr)
    # G(t2w,ptr n)
    aes_t2 = AES.new(Toekn_S_Enc, model)
    G_token_S_enc = aes_t2.encrypt(start_file_addr)
    # 下一文件地址
    next_file_addr = bytes(a ^ b for a, b in zip(
        G_token_S_addr, addr))  # ptr_next
    # 当前文件加密ID
    enc_file_ID = bytes(a ^ b for a, b in zip(
        G_token_S_enc, enc_file))  # cipher
    list_search_file_ID.append(enc_file_ID)
    # print("list_search_file_ID")
    # print(list_search_file_ID)
    # print(enc_file_ID)
    # 如果下一文件的地址是这个（即NULL），则停止
    # 没有考虑更复杂的情况，即ptr_next不存在的情况（多条链拼接），递归边界写在最上面，用in来判断
    if next_file_addr != b'NNNNNNNNNNNNNNNN':
        return Server_search(Toekn_S_Addr, Toekn_S_Enc, next_file_addr, server_index, list_search_file_ID)
    else:
        return list_search_file_ID


# def Server_search_for_loop(Toekn_S_Addr,Toekn_S_Enc,start_file_addr,server_index,list_search_file_ID):
#     for i in range(100000000):
#         addr, enc_file = server_index[start_file_addr]
#         ################生成当前G
#         # G(t1w,ptr n)
#         aes_t1 = AES.new(Toekn_S_Addr, model)  # token做key进行加密
#         G_token_S_addr = aes_t1.encrypt(start_file_addr)
#         # G(t2w,ptr n)
#         aes_t2 = AES.new(Toekn_S_Enc, model)
#         G_token_S_enc = aes_t2.encrypt(start_file_addr)
#         # 下一文件地址
#         next_file_addr = bytes(a ^ b for a, b in zip(G_token_S_addr, addr))
#         # 当前文件加密ID
#         enc_file_ID = bytes(a ^ b for a, b in zip(G_token_S_enc, enc_file))
#         list_search_file_ID.append(enc_file_ID)

    # print("list_search_file_ID")
    # print(list_search_file_ID)
    # print(enc_file_ID)
    # 如果下一文件的地址这个，则停止
    if next_file_addr != b'NNNNNNNNNNNNNNNN':
        return Server_search(Toekn_S_Addr, Toekn_S_Enc, next_file_addr, server_index, list_search_file_ID)
    else:
        return list_search_file_ID


# add 一个w-ind pair
# 问题：没有进行s状态的判断以及更新u
def addfile(addfile_kw, addfile_nonce, addfile_ID, client_index, server_index, blockchain_index, blockchain_addfile_index):
    addr_before = client_index[addfile_kw][3]  # 当前的第一个ptr
    # client生成token（server端文件地址+文件内容）  不变
    # 字符串连接 计算token
    # 添加文件blockchain端token更新
    # time=client_index[addfile_kw][1]
    # client_index:kw-->[u,v,s,ptr1]
    client_index[addfile_kw][1] = client_index[addfile_kw][1]+1  # v++
    tok_server_addr = (
        addfile_kw + str(client_index[addfile_kw][0]) + str(1)).zfill(16)  # w||u||1
    tok_server_enc = (
        addfile_kw + str(client_index[addfile_kw][0]) + str(2)).zfill(16)  # w||u||2
    tok_block = (
        addfile_kw + str(client_index[addfile_kw][1])).zfill(16)  # w||v
    tok_block_last = (
        addfile_kw + str(client_index[addfile_kw][1]-1)).zfill(16)  # w||(v-1)
    # 转字节
    t_addr = tok_server_addr.encode('utf-8')
    t_enc = tok_server_enc.encode('utf-8')
    t_blo = tok_block.encode('utf-8')
    t_blo_last = tok_block_last.encode('utf-8')
    # 加密生成token
    aes = AES.new(secreat_key, model)
    # 生成token
    Toekn_S_Addr = aes.encrypt(t_addr)  # 新的tw1
    Toekn_S_Enc = aes.encrypt(t_enc)  # 新的tw2
    Token_block = aes.encrypt(t_blo)  # 新的lw
    Token_block_last = aes.encrypt(t_blo_last)  # 上一次的lw
    # 将新加入的文件和nonce添加到server的kw对应索引
    # 生成nonce块地址
    str1 = addfile_kw.encode('utf-8') + addfile_nonce  # kw||nonce
    addr = hmac.new(str1)
    addr_file = addr.digest()  # w_nonce地址,ptr
    # 生成当前G
    aes_t1 = AES.new(Toekn_S_Addr, model)  # token做key进行加密
    G_token_S_addr = aes_t1.encrypt(addr_file)  # 用tw1对nonce的ptr进行运算
    # G(t2w,ptr n)
    aes_t2 = AES.new(Toekn_S_Enc, model)
    G_token_S_enc = aes_t2.encrypt(addr_file)
    # 异或之前文件链的头（即client端的头）
    addr = bytes(a ^ b for a, b in zip(G_token_S_addr, addr_before))
    # 与nonce值异或
    enc_nonce = bytes(a ^ b for a, b in zip(
        G_token_S_enc, addfile_nonce))  # 与nonce直接异或
    server_index[addr_file] = [addr, enc_nonce]  # server端nonce块的数据
    # blockchain_index为每个token-所有文件hash的异或
    # hashnonce = hmac.new(addfile_nonce).digest()

    hashnonce = Web3.keccak(addfile_nonce)
    # 加文件块

    # 更新client端存储的起始地址
    # addr_before = client_index[addfile_kw][3]
    start_file_addr = (addfile_kw + addfile_ID).encode('utf-8')
    addr = hmac.new(start_file_addr)
    addr_file1 = addr.digest()  # 新的起始文件地址ptr
    client_index[addfile_kw][3] = addr_file1  # 更新client的ptr1状态
    # 异或下一文件地址，所有nonce块都异或前一个块
    # 上一文件地址
    last_file_addr1 = addr_file
    # 异或上一文件地址
    aes_t1 = AES.new(Toekn_S_Addr, model)  # token做key进行加密
    G_token_S_addr1 = aes_t1.encrypt(addr_file1)
    # G(t2w,ptr n)
    aes_t2 = AES.new(Toekn_S_Enc, model)
    G_token_S_enc1 = aes_t2.encrypt(addr_file1)
    addr1 = bytes(a ^ b for a, b in zip(G_token_S_addr1, last_file_addr1))  # P
    # 获得文件ID的密文 Enc(k,fi)
    # m = Kw_File_Use[kw][i]
    fileID_en = addfile_ID.encode('utf-8')
    # print(fileID_en)
    enc_file_ID = aes.encrypt(fileID_en)

    enc_file1 = bytes(a ^ b for a, b in zip(
        G_token_S_enc1, enc_file_ID))  # 与密文异或得到V
    server_index[addr_file1] = [addr1, enc_file1]  # server端nonce块的数据

    # blockchain 存储的密文hash
    # enhash = hmac.new(enc_file_ID).digest()
    enhash = Web3.keccak(enc_file_ID)

    # blockchain index 累计异或

    # 密文hash
    newhash = bytes(a ^ b for a, b in zip(hashnonce, enhash))
    lastindex = blockchain_index[Token_block_last]
    blockchain_index[Token_block] = bytes(
        a ^ b for a, b in zip(newhash, lastindex))  # 计算hash值
    blockchain_addfile_index[Token_block] = bytes(
        a ^ b for a, b in zip(newhash, lastindex))

    return client_index, server_index, blockchain_index, blockchain_addfile_index








################################## 创建ETH 对象 #############################
# client/server的账户
from_account = w3.toChecksumAddress(
    "0x6898ED602b8a883f6Bc9bC22F9464AA25d29a59E")
# 创建abi
abi_build_index = json.loads(abi_build_index)
# 合约对象
store_var_contract = w3.eth.contract(
    address=w3.toChecksumAddress('0xc4B7cdc3B615511A7E297FB1e286B74fAC201952'),
    abi=abi_build_index)





def experiment_build(dataset):
    '''
    对不同大小的数据集测试其build时间

    Parameters:
    dataset: 数据集的路径

    Returns:
    delay: 花费的时间
    '''
    # 从二进制文件中读取build用的字典数据 inverted_index
    with open(dataset, 'rb') as f:  # 打开文件
        inverted_index = pickle.load(f)

    t1 = time.time()
    # 调用build_client函数，进行build
    server_index, blockchain_index, client_index = Build_index(inverted_index)
    t2 = time.time()

    return t2-t1


###################### 测试build速度 #####################################

# 2K数据集
# t = 0
# for i in range(5):
#     t = t+experiment_build('./data/data_2K.txt')

# print('2K dataset:', t/5)

# 4K数据集
# t = 0
# for i in range(5):
#     t = t+experiment_build('./data/data_4K.txt')

# print('4K dataset:', t/5)

# 6K数据集
# t = 0
# for i in range(5):
#     t = t+experiment_build('./data/data_6K.txt')

# print('6K dataset:', t/5)

# 8K数据集
# t = 0
# for i in range(5):
#     t = t+experiment_build('./data/data_8K.txt')

# print('8K dataset:', t/5)

# 10K数据集
# t = 0
# for i in range(5):
#     t = t+experiment_build('./data/data_10K.txt')

# print('10K dataset:', t/5)



def experiment_add(dataset):
    '''
    在已经用一个10K数据集build的前提下，测试add不同数据集的时间

    Parameters:
    dataset: 数据集的路径

    Returns:
    delay: 花费的时间
    '''

    # 先用10K数据集进行build
    with open('./data/data_10K.txt', 'rb') as f:  # 打开文件
            inverted_index = pickle.load(f)
    map_server,checklist,state_client=Build_index(inverted_index)

    # 读取数据
    with open(dataset, 'rb') as f:  # 打开文件
        new_kw_files = pickle.load(f)

    t1=time.time()

    blockchain_addfile_index={}
    for kw in new_kw_files:
        l=new_kw_files[kw]
        nonce=l[0].encode('utf-8')
        
        for j in range(1,len(l)):            
            state_client,map_server,checklist,blockchain_addfile_index=addfile(kw,nonce,l[j],state_client,map_server,checklist,blockchain_addfile_index)
    
    
    t2=time.time()

    return t2-t1

###################################### 测试插入数据的速度 ##################################
# 400数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('./data/data_400.txt')
# print('400:',t/5)

# 800数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('./data/data_800.txt')
# print('800:',t/5)

# 1200数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('./data/data_1200.txt')
# print('1200:',t/5)

# 1600数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('./data/data_1600.txt')
# print('1600:',t/5)

# 2000数据集
# t=0
# for i in range(5):
#     t=t+experiment_add('./data/data_2000.txt')
# print('2000:',t/5)




def experiment_token(lb,ub):
    '''
    给定上下限，获取用户计算令牌的时间和令牌数量

    Parameters:
    lb:下限，一个整数
    ub:上限，一个整数

    Returns:
    t:用户计算令牌的时间
    n:令牌数量
    '''

    t1=time.time()
    for i in range(int(lb),int(ub+1)):
        kw=str(i)
        Toekn_S_Addr, Toekn_S_Enc, Token_block, start_file_addr=user_search_keyword_mutiple(state_client,kw)
    t2=time.time()

    return t2-t1

############################ 测试计算搜索令牌的速度 ##########################
# 先用10K数据集进行build
# with open('./data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# map_server,checklist,state_client=Build_index(inverted_index)


# 0-200范围
# total_t=0
# for i in range(5):
#     t=experiment_token(0,200)
#     total_t=total_t+t
# print('0-200:',total_t/5)

# 0-400范围
# total_t=0
# for i in range(5):
#     t=experiment_token(0,400)
#     total_t=total_t+t
# print('0-400:',total_t/5)

# 0-600范围
# total_t=0
# for i in range(5):
#     t=experiment_token(0,600)
#     total_t=total_t+t
# print('0-600:',total_t/5)

# 0-800范围
# total_t=0
# for i in range(5):
#     t=experiment_token(0,800)
#     total_t=total_t+t
# print('0-800:',total_t/5)

# 0-1000范围
# total_t=0
# for i in range(5):
#     t=experiment_token(0,1000)
#     total_t=total_t+t
# print('0-1000:',total_t/5)







def experiment_search(lb,ub):
    '''
    给定上下限，获取云服务器搜索的时间

    Parameters:
    lb:下限，一个整数
    ub:上限，一个整数

    Returns:
    t:服务器搜索的时间
    '''
    t=0
    for i in range(int(lb),int(ub+1)):
        kw=str(i)
        Toekn_S_Addr, Toekn_S_Enc, Token_block, start_file_addr=user_search_keyword_mutiple(state_client,kw)
        t1=time.time()
        list_search_file_ID=[]
        results=Server_search(Toekn_S_Addr,Toekn_S_Enc,start_file_addr,map_server,list_search_file_ID)
        t2=time.time()
        t=t+t2-t1
    
    
    
    return t



###################### 测试云服务器搜索速度 ###############################
# 先用10K数据集进行build
# with open('./data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# map_server,checklist,state_client=Build_index(inverted_index)

# [0,200]
# 这里随机数据有点问题，关键字200包含2个相同的ind了，导致会一直递归直到爆栈。所以修改初始的倒排索引
# t=0
# for i in range(5):
#     t=t+experiment_search(0,200)
# print('0-200:',t/5)

# [0,400]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,400)
# print('0-400:',t/5)

# [0,600]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,600)
# print('0-600:',t/5)

# [0,800]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,800)
# print('0-800:',t/5)

# [0,1000]
# t=0
# for i in range(5):
#     t=t+experiment_search(0,1000)
# print('0-1000:',t/5)






############################## 测试区块链验证的时间与gas #########################
def verify(results, w3, eth_contract, w):
    '''
    调用智能合约函数，完成第二轮验证

    Parameters:
    results:server返回的密文
    eth_contract:智能合约对象
    from_account:server/client的地址
    l_w_list：一个list容器，储存BRC集合对应的l_w


    Returns:
    is_correct：区块链judge的结果。若密文正确返回True
    gas: 验证中花费的gas
    '''
    l_w_list=[]
    l_w=AES.new(secreat_key,AES.MODE_ECB).encrypt((w+str(0)).zfill(16).encode('utf-8'))   
    l_w_list.append(l_w)


    gas=0

    # 先对搜索结果进行分组，每组100个密文
    # 示例：若results有321个，那么batch_num1=3，batch_last=21
    batch_size=100
    # batch_num1是包含100个密文的分组的数量
    batch_num1=int(len(results)/batch_size)
    # batch_last是不足100个密文的分组中的密文数
    batch_last=int(len(results)%batch_size)

    # 调用智能合约计算每个分组的digest
    for i in range(0,len(results),batch_size):

        # 是最后一个分组
        if len(results)-i < batch_size:
            # 最后一个分组的内容
            partition=results[i:i+batch_last]

            # 调用智能合约计算这个分组的digest
            tx_hash=eth_contract.functions.batch_gethash(partition,len(results)-i,int(i/batch_size)).transact({
                'from':w3.eth.accounts[0], 
                'gasPrice': w3.eth.gasPrice, 
                'gas': 3000000000
            })

        # 不是最后一个分组，分组中的密文数量是满的
        else:
            # 分组的内容
            partition=results[i:i+batch_size]

            # 调用智能合约计算这个分组的digest
            tx_hash=eth_contract.functions.batch_gethash(partition,batch_size,int(i/batch_size)).transact({
                'from':w3.eth.accounts[0], 
                'gasPrice': w3.eth.gasPrice, 
                'gas': 3000000000
            })
        
        # 根据交易的哈希值查找花费的gas
        rp=w3.eth.getTransactionReceipt(tx_hash)
        gas=gas+rp['gasUsed']



    # 调用智能合约，将前面所有分组的digest组合起来计算最终的digest
    # 计算总的分组数量
    total_num=0
    if batch_last==0:
        total_num=batch_num1
    else:
        total_num=batch_num1+1

    eth_contract.functions.getlastxor(total_num-1).transact({
                'from':w3.eth.accounts[0], 
                'gasPrice': w3.eth.gasPrice, 
                'gas': 3000000000
    })
    # 根据交易的哈希值查找花费的gas
    rp=w3.eth.getTransactionReceipt(tx_hash)
    gas=gas+rp['gasUsed']


    # 进行judge
    eth_contract.functions.try_whether_equal(l_w_list[0]).transact({
                'from':w3.eth.accounts[0], 
                'gasPrice': w3.eth.gasPrice, 
                'gas': 3000000000
    })
    # 根据交易的哈希值查找花费的gas
    rp=w3.eth.getTransactionReceipt(tx_hash)
    gas=gas+rp['gasUsed']


    # 读取judge的结果
    return eth_contract.functions.check_equal_or_not().call(),gas




def experiment_judge(lb,ub):
    '''
    给定上下限，获取区块链第二轮验证的时间

    Parameters:
    lb:下限，一个整数
    ub:上限，一个整数

    Returns:
    t:区块链第二轮验证的时间
    gas: 花费的gas
    '''

    t=0
    g=0
    for i in range(int(lb),int(ub+1)):
        kw=str(i)
        Toekn_S_Addr, Toekn_S_Enc, Token_block, start_file_addr=user_search_keyword_mutiple(state_client,kw)
        list_search_file_ID=[]
        results=Server_search(Toekn_S_Addr,Toekn_S_Enc,start_file_addr,map_server,list_search_file_ID)

        # 进行验证
        
        l_w_list=[]
        l_w=AES.new(secreat_key,AES.MODE_ECB).encrypt((kw+str(0)).zfill(16).encode('utf-8'))   
        l_w_list.append(l_w)   
        t1=time.time()
        flag,gas=verify(results,store_var_contract,from_account,l_w_list)
        t2=time.time()
        if not flag:
            print(flag)

        g=g+gas
        t=t+t2-t1

    return t,g



# # 先用10K数据集进行build，并设置检查表
# with open('./data/data_10K.txt', 'rb') as f:  # 打开文件
#         inverted_index = pickle.load(f)
# map_server,checklist,state_client=Build_index(inverted_index)

# for toekn in checklist:
#     tx_hash11 = store_var_contract.functions.set(toekn,checklist[toekn]).transact({
#                     "from": from_account,
#                     "gas": 3000000,
#                     "gasPrice": 0,
#                 })

# secreat_key=secreat_key = hmac.new(b'chen').digest()





# # 0-200
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,200)
#     t=t+delay
#     g=g+gas
# print('0-200:',t/5,g/5)

# # 0-400
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,400)
#     t=t+delay
#     g=g+gas
# print('0-400:',t/5,g/5)

# # 0-600
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,600)
#     t=t+delay
#     g=g+gas
# print('0-600:',t/5,g/5)

# # 0-800
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,800)
#     t=t+delay
#     g=g+gas
# print('0-800:',t/5,g/5)

# # 0-1000
# t=0
# g=0
# for i in range(5):
#     delay,gas=experiment_judge(0,1000)
#     t=t+delay
#     g=g+gas
# print('0-1000:',t/5,g/5)