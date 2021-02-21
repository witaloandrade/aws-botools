# Witalo Andrade - Jan 2021
# This script will copy tags from ssm and add them to ec2 instances
# How to use this script: run it passing the aws profile name you configured:
# python3 ./ebsTaggingFEc2TaggingFromSmm.py <aws-profile-name>

import boto3
import sys
from botocore.exceptions import ClientError
from datetime import datetime

startTime = datetime.now()

# Catch profile name from arg that user will provide
prof=sys.argv[1]

# Pull list of regions from aws
ec2 = boto3.client('ec2')
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Pull Tags from ssm and push to aws
print(bcolors.WARNING + "Starting Execution for aws Account:", prof + bcolors.ENDC)
for each_reg in regions:
    print(bcolors.OKBLUE + 'Running on aws region {}'.format(each_reg) + bcolors.ENDC)
    session=boto3.Session(profile_name=prof,region_name=each_reg)
    ssm = session.client('ssm', region_name=each_reg)
    ec2 = session.client('ec2', region_name=each_reg)
    paginator = ssm.get_paginator('describe_instance_information')
    for response in paginator.paginate():
        for instance in response['InstanceInformationList']:
            Ids = []
            Ids.append(instance["InstanceId"])
            tagsDicList = [
                {'Key':'Hostname', 'Value':instance["ComputerName"].split('.')[0]},
                {'Key':'OSType', 'Value':instance["PlatformType"]},
                {'Key':'OSName', 'Value':instance["PlatformName"]},
                {'Key':'OSVersion', 'Value':instance["PlatformVersion"]},
                {'Key':'AWS-Snapshot-Daily', 'Value':'Yes'}
            ]
            if len(instance["ComputerName"].split('.')) >= 2:
                tagsDicList.append({'Key':'Domain', 'Value':instance["ComputerName"].split('.')[1]})
            else:
                tagsDicList.append({'Key':'Domain', 'Value':'None'})
            try:
                print("Adding tags to ec2: ", Ids)
                response = ec2.create_tags(Resources=Ids,Tags=tagsDicList,DryRun=False)
                #print(response)
            except ClientError as e:
                if e.response['Error'].get('Code') == 'DryRunOperation':
                    # Success
                    print("DryRun: Would have successfully tagged {} with tags {}".format(Ids, tagsDicList))
                    print()
                else:
                   # failure
                    print( bcolors.FAIL + "Error to tag {}".format(Ids) + bcolors.ENDC)
                    print(e)
            #print(tagsDicList)
print("Execution time: ", datetime.now() - startTime)
