# SeaCQ

## File Structure

~~~
SeaCQ
│  .gitignore
│  README.md
│  temp.txt
│  
├─contract			// Smart contracts for our schemes SeaCQ, FB-SeaCQ, FB-SeaCQ*
│  │  truffle-config.js
│  │  
│  ├─contracts
│  │      .gitkeep
│  │      io.sol	// Smart contract.
│  │      
│  ├─migrations
│  │      .gitkeep
│  │      1_migration.js
│  │      
│  └─test
│          .gitkeep
│          
├─dataset		
│      gen_dataset.py		// Generate datasets of different sizes.
│      
├─FB-SeaCQ				// Our scheme: FB-SeaCQ
│      Accumulator.py	// RSA accumulator
│      experiment.py	// Experiment APIs
│      main.py			// The main method
│      numbthy.py		// The number theory libarary
│      owner.py			// Functions of the owner
│      server.py		// Functions of the server
│      test.py
│      
├─FB-SeaCQ-star			// Our scheme: FB-SeaCQ*
│      Accumulator.py
│      experiment.py	
│      main.py		
│      numbthy.py
│      owner.py
│      server.py
│      test.py
│      
├─Guo					// Guo's scheme: BVF-SSE
│  │  experiment.py		// Experiment APIs
│  │  gen_data.py
│  │  ICC20.py			// Basic functions
│  │  main.py			// Main function
│  │  test.py
│  │  
│  └─contract			// Smart contract for BVF-SSE
│      │  truffle-config.js
│      │  
│      ├─contracts
│      │      .gitkeep
│      │      contract.sol
│      │      
│      ├─migrations
│      │      .gitkeep
│      │      1_migration.js
│      │      
│      └─test
│              .gitkeep
│              
├─SeaCQ					// SeaCQ
│      Accumulator.py
│      experiment.py
│      main.py
│      numbthy.py
│      owner.py
│      server.py
│      test.py
│      
└─vsChain				// Cui's scheme: vschain
    │  binSearchTree.py		// The binary search tree class
    │  experiment.py		// Experiment APIs
    │  gen_data.py			
    │  main.py				// Main function
    │  owner.py				// The owner class
    │  round.py				// Round class for authenticated join queries
    │  server.py			// The server class
    │  test.py				
    │  
    └─contract				// Smart contract for vschain
        │  truffle-config.js
        │  
        ├─contracts
        │      .gitkeep
        │      merkle.sol
        │      
        ├─migrations
        │      .gitkeep
        │      1_migration.js
        │      
        └─test
                .gitkeep
~~~



## Baseline

[1] Cui N, Wang D, Li J, et al. Enabling Efficient, Verifiable, and Secure Conjunctive Keyword Search in Hybrid-Storage Blockchains[J]. IEEE Transactions on Knowledge and Data Engineering, 2023.

[2] Guo Y, Zhang C, Wang C, et al. Towards public verifiable and forward-privacy encrypted search by using blockchain[J]. IEEE Transactions on Dependable and Secure Computing, 2022, 20(3): 2111-2126.



## Prepare Environment

Intel(R) Core(TM) i7-10700 [CPU@2.60GHz](mailto:CPU@2.60GHz) ，16GB RAM,

Ubuntu 18.04 Server,

python 3.6, solidity 0.5.17



## Building Procedure

### Init

Use dataset/gen_dataset.py to generate datasets.

Install the Truffle:

~~~bash
npm install -g truffle
~~~

Install the Ganache into the Truffle:

~~~bash
npm install ganache --global
~~~

### SeaCQ

~~~bash
# Start the ganache private chain
ganache -a 2

# In a new session
cd contract
truffle migrate
#Copy the contract address and paste it into the main method
cd ../SeaCQ
python main.py
~~~

### FB-SeaCQ

~~~bash
# Start the ganache private chain
ganache -a 2

# In a new session
cd contract
truffle migrate
#Copy the contract address and paste it into the main method
cd ../FB-SeaCQ
python main.py
~~~

### FB-SeaCQ*

~~~bash
# Start the ganache private chain
ganache -a 2

# In a new session
cd contract
truffle migrate
#Copy the contract address and paste it into the main method
cd ../FB-SeaCQ-star
python main.py
~~~

### BVF-SSE

~~~bash
# Start the ganache private chain
ganache -a 2

# In a new session
cd Guo
cd contract
truffle migrate
#Copy the contract address and paste it into the main method
cd ..
python main.py
~~~

### vschain

~~~bash
# Start the ganache private chain
ganache -a 2

# In a new session
cd vsChain
cd contract
truffle migrate
#Copy the contract address and paste it into the main method
cd ..
python main.py
~~~



## Contact

[yangxu@stu.xjtu.edu.cn](mailto:yangxu@stu.xjtu.edu.cn)

[hgzhao@stu.xjtu.edu.cn](mailto:hgzhao@stu.xjtu.edu.cn)