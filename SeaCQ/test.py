from web3 import Web3
import json
from hexbytes import HexBytes

# 连接到区块链网络
# ganache网络
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# 加载合约地址和ABI
# 合约地址
contract_address='0x50bdca0985E862A2c7b4F09bF8755E714634Be23'
# 从json文件中读取abi
json_file='./contract/build/contracts/ADS.json'
abi=None
with open(json_file,'r') as f:
    contract_json =json.load(f)
    abi=contract_json['abi']

# 生成合约账户
contract=web3.eth.contract(address=contract_address,abi=abi)

# 要传递的数据
s = 'abc'.zfill(16)
hex_s=HexBytes(s)
# hex_s = s.encode('utf-8').hex()
# hex_s = s.encode('utf-8').hex()
num=123813810293102398102938102381029381029381020230238947293842309802938
# 计算大整数num对应的字节数
byte_length=(num.bit_length()+7)//8
# hex_num=HexBytes(num)
hex_num=num.to_bytes(byte_length,byteorder='big')
print(hex_s)
print(HexBytes(num))

# 检查是否可编码
print(web3.is_encodable('bytes16',hex_s))
print(web3.is_encodable('bytes1[]', [b'\x00',b'\x01',b'\x02']))
print([bytearray([b]) for b in hex_num])


# 调用智能合约
# contract.functions.test(10).call()
contract.functions.setADS(hex_s,[b'\x00',b'\x01',b'\x02']).transact({'from':web3.eth.accounts[0], 'gasPrice': web3.eth.gasPrice, 'gas': web3.eth.getBlock('latest').gasLimit})
r=contract.functions.getADS(hex_s).call()
print(r)