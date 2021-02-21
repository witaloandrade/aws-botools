# Witalo Andrade - Jan 2021
# This function will check if an ec2 is behind an elb.

import json
import boto3


def findelbsv2(InstanceId):
    d = []
    client = boto3.client('elbv2')
    response = client.describe_target_groups()
    for i in range(0,len(response['TargetGroups'])):
        tg = client.describe_target_health(TargetGroupArn=response['TargetGroups'][i]['TargetGroupArn'])
        for j in range(0,len(tg['TargetHealthDescriptions'])):
            if InstanceId == tg['TargetHealthDescriptions'][j]['Target']['Id']:
                d.append(response['TargetGroups'][i]['TargetGroupName'])      
    return ', '.join(map(str, d)) 

#def lambda_handler(event, context):
#    templist = []
#    client = boto3.client('elbv2')
#    response = client.describe_target_groups()
#    for i in range(0,len(response['TargetGroups'])):
#        tg = client.describe_target_health(TargetGroupArn=response['TargetGroups'][i]['TargetGroupArn'])
#        for j in range(0,len(tg['TargetHealthDescriptions'])):
#            if event['ec2id'] == tg['TargetHealthDescriptions'][j]['Target']['Id']:
#                templist.append(response['TargetGroups'][i]['TargetGroupName'])      
#    return ', '.join(map(str, templist)) 
#
#if __name__ == "__main__":
#    event = {"ec2id": 'i-0f65377ada44d16a7' }
#    context = []
#    print(lambda_handler(event,context))

