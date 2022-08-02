from textwrap import indent
import requests
import json
import logging
from requests.auth import HTTPBasicAuth
import os
import sys

# Get the absolute path for the directory where this file is located "here"
here = os.path.abspath(os.path.dirname(__file__))
#print(here)

# Get the absolute path for the project / repository root
project_root = os.path.abspath(os.path.join(here, "../.."))

#Extend the system path to include the project root and import the files
sys.path.insert(0, project_root)

import env_lab

DNAC_URL = env_lab.DNA_CENTER['host']
DNAC_USER = env_lab.DNA_CENTER['username']
DNAC_PASS = env_lab.DNA_CENTER['password']

"""
    this code snippet will run execute operational commands across your
    entire network using Cisco DNA Center command Runner APIs
"""

def get_auth_token():
    """
    Building out Auth request. using requests.post to make a call to the Auth Endpoint
    """
    token = ''
    url = 'https://{}/dna/system/api/v1/auth/token'.format(DNAC_URL)
    hdr = {'content-type': 'application/json'}
    try:
        logging.captureWarnings(True)
        resp = requests.post(url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASS), headers=hdr, verify=False)
        token = resp.json()['Token']
    except Exception as e:
        print('Error: ', e)
    return token



def get_device_list():
    """
    Building out function to retrieve list of devices. Using requests.get to make a call to the network device Endpoint
    """
    token = get_auth_token()
    url = "https://{}/api/v1/network-device/1/4".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type': 'application/json'}
    logging.captureWarnings(True)
    resp = requests.get(url, headers=hdr, verify=False)
    device_list = resp.json()
    #print(json.dumps(device_list, indent=4, sort_keys=True))
    print("{0:25}{1:25}".format("hostname", "id"))
    for device in device_list['response']:
        print("{0:25}{1:25}".format(device['hostname'], device['id']))
    initiate_cmd_runner(token)




def initiate_cmd_runner(token):
    ios_cmd = "show ver | inc RELEASE"
    #ios_cmd = "show ver"
    device_id = str(input("Cpoy/Past a device ID here: "))
    print("Executing ios command --> ", ios_cmd)
    param = {
        "name": "Show Command",
        "commands": [ios_cmd],
        "deviceUuids": [device_id]
    }
    url = "https://{}/api/v1/network-device-poller/cli/read-request".format(DNAC_URL)
    hdr = {'x-auth-token': token, 'content-type': 'application/json'}
    logging.captureWarnings(True)
    response = requests.post(url, data=json.dumps(param), headers=hdr, verify=False)
    task_resp = response.json()
    #print(json.dumps(task_resp, indent=4, sort_keys=True))
    task_id = task_resp['response']['taskId']
    task_url = task_resp['response']['url']
    print("Command runner Initiated! Task Id --> ", task_id)
    print("Retrieving Command Results... ")
    get_task_info(task_id, task_url, token)




def get_task_info(task_id, task_url, token):
    url = "https://{}{}".format(DNAC_URL, task_url) #this will also work "https://{}/api/v1/task/{}".format(DNAC_URL, task_id)
    hdr = {'x-auth-token': token, 'content-type': 'application/json'}
    logging.captureWarnings(True)
    task_result = requests.get(url, headers=hdr, verify=False)
    result_resp = task_result.json()
    #print(json.dumps(result_resp, indent=4, sort_keys=True))
    file_id = result_resp['response']['progress']
    if "fileId" in file_id:
        #print(file_id)
        unwanted_chars = '{"}'
        for char in unwanted_chars:
            file_id = file_id.replace(char, '')
        #print(file_id)
        file_id = file_id.split(':')
        file_id = file_id[1]
        print("File ID --> ", file_id)
    else:   #keep checking for task completion
        get_task_info(task_id, task_url, token)
    get_cmd_output(token, file_id)

def get_cmd_output(token, file_id):
    url = "https://{}/api/v1/file/{}".format(DNAC_URL, file_id)
    hdr = {'x-auth-token': token, 'content-type': 'application/json'}
    logging.captureWarnings(True)
    cmd_result = requests.get(url, headers=hdr, verify=False)
    print(json.dumps(cmd_result.json(), indent=4, sort_keys=True))


if __name__ == "__main__":
    get_device_list()