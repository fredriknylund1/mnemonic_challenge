#!/usr/bin/env python3

import requests
import http.client as httplib

# TEST API
def test():

    url = 'http://localhost:8000/transaction'

    passed = 0
    # TEST SUCCESSFUL TRANSACTION
    print("test successful transaction")
    data = "source= 0 destination= 1 amount= 250"
    r = requests.post(url=url, data=data)
    body = r.json()
    if body['success'] == True and body['message'] == 'Successful transaction' and r.status_code == 200:
        passed += 1
        print("OK")
    
    # RETURN MONEY
    data = "source= 1 destination= 0 amount= 250"
    requests.post(url=url, data=data)

    # TEST INVALID SOURCE ACCOUNT
    print("test invalid source account")
    data = "source= 4 destination= 1 amount= 500"
    r = requests.post(url=url, data=data)
    body = r.json()
    if body['success'] == False and body['message'] == 'Invalid source account' and r.status_code == 400:
        passed += 1
        print("OK")

    # TEST INVALID DESTINATION ACCOUNT
    print("test invalid destination account")
    data = "source= 0 destination= 4 amount= 500"
    r = requests.post(url=url, data=data)
    body = r.json()
    if body['success'] == False and body['message'] == 'Invalid destination account' and r.status_code == 400:
        passed += 1
        print("OK")

    # TEST INSUFFICIENT AVAILABLE FUNDS
    print("test insufficient available funds")
    data = "source= 0 destination= 1 amount= 1000"
    r = requests.post(url=url, data=data)
    body = r.json()
    if body['success'] == False and body['message'] == 'Insufficient available funds' and r.status_code == 404:
        passed += 1
        print("OK")

    # TEST INVALID REQUEST FORMAT
    print("test invalid request format")
    data = "source= 0 1 amount= 1000"
    r = requests.post(url=url, data=data)
    body = r.json()
    if body['success'] == False and body['message'] == 'Invalid request format' and r.status_code == 400:
        passed += 1
        print("OK")

    print("Passed " + str(passed) + " of 5 tests!")


   
if __name__ == "__main__":

    test()