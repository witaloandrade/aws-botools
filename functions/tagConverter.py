# Witalo Andrade - Dez 2020
# This functions will convert aws tags to dic and list

def _format_dict(tags):
    output = []
    for (key, value) in tags.items():
        output.append("%s:%s" % (key, value))

    return ", ".join(output)

def _dict_to_aws_tags(tags):
    return [{'Key': key, 'Value': value} for (key, value) in tags.items() if not key.startswith('aws:')]

def _aws_tags_to_dict(aws_tags):
    return {x['Key']: x['Value'] for x in aws_tags if not x['Key'].startswith('aws:')}