# Tx Tracker
## Description
The Tx tracker is divided into two parts.
Part 1. obtain the transaction every once in a minute, and adding it into logical queue or file, or database.
Part 2. check repeatedly at queue (for instance, every once in a minute).
pick up the transaction from queue, and check it whether it has suitable confirmation count or not. if confirmation count is suitable, register transaction data into database and remove from queue, else it will be checked again later (for instance, later a minute).

## Environment Setup

### Install Python 3.x.

### Install dependencies package
``` bash
pip install -r requirements.txt
```

### Database connection setting

``` code
driver = GraphDatabase.driver('***connection uri***', auth=basic_auth('***user***', '***password***'))
```

## Database Schema
I would be able to imagine DB schema as follows:

(:Transaction {blockHash: , blockNumer: from: , gas: , gasPrice: hash: , input: , maxFeePerGas: , maxPriorityFeeGas: , nonce: , to: , transactionIndex: , value: , confirmation: })

### Description about properties
blockHash: block hash which transaction is contained.
blockNumber: block number which transaction is contained.
gas: transaction fee.
gasPrice: not sure.
hash: not sure.
input: not sure.
maxFeeGas: not sure.
maxPriorityFeeGas: not sure.
nonce: not sure.
from: sender's address
to: receiver's address
transactionIndex: transaction index on block
value: still not sure.
confirmation: used confirmation count to be linked the transaction to the chain
