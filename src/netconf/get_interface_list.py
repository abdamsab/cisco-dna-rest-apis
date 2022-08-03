from ncclient import manager
import xmltodict
import xml.dom.minidom
import env_lab
from pprint import pprint

# Create an XML filter for targeted NETCONF queries
netconf_filter = """
<filter>
    <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
        <interface></interface>
    </interfaces>
</filter>
"""

with manager.connect(
    host=env_lab.IOS_XE_1['host'],
    port=env_lab.IOS_XE_1['netconf_port'],
    username=env_lab.IOS_XE_1['username'],
    password=env_lab.IOS_XE_1['password'],
    hostkey_verify=False
) as m:
    netconf_reply = m.get_config(source = 'running', filter=netconf_filter)
print(xml.dom.minidom.parseString(netconf_reply.xml).toprettyxml())

# parse the returned XML to an Ordered Dictionary
netconf_data = xmltodict.parse(netconf_reply.xml)['rpc-reply']['data']
#pprint(netconf_data)

# Create a list of interfaces
interfaces = netconf_data['interfaces']['interface']
#print(interfaces)

for interface in interfaces:
    print("Interface {} enabled status is {}".format(
            interface['name'],
            interface['enabled']
        ))

