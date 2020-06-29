import boto3
import os

WAF_REF = os.environ.get('WAF_REF')

waf_split = WAF_REF.split('|')

WAF_RESOURCE_NAME = waf_split[0]
WAF_PHYSICAL_ID = waf_split[1]
WAF_SCOPE = waf_split[2]

WAF_IP_SET_NAME = 'waf-ip-set'

s3 = boto3.resource('s3')
client = boto3.client('wafv2')


def lambda_handler(_event, _context):
    print(f"Event: {_event}")

    objectEvent = _event['Records'][0]['eventName']
    ipSetId = getIpSet()

    print(f"lambda_handler: objectEvent: {objectEvent}")
    print(f"lambda_handler: ipSetId: {ipSetId}")

    if objectEvent == 'ObjectRemoved:Delete':
        print("lambda_handler: delete waf Rules")
        if ipSetId != None:
            deleteIpSet(ipSetId)
    else:
        print("lambda_handler: update waf rules")

        addresses = getAddressesFromBucket(_event)

        if ipSetId != None:
            print("lambda_handler: updateIpSet")
            updateIpSet(addresses, ipSetId)
        else:
            print("lambda_handler: createIpSet")
            createIpSet(addresses)


def getAddressesFromBucket(_event):
    bucket = _event['Records'][0]['s3']['bucket']['name']
    key = _event['Records'][0]['s3']['object']['key']
    print(f"getAddressesFromBucket: bucket: {bucket}")
    print(f"getAddressesFromBucket: key: {key}")

    contents = getFileContents(bucket, key)
    print(f"getAddressesFromBucket: contents: {contents}")

    addresses = contents.splitlines()
    print(f"getAddressesFromBucket: addresses: {addresses}")

    filteredAddresses = list(filter(None, addresses))
    print(f"getAddressesFromBucket: filteredAddresses: {filteredAddresses}")

    return filteredAddresses


def getIpSet():
    response = client.list_ip_sets(
        Scope=WAF_SCOPE,
    )
    ipSets = response['IPSets']
    print(f"getIpSet: response: {response}")
    print(f"getIpSet: ipSets: {ipSets}")

    ipSetId = None
    try:
        for ipSet in ipSets:
            if ipSet["Name"] == WAF_IP_SET_NAME:
                ipSetId = ipSet["Id"]
                break
    except Exception as e:
        print(f"getIpSet: except: {e}")
        return None
    return ipSetId


def createIpSet(addresses):
    response = client.create_ip_set(
        Name=WAF_IP_SET_NAME,
        Scope=WAF_SCOPE,
        IPAddressVersion='IPV4',
        Addresses=addresses
    )
    print(f"createIpSet: response: {response}")


def updateIpSet(addresses, ipSetId):
    lockToken = getLockToken(ipSetId)

    response = client.update_ip_set(
        Name=WAF_IP_SET_NAME,
        Scope=WAF_SCOPE,
        Id=ipSetId,
        Addresses=addresses,
        LockToken=lockToken
    )
    print(f"updateIpSet: response: {response}")


def deleteIpSet(ipSetId):
    lockToken = getLockToken(ipSetId)

    response = client.delete_ip_set(
        Name=WAF_IP_SET_NAME,
        Scope=WAF_SCOPE,
        Id=ipSetId,
        LockToken=lockToken
    )
    print(f"deleteIpSet: response: {response}")


def getLockToken(ipSetId):
    response = client.get_ip_set(
        Name=WAF_IP_SET_NAME,
        Scope=WAF_SCOPE,
        Id=ipSetId
    )
    print(f"getLockToken: response: {response}")
    lockToken = response['LockToken']
    return lockToken


def getFileContents(bucket, key):
    obj = s3.Object(bucket, key)
    contents = obj.get()['Body'].read().decode('utf-8')
    return contents
