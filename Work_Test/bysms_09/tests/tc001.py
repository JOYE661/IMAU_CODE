import  requests,pprint

payload = {
    'action': 'list_customer'
}

response = requests.get('http://localhost/api/mgr/customers',
              params=payload)

pprint.pprint(response.json())
