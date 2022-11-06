import socketserver
from os import path
import sys
import json
import time
import random

HOST = "127.0.0.1"
PORT = 8000

ACCOUNTS_FILE = 'accounts.json'

status_OK = 'HTTP/1.1 200 OK\r\n'
status_BAD_REQUEST = 'HTTP/1.1 400 Bad Request\r\n'
status_NOT_FOUND = 'HTTP/1.1 404 Not Found \r\n'

# CLASS FOR HANDLING TCP CONNECTIONS.
class TcpHandler(socketserver.StreamRequestHandler):

    # HANDLES CONNECTIONS
    def handle(self):
        self.content_length = 0

        # READS THE FIRST LINE OF THE REQUEST HEADER.
        self.request_line = self.rfile.readline().decode('ascii')

        # SPLIT REQUEST LINE INTO THE GIVEN ELEMENTS.
        request_line_list = self.request_line.split()

        # 
        if request_line_list[0] == 'POST':
            self.post_handler(request_line_list[1])

    # HANDLES POST REQUESTS
    def post_handler(self, resource):

        if resource == '/transaction':
            self.transaction()

    # HANDLES A TRANSACTION
    # TRANSACTION REQUEST BODY SHOULD BE ON FORMAT = "source= {source_account.id} dest= {destination_Account.id} amount= {amount}"
    def transaction(self):

         # READS HEADER LINES TO GET CONTENT LENGTH OF REQUEST.
        self.read_until_body()

        # GET TRANSACTION ELEMENTS FROM BODY
        body_elements = self.rfile.read(self.content_length).decode('ascii').split()

        # CHECKS THAT THE REQUEST IS SENT IN THE CORRECT FORMAT
        if len(body_elements) != 6:
            transaction_result = self.create_transaction_result(0, 0, 0, False, 'Invalid request format')
            self.response(status_BAD_REQUEST, transaction_result)
            return

        # RETRIEVES THE NEEDED ACCOUNT AND AMOUNT INFORMATION FROM THE REQUEST
        src = int(body_elements[1])
        dest = int(body_elements[3])
        amount = int(body_elements[5])

        # GET JSON CONTENT OF ACCOUNTS
        content = read_from_json(ACCOUNTS_FILE)
        accounts = content['accounts']
        dest_account = {
            'id': -1, 
            'name': '', 
            'available_funds': 0
            }
        src_account = {
            'id': -1, 
            'name': '', 
            'available_funds': 0
            }

        # LOOP THROUGH ACCOUNTS TO FIND DESTINATION AND SOURCE ACCOUNTS.
        for account in accounts:
            if dest == account['id']:
                dest_account = account 
            if src == account['id']:
                src_account = account

        # CHECK IF INVALID SOURCE ACCOUNT 
        if src_account['id'] == -1:
            transaction_result = self.create_transaction_result(src, dest, amount, False, 'Invalid source account')
            self.response(status_BAD_REQUEST, transaction_result)
            return 
        # CHECK IF INVALID DESTINATION ACCOUNT
        if dest_account['id'] == -1:
            transaction_result = self.create_transaction_result(src, dest, amount, False, 'Invalid destination account')
            self.response(status_BAD_REQUEST, transaction_result)
            return 

        # CHECK IF ENOUGH FUNDS ON SOURCE ACCOUNT TO COMPLETE TRANSACTION
        if src_account['available_funds'] < amount:
            transaction_result = self.create_transaction_result(src, dest, amount, False, 'Insufficient available funds')
            self.response(status_NOT_FOUND, transaction_result)
            return

        # COMPLETE TRANSACTION
        dest_account['available_funds'] = dest_account['available_funds'] + amount
        src_account['available_funds'] = src_account['available_funds'] - amount

        # WRITE BACK TO ACCOUNT FILE
        write_to_json(ACCOUNTS_FILE, content)


        # CREATE TRANSACTION 
        transaction_result = self.create_transaction_result(src, dest, amount, True, 'Successful transaction')

        # SEND RESPONSE FOR SUCCESSFUL TRANSACTION
        self.response(status_OK, transaction_result)

    # READS THE HEADERLINES OF A REQUEST, RETURNS WITH THE BODY AS THE NEXT LINE TO READ OF RFILE.
    # RETRIEVES AND SAVES CONTENT LENGTH OF REQUEST.
    def read_until_body(self):

        line = self.rfile.readline().decode('ascii')

        while line:
            # IF BLANK LINE RETURN, BECAUSE BODY STARTS ON NEXT LINE.
            if line == '\r\n':
                return line

            # SPLIT LINE INTO LIST OF ELEMENTS
            line_list = line.split()

            # CHECK IF CONTENT-LENGTH LINE
            if line_list[0] == 'Content-Length:':
                self.content_length = int(line_list[1])

            # READ NEXT LINE OF REQUEST
            line = self.rfile.readline().decode('ascii')

    # CREATES RESPONSE MESSAGE AND SENDS IT TO CLIENT
    def response(self, status, content):

        # CONVERTS CONTENT INTO JSON FORMAT.
        body = json.dumps(content, indent=4).encode('utf-8')
        # GET SIZE OF BODY
        content_length = sys.getsizeof(body)

        # CREATE HEADER AND RESPONS.
        header_lines = ('Content-Length: ' + str(content_length) + '\r\n'
            + 'Content-Type: application/json' + '\r\n')

        response = bytes(status + header_lines + '\r\n', 'ascii') + body

        self.wfile.write(response)

    # CREATES TRANSACTION RESULT
    def create_transaction_result(self, src, dest, amount, success, message):

        # GET TIMESTAMP
        timestamp = int(time.time())

        transaction = {
            'id': random.randrange(0, 1000000),
            'time': timestamp,
            'success': success,
            'message': message,
            'amount': amount,
            'src_account': src,
            'dest_account': dest
        }

        return transaction

# WRITES DATA TO A JSON FILE
def write_to_json(filename, content):
    wfile = open(filename, 'w')
    json.dump(content, wfile, indent=4)
    wfile.close()

# READS DATA FROM A JSON FILE AND FORMATS IT
def read_from_json(filename):
    if sys.getsizeof(filename) > 0:
        rfile = open(filename)
        content = json.load(rfile)
        rfile.close()

        return content
                    
                
if __name__ == "__main__":
    HOST, PORT = "localhost", 8000
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), TcpHandler) as server:
        print("Serving at: http://{}:{}".format(HOST, PORT))
        server.serve_forever()