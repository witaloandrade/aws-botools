#!/usr/bin/python3

import re
import boto3
import logging

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logger = logging.getLogger()

aws_regions = ['us-east-1','us-west-2','ap-southeast-1','ap-southeast-2','eu-central-1','eu-west-1']
aws_accounts = ['<profile-name>']

def listEc2(ec2_client):
    logger.info('Starting boto3 session for  %s - %s', acc,region)
    
    #print(ec2_client.meta.region_name)
    #ec2_response = ec2_client.describe_instances()
    #ec2_list = sum([[i for i in r.get('Instances', [])] for r in ec2_response.get('Reservations', [])], [])
    #print(type(ec2_list))
    #for ecc in ec2_list:
    #    print(ecc['InstanceId'])

def main():
    for acc in aws_accounts:
        for region in aws_regions:
            logger.info('Starting boto3 session for  %s - %s', acc,region)
            try:
                session=boto3.Session(profile_name=acc,region_name=region)
                ec2  = session.client('ec2')
            except Exception as e:
                logger.error('Failed to start boto3 session for  %s, - %s', acc,region)
            listEc2(ec2)

if __name__ == '__main__':
    main()