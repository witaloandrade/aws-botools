#!/usr/bin/python3

"""
Witalo Andrade - 2021-07-15
This script will copy old BillingId/Owner tag values to new values.
How run it: python3 ./<NAME>.py
"""

import os
import boto3
from time import sleep
from botocore.exceptions import ClientError
import logging
import re

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.ERROR)
logger = logging.getLogger()

#Static most used regions
aws_regions = ["us-east-1","us-west-2","ap-southeast-1","ap-southeast-2","eu-central-1","eu-west-1"]

def pullAwsCreds(file='~/.aws/credentials'):
    """
    This function will return a list with all aws profiles from user default aws cred file.
    """
    path = file
    full_path = os.path.expanduser(path)
    with open(full_path, 'r') as f:
        lines = f.readlines() 
        f.close()
    return [line[1:-2] for line in lines if line.startswith('[') ]


def addTags(aws_accounts):
    """
    This function will iterate through ec2 instances and update the tags from regexLowerCaseTags return.
    """
    for account in aws_accounts:
        print('Working on aws credential :', account)
        for each_reg in aws_regions:
            session=boto3.Session(profile_name=account,region_name=each_reg)
            client  = session.client('ec2')
            response = client.describe_instances(
            Filters=[ # add any filters if needed, used for dev
                #{
                #    'Name': 'tag:Name',
                #    'Values': ['xyz']
                #}
            ]
            )
            for reservation in response['Reservations']:
                for instance_description in reservation['Instances']:
                    print('Listing :', instance_description['InstanceId'])
                    sleep(2)
                    to_tag = regexLowerCaseTags(instance_description['Tags'])
                    if to_tag:
                        logger.info('Func returned new tags: %s for %s ', to_tag, instance_description['InstanceId'] )
                        try:
                            print("Tagging ec2 {} - {}".format(instance_description['InstanceId'], to_tag, end='\n\n'))
                            client.create_tags(Resources=[instance_description['InstanceId']], DryRun=False, Tags=to_tag)
                        except ClientError as e:
                            if e.response['Error'].get('Code') == 'DryRunOperation':
                                print("DryRun executed, ec2 would have been tagged.",end='\n\n')
                            else:
                                logger.error('Failed to tag ec2 with error : %s', account,end='\n\n')
                        except Exception as e:
                            print(e)

def lowerCaseTags(tags):
    new_tags = []
    for t in tags:
        if t['Key'] == 'BillingId':
            new_tags.append({'Key':'billingid', 'Value': t['Value']})
        elif t['Key'] == 'Owner':
            new_tags.append({'Key':'owner', 'Value': t['Value']})
    if len(new_tags) > 0:
        return new_tags

def regexLowerCaseTags(tags):
    """
    This function will return the new tag values from the existing tags.
    I will try to regex filter best and not valid values. 
    """
    new_tags = []
    billKeyRegex = re.compile(r'bill', re.IGNORECASE)
    billValueRegex = re.compile(r'\D+-\d+', re.IGNORECASE)
    ownerRegex = re.compile(r'owner', re.IGNORECASE)
    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    for t in tags:
        if bool(billKeyRegex.search(t['Key'])) == True and bool(billValueRegex.search(t['Value'])) == True:
            print('Found {}'.format(t))
            b = {'Key':'billingid', 'Value': t['Value']}
        elif bool(ownerRegex.search(t['Key'])) == True and bool(emailRegex.search(t['Value'])) == True:
            print('Found {}'.format(t))
            o = {'Key':'owner', 'Value': emailRegex.search(t['Value']).group()}
    try:
        new_tags.append(b)
    except Exception as e:
        logger.info('Billing not found')
    try:
        new_tags.append(o)
    except Exception as e:
        logger.info('Owner not found')
    #print('Result is :', new_tags)
    if len(new_tags) > 0:
        return new_tags

def main():
    addTags(pullAwsCreds())

if __name__ == '__main__':
    main()