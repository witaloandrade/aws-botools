# Witalo Andrade - Dez 2020
# This function will iterate sgs and return te names as an str

instance_description =  {}
instance_description['SecurityGroups'] = [{'GroupName': 'abc', 'GroupId': 'sg-12345'}, {'GroupName': 'xyz', 'GroupId': 'sg-6789'}]

#print(instance_description['SecurityGroups'][0]['GroupId'])
#for sg in instance_description['SecurityGroups']:
#    print(sg['GroupId'])
#sg_id = [i['GroupId'] for i in instance_description['SecurityGroups']]
#print(str(sg_id).strip('[]'))

#sg_id = str([i['GroupId'] for i in instance_description['SecurityGroups']]).strip('[]')
#print(sg_id)

print(', '.join([i['GroupId'] for i in instance_description['SecurityGroups']]))
