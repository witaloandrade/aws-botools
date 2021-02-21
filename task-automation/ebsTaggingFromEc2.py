# Witalo Andrade - Jan 2021
# This script will copy tags from ec2 and add them to ebs volumes, tags can be filtered using tags_to_use variable
# How to use this script: run it passing the aws profile name you configured:
# python3 ./ebsTaggingFromEc2.py <aws-profile-name>

import boto3
import json
import sys

# Catch profile name from arg that user will provide
prof=sys.argv[1]

# Pull list of regions from aws
ec2 = boto3.client('ec2')
regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]

# Tag to pull from Ec2
tags_to_use = ['Name','Role','App','Bill','Email','Env','Hostname','LOB','Life','OS','Owner']

# Function to get ec2 tag name
def ec2name(x):
    for t in x:
        if t["Key"] == 'Name':
            instancename = t["Value"]
    return instancename

# Find ec2 that user Owns
def lambda_handler(event, context):
    for each_reg in regions:
        print("Listing Ec2 Instances from the Region: {}".format(each_reg))
        session=boto3.Session(profile_name=prof,region_name=each_reg)
        ec2 = session.resource('ec2')
        instances = ec2.instances.filter(
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
        # Iterate through existing tags and filter only defined 
        for instance in instances:
            tags = instance.tags
            to_tag = [t for t in tags if t['Key'] in tags_to_use]
            to_tag.append({'Key':'EbsAttachedTo', 'Value':instance.id})
            for vol in instance.volumes.all():
                print(f"Tagging volume {vol.id} from instance {instance.id}")
                vol.create_tags(Tags=to_tag)

if __name__ == "__main__":
    event = []
    context = []
    lambda_handler(event,context)
