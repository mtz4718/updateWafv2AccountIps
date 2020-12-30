import boto3
import json

# Define IP-Set Info
wafIpName='Local-Account_IPSet'
wafIpSetId='09b16840-689d-4c57-b977-92d119d7bd6d'
wafIpSetScope='REGIONAL'


# Define credential session
client = boto3.client('wafv2')
# Get all pub ips from all regions in account, return <list>
def pullPubIps():
    session = boto3.session.Session()
    client = boto3.client('ec2')
    regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    foundIps = []
    appendCidr = '/32'
    for region in regions:
        ec2 = session.resource('ec2', region_name=region)
        for vpc in ec2.vpcs.all():
            for eni in vpc.network_interfaces.all():
                if eni.association_attribute:
                    foundIps.append(eni.association_attribute['PublicIp'])
    formatIps = [ip + appendCidr for ip in foundIps]
    return formatIps
# Get Lock Token for defined IP Set
def getLockToken():
    lockToken = client.get_ip_set(Id=wafIpSetId,Scope=wafIpSetScope,Name=wafIpName)['LockToken']
    return lockToken

# Push Updated IpSet
def pushIpSet():
    response = client.update_ip_set(
        Name=wafIpName,
        Scope=wafIpSetScope,
        Id=wafIpSetId,
        Addresses=pullPubIps(),
        LockToken=getLockToken()
    )
    return response

pushIpSet()

