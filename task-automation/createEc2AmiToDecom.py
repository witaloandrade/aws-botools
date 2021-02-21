# Witalo Andrade - Jan 2021
# This script will take an AMI and copy the tags from the ec2 instance.
# How to use this script: run it passing the aws profile name you configured:
# python3 ./createAmi.py <aws-profile-name>

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
    session=boto3.Session(profile_name=prof,region_name=each_reg)
    client  = session.client('ec2')
    resource = session.resource('ec2')
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
        instance_id = instance_description['InstanceId']
        ec2_tags = instance_description['Tags']
        ec2_tags.append({'Key':'InstanceType', 'Value': instance_description['InstanceType']})
        ec2_tags.append({'Key':'KeyName', 'Value': instance_description['KeyName']})
        ec2_tags.append({'Key':'VpcId', 'Value': instance_description['VpcId']})
        ec2_tags.append({'Key':'IamInstanceProfile', 'Value': instance_description['IamInstanceProfile']['Arn'].split('/')[-1]})
        ec2_tags.append({'Key':'SubnetId', 'Value': instance_description['SubnetId']})
        ec2_tags.append({'Key':'PrivateIpAddress', 'Value': instance_description['PrivateIpAddress']})
        ec2_tags.append({'Key':'SecurityGroups', 'Value': ', '.join([i['GroupId'] for i in instance_description['SecurityGroups']])})
        ec2_tags.append({'Key':'Ec2Id', 'Value': instance_id})
        ec2_tags.append({'Key':'Decommissioned', 'Value': datetime.utcnow().strftime('%Y-%m-%d')})
        ec2_tags.append({'Key':'DeleteAfter', 'Value': (datetime.utcnow() + timedelta(days=90)).strftime('%Y-%m-%d')})
        ec2_tags.append({'Key':'Name', 'Value': ec2name(ec2_tags)})
        to_tag = [t for t in ec2_tags if t['Key'] if not t['Key'].startswith('aws:')]
        image_name = f"{ec2name(ec2_tags)}-Decommissioned-{datetime.utcnow().strftime('%Y-%m-%d')}"
        print(to_tag)
        try:
            print("Creating ami for:", ec2name(ec2_tags),"- ", end='')
            print("AMI Name is: ", image_name)
            new_ami = client.create_image(InstanceId=instance_id, DryRun=False, Description='Decommission Process', Name=image_name)
            try:
                print("Waiting for ami creation!")
                ami_waiter = client.get_waiter('image_available')
                ami_waiter.wait(Owners=['self'],ImageIds=[new_ami['ImageId']])
                try:
                    print("Tagging image", new_ami['ImageId'] )
                    client.create_tags(Resources=[new_ami['ImageId']], Tags=to_tag)
                except ClientError as e:
                    print('Failed to tag AMI with error: ', e)
            except ClientError as e:
                print('Failed to create AMI with error: ', e)
            print("Image Successfully created", end='')
            response = client.describe_images(Owners=['self'],ImageIds=[new_ami['ImageId']])
            print(response['Images'][0]['ImageId'], response['Images'][0]['State'], response['Images'][0]['CreationDate'])
        except ClientError as e:
            if e.response['Error'].get('Code') == 'DryRunOperation':
                print("DryRun Operation Would have succeeded")
            else:
              print(e)
     
def ec2name(x):
  for t in x:
      if t["Key"] == 'Name':
          instancename = t["Value"]
  return instancename

if __name__ == "__main__":
    event = []
    context = []
    lambda_handler(event,context)

