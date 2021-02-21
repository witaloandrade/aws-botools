# Witalo Andrade - Jan 2021
# This Script will add ec2 data as ec2 tags, like: ip, az, subnet etc.
# How to use this script: run it passing the aws profile name you configured:
# python3 ./createAmi.py <aws-profile-name>

# TO DO's
# Add tag with all ebs the ec2 is member of

import boto3
import os
import sys
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Catch profile name from arg that user will provide
prof=sys.argv[1]

# Pull list of regions from aws
ec2 = boto3.client('ec2')
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]


def lambda_handler(event, context):
  for each_reg in regions:
    print("\033[92m","Working on ", each_reg ,"\033[0m")
    session=boto3.Session(profile_name=prof,region_name=each_reg)
    client  = session.client('ec2')
    response = client.describe_instances(
    Filters=[
            {
                'Name': 'tag:Owner',
                'Values': ['*xyz*']
            },
            {
                'Name': 'tag:Principalid',
                'Values': ['*Witalo*']
            }
    ]
    )
    for reservation in response['Reservations']:
      
      for instance_description in reservation['Instances']:
        #print(instance_description)
        ec2_tags = []
        ec2_tags.append({'Key':'InstanceType', 'Value': instance_description['InstanceType']})
        ec2_tags.append({'Key':'KeyName', 'Value': instance_description['KeyName']})
        ec2_tags.append({'Key':'VpcId', 'Value': instance_description['VpcId']})
        ec2_tags.append({'Key':'IamInstanceProfile', 'Value': instance_description['IamInstanceProfile']['Arn'].split('/')[-1]})
        ec2_tags.append({'Key':'SubnetId', 'Value': instance_description['SubnetId']})
        ec2_tags.append({'Key':'PrivateIpAddress', 'Value': instance_description['PrivateIpAddress']})
        ec2_tags.append({'Key':'SecurityGroups', 'Value': ', '.join([i['GroupId'] for i in instance_description['SecurityGroups']])})
        try:
            print("Tagging ec2", instance_description['InstanceId'] )
            print("Will add tags: ", ec2_tags)
            client.create_tags(Resources=[instance_description['InstanceId']], Tags=ec2_tags)
        except ClientError as e:
            print('Failed to tag ec2 with error: ', e)

if __name__ == "__main__":
    event = []
    context = []
    lambda_handler(event,context)
