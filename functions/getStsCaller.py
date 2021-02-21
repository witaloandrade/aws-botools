# Witalo Andrade - Dez 2020
# This Function will get the user using boto3

import boto3

def GetUser():
    sts = boto3.client('sts')
    #response = sts.get_caller_identity()
    #return (response.get('UserId').split(':')[-1])
    return (sts.get_caller_identity().get('UserId').split(':')[-1])

