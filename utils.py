import boto3
import os
import requests
from settings import DEFAULT_REGION, KEYNAME

session = boto3.session.Session(region_name=DEFAULT_REGION, profile_name=KEYNAME)

def get_public_ip(instance_ids):
    ec2_client = session.client("ec2")
    reservations = ec2_client.describe_instances(InstanceIds=instance_ids).get(
        "Reservations"
    )

    for reservation in reservations:
        for instance in reservation["Instances"]:
            return instance.get("PublicIpAddress")


def get_running_instances():
    ec2_client = session.client("ec2")
    reservations = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"],}]
    ).get("Reservations")

    instances = []
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            public_ip = instance["PublicIpAddress"]
            private_ip = instance["PrivateIpAddress"]
            instances.append(
                f"{instance_id}, {instance_type}, {public_ip}, {private_ip}"
            )

    return instances


def get_instance_status(instance_id):
    ec2_client = session.client("ec2")
    if instance_id:
        reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")
    else:
        reservations = ec2_client.describe_instances().get("Reservations")

    instances_status = []
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            instance_status = instance["State"]['Name']
            public_dns_name = instance["PublicDnsName"]
            link_details = "Server is spinning up"
            if instance_status =="running":
                link_details = "Server is up and docker is spinning up right now"
                try:
                    response = requests.get(f'http://{public_dns_name}')
                    if response.status_code == 200:
                        link_details = f'The site is up and running. please visit http://{public_dns_name}'
                except:
                    link_details = "Server is up and docker is spinning up right now"
            elif instance_status == "terminated":
                link_details = "Server is terminated"
            elif instance_status == "shutting-down":
                link_details = "Server is shutting down"
            else:
                link_details = ""
            
            instances_status.append(
                f"{instance_id}, {instance_type}, {instance_status}, {link_details}"
            )

    return instances_status


def stop_instance(instance_id):
    ec2_client = session.client("ec2")
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    return response


def terminate_instance(instance_id):
    ec2_client = session.client("ec2")
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    return response


def create_key_pair():
    ec2_client = session.client("ec2")
    key_pair = ec2_client.create_key_pair(KeyName=KEYNAME)

    private_key = key_pair["KeyMaterial"]

    # write private key to file with 400 permissions
    with os.fdopen(os.open("/tmp/aws_ec2_key.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(private_key)
