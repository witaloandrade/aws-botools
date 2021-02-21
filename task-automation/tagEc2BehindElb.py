# Witalo Andrade - Feb 2021
# This Script will create a database file "data" with all albs
# after that it will check every ec2 if it is behind an elb

import json
import boto3
import time

# Pull list of regions from aws
ec2 = boto3.client('ec2')
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

for each_reg in regions:
    print("\033[92m","Working on ", each_reg ,"\033[0m")
    ec2client = boto3.client('ec2',region_name=each_reg)
    elbclient = boto3.client('elbv2',region_name=each_reg)

    print("\033[92m","Creating ELB Database","\033[0m")
    elbresponse = elbclient.describe_target_groups()
    data = {}
    data['TargetGroups'] = []
    for i in range(0,len(elbresponse['TargetGroups'])):
        tg = elbclient.describe_target_health(TargetGroupArn=elbresponse['TargetGroups'][i]['TargetGroupArn'])
        for j in range(0,len(tg['TargetHealthDescriptions'])):
            #print(tg['TargetHealthDescriptions'][j]['Target'])
            d = {
                'Name': elbresponse['TargetGroups'][i]['TargetGroupName'],
                'Id' : tg['TargetHealthDescriptions'][j]['Target']['Id'],
                'Port': tg['TargetHealthDescriptions'][j]['Target']['Port']
            }
            data['TargetGroups'].append(d)

    # Uncomment this if you want to lave a copy of the file locally
    #with open(str(each_reg + '.json'), 'w') as outfile:
    #    json.dump(data, outfile)

    print("\033[92m","Listing Ec2","\033[0m")
    ec2response = ec2client.describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': ['stopped']
        },
        {
            'Name': 'tag:Name',
            'Values': ['xyz']
        }
    ]
    )
    print("\033[92m","Checking Ec2 for ELB","\033[0m")
    for reservation in ec2response['Reservations']:
        for instance_description in reservation['Instances']:
            tgmember = []
            for tg in data['TargetGroups']:
                if instance_description['InstanceId'] == tg['Id']:
                    tgmember.append(tg['Name'])
            if len(tgmember) != 0:
                ec2_tags = []
                ec2_tags.append({'Key':'ELBv2TargetGroups', 'Value':', '.join(map(str, tgmember))})
                print("Tagging ec2", instance_description['InstanceId'] )
                print("Will add tags: ", ec2_tags)
                ec2client.create_tags(Resources=[instance_description['InstanceId']], Tags=ec2_tags)
