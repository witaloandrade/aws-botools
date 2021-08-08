# Credit to the original: https://gist.github.com/brandond/6b4d22eaefbd66895f230f68f27ee586

"""
Witalo Andrade
This script will copy tags to snapshots from AMIS
How run it: python3 ./<NAME>.py
"""

import copy
import logging
import os, sys
import boto3

prof=sys.argv[1]

logging.basicConfig(level=os.environ.get('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

#Static most used regions
aws_regions = ["us-east-1","us-west-2","ap-southeast-1","ap-southeast-2","eu-central-1","eu-west-1"]
tags_to_use = ['Name','approle','AppRole','app_id','Application','BillingId','Email','Environment','Hostname','LOB','Lifespan','OSType','ostype','Owner','billingid','owner','BillingId','Owner']


def tag_everything():
    for each_reg in aws_regions:
        print('Working on aws credential :', each_reg)
        session=boto3.Session(profile_name=prof,region_name=each_reg)
        ec2 = session.client('ec2')
        snapshots = {}
        for response in ec2.get_paginator('describe_snapshots').paginate(OwnerIds=['self']):
            snapshots.update([(snapshot['SnapshotId'], snapshot) for snapshot in response['Snapshots']])

        for image in ec2.describe_images(ImageIds=[],Owners=['self'])['Images']:
            tags = boto3_tag_list_to_ansible_dict(image.get('Tags', []))
            #print('Working on Image {}'.format(image['ImageId']))
            for device in image['BlockDeviceMappings']:
                #print(device)
                if 'Ebs' in device: # skip ephemeral
                    if 'SnapshotId' in device['Ebs']:
                        snapshot = snapshots[device['Ebs']['SnapshotId']]
                        snapshot['Used'] = True
                        cur_tags = boto3_tag_list_to_ansible_dict(snapshot.get('Tags', []))
                        new_tags = copy.deepcopy(cur_tags)
                        new_tags.update(tags)
                        new_tags['ImageId'] = image['ImageId']
                        new_tags['Parent'] = image['ImageId']
                        #new_tags['Name'] += ' ' + device['DeviceName'] #to do add get name or return none, don't want the name changed
                        if new_tags != cur_tags:
                            try:
                                logger.info('{0}: Tags changed to {1}'.format(snapshot['SnapshotId'], new_tags))
                                ec2.create_tags(Resources=[snapshot['SnapshotId']], Tags=ansible_dict_to_boto3_tag_list(new_tags))
                            except Exception as e:
                                print(e)

        for snapshot in snapshots.values():
            if 'Used' not in snapshot:
                cur_tags = boto3_tag_list_to_ansible_dict(snapshot.get('Tags', []))
                name = cur_tags.get('Name', snapshot['SnapshotId'])
                if not name.startswith('ORPHAN'):
                    logger.warning('{0} Unused!'.format(snapshot['SnapshotId']))
                    cur_tags['Name'] = 'ORPHAN-' + name
                    cur_tags['Parent'] = 'ORPHAN'
                    try:
                        ec2.create_tags(Resources=[snapshot['SnapshotId']], Tags=ansible_dict_to_boto3_tag_list(cur_tags))
                    except Exception as e:
                        print(e)

        volumes = {}
        for response in ec2.get_paginator('describe_volumes').paginate():
            volumes.update([(volume['VolumeId'], volume) for volume in response['Volumes']])

        for response in ec2.get_paginator('describe_instances').paginate():
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    tags = boto3_tag_list_to_ansible_dict(instance.get('Tags', []))
                    for device in instance['BlockDeviceMappings']:
                        volume = volumes[device['Ebs']['VolumeId']]
                        volume['Used'] = True
                        cur_tags = boto3_tag_list_to_ansible_dict(volume.get('Tags', []))
                        new_tags = copy.deepcopy(cur_tags)
                        new_tags.update(tags)
                        #new_tags['Name'] += ' ' + device['DeviceName'] #to do add get name or return none, don't want the name changed
                        if new_tags != cur_tags:
                            logger.info('{0} Tags changed to {1}'.format(volume['VolumeId'], new_tags))
                            try:
                                ec2.create_tags(Resources=[volume['VolumeId']], Tags=ansible_dict_to_boto3_tag_list(new_tags))
                            except Exception as e:
                                print(e)

        for volume in volumes.values():
            if 'Used' not in volume:
                cur_tags = boto3_tag_list_to_ansible_dict(volume.get('Tags', []))
                name = cur_tags.get('Name', volume['VolumeId'])
                if not name.startswith('ORPHAN'):
                    logger.warning('{0} Unused!'.format(volume['VolumeId']))
                    cur_tags['Name'] = 'ORPHAN- ' + name
                    try:
                        ec2.create_tags(Resources=[volume['VolumeId']], Tags=ansible_dict_to_boto3_tag_list(cur_tags))
                    except Exception as e:
                        print(e)

def boto3_tag_list_to_ansible_dict(tags_list):
    #return {tag["Key"]: tag["Value"] for tag in tags_list if not tag["Key"].startswith("aws:")}
    return {tag["Key"]: tag["Value"] for tag in tags_list if tag['Key'] in tags_to_use}


def ansible_dict_to_boto3_tag_list(tags_dict):
    return [{"Key": k, "Value": v} for k, v in tags_dict.items() if not k.startswith("aws:")]

if __name__ == '__main__':
    tag_everything()