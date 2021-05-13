from getpass import getpass
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def cisco_rest_query(host, suffix=''):
	"""
	Make an HTTPS GET request to a Cisco device with restconf enabled
	Suffix is added to the restconf root URI
	"""
	
	uri = 'https://{}:443/restconf/data/{}'.format(host,suffix)
	headers = { 'Accept':'application/yang-data+json' }
	
	response = requests.get(uri, auth=(username,password), headers=headers, verify=False)
	response.raise_for_status()
	
	return response.json()

def rest_arp_table_example():
	"""
	Call the specific YANG module that returns operational arp data
	"""
	
	arp_json = cisco_rest_query(host, 'Cisco-IOS-XE-arp-oper:arp-data')
	
	return arp_json
	
if __name__ == '__main__':

	#We will use Cisco's public Devnet lab CSR (that means you can run this code yourself - credentials are developer/C1sco12345
	host = 'sandbox-iosxe-latest-1.cisco.com'
	
	#prompt for credentials - password does not echo
	username = input('Username:')
	password = getpass('Password:')
	
	arp = rest_arp_table_example()
	
	for entry in arp['Cisco-IOS-XE-arp-oper:arp-data']['arp-vrf'][0]['arp-oper']:
		print(entry)