#!/usr/bin/python3

"""
Witalo Andrade - 2021-07-16
This script will count number of s3 buckets per account
"""

import os
import boto3
from time import sleep
from botocore.exceptions import ClientError

import logging
logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.ERROR)
logger = logging.getLogger()


#Static Most Used Regions
aws_regions = ["us-east-1","us-west-2","ap-southeast-1","ap-southeast-2","eu-central-1","eu-west-1"]

def pullAwsCreds(file='~/.aws/credentials'):
    """
    This function will return a list with all aws profiles
    from user default aws cred file
    """
    path = file
    full_path = os.path.expanduser(path)
    with open(full_path, 'r') as f:
        lines = f.readlines() 
        f.close()
    return [line[1:-2] for line in lines if line.startswith('[') ]


def countBuckets(aws_accounts):
    """
    This function will iterate through accounts from user
    aws credentials and will count de buckets 
    """
    for account in aws_accounts:
        buckets = []
        logger.info('Working on account : %s', account)
        session=boto3.Session(profile_name=account)
        sts = session.client('sts')
        logger.info('Account Number is : %s', sts.get_caller_identity()['Account'])
        s3 = session.client('s3')
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        print("Account {} has {} buckets".format(account, len(buckets)), end='\n\n')
