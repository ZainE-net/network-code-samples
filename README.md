# Zain's Network Automation Samples

This repository aims to demonstrate how to **programmatically** interact with a Cisco IOS-XE device using either the CLI or REST.  We will address a real-world scenario that this type of code can answer.

### Scenario
Imagine you are planning for a major hardware replacement in your data center. It's your first time taking on such major work, but you've heard from your boss and colleagues that in the past these infrastructure changes have caused a lot of issues the next business day. 

Your boss wants to avoid any misses this time around, and asks you to look at "automation" or a "devops" solution to validate the change. They might sound like buzzwords - but hopefully these simple examples demonstrate the value of bringing code into a traditional network infrastructure replacement.



## The ARP Table
Certainly if ARP is not working at all on your new replacement hardware, you will notice without any help. The hardware likely would not be reachable. What's more difficult is when a few ARP entries are missing out of thousands. These could represent something more sinister, like an SVI that is missing or broken on your new switch - leaving a number of servers trapped in their own little Layer 2 island. 

### Sample ARP Table CLI output:

	csr1000v-1#sh ip arp
	Protocol  Address          Age (min)  Hardware Addr   Type   Interface
	Internet  4.4.4.3                 -   0000.0c07.ac0a  ARPA   GigabitEthernet2.40
	Internet  4.4.4.4                 -   0050.56bf.4ea3  ARPA   GigabitEthernet2.40
	Internet  10.10.0.74              -   0050.56bf.7db4  ARPA   GigabitEthernet3
	Internet  10.10.10.10             -   0050.56bf.4ea3  ARPA   GigabitEthernet2
	Internet  10.10.20.28             7   0050.56bf.490f  ARPA   GigabitEthernet1
	Internet  10.10.20.48             -   0050.56bf.78ac  ARPA   GigabitEthernet1
	Internet  10.10.20.254           52   0050.56bf.d636  ARPA   GigabitEthernet1


### Retrieving the ARP table from the CLI in Python
The first thing we need to do is get the same ARP table output we see above - but our code needs to get it. We are using Kirk Byers' netmiko python module to open the SSH connection to our device and get the response. 

    def cisco_cli_query (host, command):
	"""
	Open a connection to the Host CLI via Netmiko
	The command parameter will be sent to the CLI and the response will be returned
	"""
	
	csr = {
		'device_type': 'cisco_ios',
		'host': host,
		'username': username,
		'password': password
		}
	try:
		csr_connection = ConnectHandler(**csr)
		output = csr_connection.send_command(command)
		return output
	except:
		print('CLI query failed - program will exit')
		quit()

In the python function above, we will connect to the device's CLI via SSH, and issue a command. In this case that command is "show ip arp". The response is recorded in the variable **output** as a single large string. Finally! We have the ARP table stored in memory and we can start writing code to compare ARP tables...right?

### Converting Unstructured Data
Unfortunately, the CLI is designed for human consumption. It's output is one big string that is spaced out to look like a table, but in memory it exists as one big ugly string. In programming terms, this would be `'Unstructured'` data. 

Here is what the raw ARP table output looked like in the python interpreter:

	cisco_cli_query(host, 'show ip arp')
> 'Protocol  Address          Age (min)  Hardware Addr   Type   Interface\nInternet  4.4.4.3                 -   0000.0c07.ac0a  ARPA   GigabitEthernet2.40\nInternet  4.4.4.4                 -   0050.56bf.4ea3  ARPA   GigabitEthernet2.40\nInternet  10.10.0.74              -   0050.56bf.7db4  ARPA   GigabitEthernet3\nInternet  10.10.10.10             -   0050.56bf.4ea3  ARPA   GigabitEthernet2\nInternet  10.10.20.28             8   0050.56bf.490f  ARPA   GigabitEthernet1\nInternet  10.10.20.48             -   0050.56bf.78ac  ARPA   GigabitEthernet1\nInternet  10.10.20.254          100   0050.56bf.d636  ARPA   GigabitEthernet1'

Not exactly pretty is it? Since all the elements are there in the string somewhere, we will employ the powerful **regular expression** library that comes with python to extract the relevant data.

    def structurize_arp_table (arp_table_raw):
	"""
	Parse the raw unstructured CLI output from a 'show ip arp' command
	The regular expression below is designed to extract the IP Address, MAC Address, and Interface	
	"""
	
	arp_rex = '(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}).+(\\w{4}\\.\\w{4}.\\w{4}).+?(\\S+)$'
	arp_table = re.findall(arp_rex, arp_table_raw, re.MULTILINE)
	return arp_table
Have a look at the code above - specifically the arp_rex variable. This is a regular expression that is designed to **capture** the fields we want. The **IP Address**, the **MAC address**, and the **Interface**. Take a look at the result:

	arp = structurize_arp_table(cisco_cli_query(host, 'show ip arp'))
	print(*arp, sep='\n')
	('4.4.4.3', '0000.0c07.ac0a', 'GigabitEthernet2.40')
	('4.4.4.4', '0050.56bf.4ea3', 'GigabitEthernet2.40')
	('10.10.0.74', '0050.56bf.7db4', 'GigabitEthernet3')
	('10.10.10.10', '0050.56bf.4ea3', 'GigabitEthernet2')
	('10.10.20.28', '0050.56bf.490f', 'GigabitEthernet1')
	('10.10.20.48', '0050.56bf.78ac', 'GigabitEthernet1')
	('10.10.20.254', '0050.56bf.d636', 'GigabitEthernet1')

Looks a lot better right? You can start to see how we could get and compare two of these ARP tables. Or other data sets like routing peers, VxLAN VNIs, IP SLA Data, Port Authentications, etc.

You can take things a step farther, for example if you find some ARP entry is missing - you can have your code do a **DNS Lookup**, or query any **IP Address Manager** for details on the IP. Your code can put that sort of information immediately in front of you, so you have more time to address the actual issue - and with the right data. 


## How do APIs factor in?
If you're particularly savvy, you may have realized that the regular expression string we created to turn the ARP table output into structured data won't work for other output. You'll need to come up with a way to extract the data from each command you send to the CLI before you can really start working with dataset. 

Unlike the CLI, newer methods to communicate with devices such as Netconf or Restconf are designed to be consumed programatically. The data comes back from the device in a structured package. Have a  look at the data that is returned by the **RESTCONF** sample code.

    def cisco_rest_query(host, suffix=''):
	"""
	Make an HTTPS GET request to a Cisco device with restconf enabled
	Suffix is added to the restconf root URI
	"""
	
	uri = 'https://{}:443/restconf/data/{}'.format(host,suffix)
	headers = { 'Accept':'application/yang-data+json' }
	
	try:
		response = requests.get(uri, auth=(username,password), headers=headers, verify=False)
		if response.status_code != 200:
			print('Non-200 GET response, program will exit')
			print(response.status_code)
			quit()
		return response.json()
	except:
		print('HTTPS query failed - program will exit')
		quit()

	{'address': '4.4.4.3', 'enctype': 'ios-encaps-type-arpa', 'interface': 'GigabitEthernet2.40', 'type': 'ios-linktype-ip', 'mode': 'ios-arp-mode-app-alias', 'hwtype': 'ios-snpa-type-ieee48', 'hardware': '00:00:0c:07:ac:0a', 'time': '2021-04-28T07:18:22.815+00:00'}

This is just one of the ARP entries returned from the query. You can see not only is the data structured as a JSON dictionary already, but there's actually more data than we get from issuing a 'show ip arp' on the CLI.


## Thanks for Reading
Hopefully if you are reading this you found it useful. Let me know if you would like to see more similar content.
