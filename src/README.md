HOW TO RUN
server: 
~ python3 server.py

test:
~ python3 test.py

API for simple bank transaction between two accounts.
Format of transaction request: 
 POST /transaction http/1.1
 headers
 body: 
 "source= {source_account.id} dest= {destination_account.id} amount= {amount}"

NOTES

This is a simple API which handles just one type of request. It could easily be modified to be 
able to handle other types of request. If necessary, a framework like flask could be used to
make the request handling and routing more elegant. A test file is used to test that the API fulfills the requirements of the assignment.

Although this implementation fulfills the requirements for this assignment, it is not suitable for any kind of production use. There are several points which has to be addressed to make it suitable for production:
1)
Securing the confidentiality of messages sent between server and client. TLS (Transport layer security) can be used to assure a secure connection between client and host. This would be of great importance, especially since there are bank transaction details which are sent over the network. 
2)
Safe storage of user and transaction data on server side. For this assignment, the account data is stored in plaintext in a json file. For production, it would be wise to store the account data encrypted in a database.
3)
It is also important to regulate the incoming request, to protect from requests created by malicious users to perform actions with malicious intent. Examples of this includes restricting the content of the request body, to deny any attempts at buffer overflow attacks. 
4) 
For a bank transaction, it is extremely import to ensure that is fulfills the ACID (Atomic, consistency, isolation, durability) properties. It must be assured that either the transaction finished, or the state must be rolled back to where it was before the operation started. 



