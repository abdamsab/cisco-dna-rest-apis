from email import header
import requests
from requests.auth import HTTPBasicAuth
import argparse
import json
from dnac_config import DNAC_IP, DNAC_PORT, DNAC_USER, DNAC_PASSWORD
from pprint import pprint

parser = argparse.ArgumentParser()
requests.packages.urllib3.disable_warnings()

# Command Line Parameters for Source and Destination IP
parser.add_argument("source_ip", help="Source IP Address")
parser.add_argument("destination_ip", help="Destination IP Address")
args = parser.parse_args()

# Get Source and Destination IPs from Command Line
source_ip = args.source_ip
destination_ip = args.destination_ip

def filter_host(host):
    if host['hostIp'] == source_ip or host['hostIp'] == destination_ip:
        return True
    return False

def apic_login(host, username, password):
    """
    Use the REST API to log into an APIC-EM and retrieve ticket
    """
    url = "https://{}/api/system/v1/auth/token".format(host)
    # Make login request and return the response body
    response = requests.request("POST", url, auth=HTTPBasicAuth(username, password), verify=False)
    token = response.json()['Token']
    return token

def get_host_list():
    url ="https://{}/api/v1/host".format(DNAC_IP)
    hdr = {'x-auth-token': ticket, 'content-type': 'application/json'}
    response = requests.get(url, headers=hdr, verify=False)
    host_list = response.json()['response']
    filtered_list = filter(filter_host, host_list)
    filtered_list = list(filtered_list)
    print_host(filtered_list)
    get_device_list(filtered_list)
    




def get_device_list(host_list):
    for host in host_list:
        if host['hostIp'] == source_ip:
            source_device_id = host['connectedNetworkDeviceId']
            source_connected_interface_id = host['connectedInterfaceId']
        if host['hostIp'] == destination_ip:
             destination_device_id = host['connectedNetworkDeviceId']
             destination_connected_interface_id = host['connectedInterfaceId']

    filter_device = []   

    url = "https://{}/api/v1/network-device".format(DNAC_IP)
    hdr = {'x-auth-token': ticket, 'content-type': 'application/json'}
    response = requests.get(url, headers=hdr, verify=False)
    device_list = response.json()['response']
    for device in device_list:
        if device['id'] == source_device_id or device['id'] == destination_device_id:
            filter_device.append(device)
    print_device(filter_device, source_device_id, destination_device_id, source_connected_interface_id, destination_connected_interface_id)




def get_interface(id):
    url = "https://{}/api/v1/interface/{}".format(DNAC_IP, id)
    hdr = {'x-auth-token': ticket, 'content-type': 'application/json'}
    response = requests.get(url, headers=hdr, verify=False)
    interface = response.json()['response']
    print_connected_interface(interface)
 




def perform_flow_analysis():
    url = "https://{}/api/v1/flow-analysis".format(DNAC_IP)
    hdr = {'x-auth-token': ticket, 'content-type': 'application/json'}
    param = {
        'destIP': destination_ip,
        'periodicRefresh': False,
        'sourceIP': source_ip
    }
    response = requests.get(url, data=json.dumps(param), headers=hdr, verify=False)
    path_json = response.json()
    pprint(path_json)
    flow_id = path_json['response']['flowAnalysisId']
    print("Path Trace Initiated! Path ID -----> ", flow_id)
    print("Retrieving Path Trace Results...... ")
    retrieve_path_results(flow_id)




def retrieve_path_results(flow_id):
    url = "https://{}/api/v1/flow-analysis/{}".format(DNAC_IP, flow_id)
    hdr = {'x-auth-token': ticket, 'content-type': 'application/json'}
    path_result = requests.get(url, headers=hdr, verify=False)
    print(json.dumps(path_result.json(), indent=4, sort_keys=True))




def print_host(host_list):
    print("Running Troubleshooting Script for: ")
    print("\tSource IP:\t{}".format(source_ip))
    print("\tDestination IP\t{}".format(destination_ip))
    print('\n')
    for host in host_list:
        if host['hostIp'] == source_ip:
            print('Source Host Details:')
            print('-'*25)
        if host['hostIp'] == destination_ip:
            print('Destination Host Details:')
            print('-'*25)
        print("Host Name: {}\nNetwork Type: {}\nConnected Network Device: {}\nConnected Network InterfaceName: {}\nVLAN: {}\nHost IP: {}\nHost MAC: {}\nHost Sub Type: {}".
            format(
                "Unavailable", 
                host['hostType'], 
                host['connectedNetworkDeviceIpAddress'],
                host['connectedInterfaceName'],
                host['vlanId'],
                host['hostIp'],
                host['hostMac'],
                host['subType']
            ))
        print('\n')




def print_device(device_list, source_device_id, destination_device_id, source_connected_interface_id, destination_connected_interface_id):
    print('\n')
    for device in device_list:
        if device['id'] == source_device_id:
            print('Source Host Network Connection Details:')
            print('-'*35)
        if device['id'] == destination_device_id:
            print('Destination Host Network Connection Details:')
            print('-'*35)
        print("Device Hostname: {}\nManagement IP: {}\nDevice Location: {}\nDevice Type: {}\nPlatform Id: {}\nDevice Role: {}\nSerial Number: {}\nSoftware Version: {}\nUp Time: {}\nReachability Status: {}\nError Code: {}\nError Description: {}".
            format(
                device['hostname'], 
                device['managementIpAddress'], 
                device['location'],
                device['type'],
                device['platformId'],
                device['role'],
                device['serialNumber'],
                device['softwareVersion'],
                device['upTime'],
                device['reachabilityStatus'],
                device['errorCode'],
                device['errorDescription']
            ))
        print('\n')
        if device['id'] == source_device_id:
            get_interface(source_connected_interface_id)
        else:
            get_interface(destination_connected_interface_id)

def print_connected_interface(interface):
    print('\n')
    print('Attached Interface:')
    print('-'*35)
    print("Port Name: {}\nInterface Type: {}\nAdmin Status: {}\nOperational Status: {}\nMedia Type: {}\nSpeed: {}\nDuplex Setting: {}\nPort Mode: {}\nInterface VLAN: {}\nVoice VLAN: {}".
            format(
                interface['portName'], 
                interface['interfaceType'], 
                interface['adminStatus'],
                interface['status'],
                interface['mediaType'],
                interface['speed'],
                interface['duplex'],
                interface['portMode'],
                interface['vlanId'],
                interface['voiceVlan']
            ))
    print('\n')


ticket = apic_login(DNAC_IP, DNAC_USER, DNAC_PASSWORD)
get_host_list()
perform_flow_analysis()





