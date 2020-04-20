# Automated AMI Backups
#
# FILENAME LambdaAmiBackupV3.2.py
#
# @author Based on the work by Robert Kozora <bobby@kozora.me>
#
# https://gist.github.com/bkozora/724e01903a9ad481d21e
#
# This script will search for all instances having a tag with "Backup" or "backup"
# on it. As soon as we have the instances list, we loop through each instance
# and create an AMI of it. Also, it will look for a "Retention" tag key which
# will be used as a retention policy number in days. If there is no tag with
# that name, it will use a 7 days default value for each AMI.
#
# After creating the AMI it creates a "DeleteOn" tag on the AMI indicating when
# it will be deleted using the Retention value and another Lambda function
import collections
import datetime
import pprint

import boto3

SESSION = boto3.session.Session()


def lambda_handler(_event, _context):
    ec2 = SESSION.client("ec2")
    instances = get_instances(ec2)
    print(f"Found {len(instances)} instances that need backing up")

    create_time = datetime.datetime.now()

    to_tag = get_to_tag(ec2, instances, create_time)
    print(to_tag.keys())

    tag_instances(ec2, to_tag, create_time)


def tag_instances(ec2, to_tag, create_time):
    for retention_days, instances in to_tag.items():
        delete_date = datetime.date.today() + datetime.timedelta(
            days=int(retention_days)
        )
        delete_fmt = delete_date.strftime("%m-%d-%Y")
        print("Will delete {} AMIs on {}".format(len(instances), delete_fmt))

        for instance in instances:
            name = f"{instance['name']} - {create_time.strftime('%Y-%m-%d_%a')}"
            ec2.create_tags(
                Resources=[instance["ami_id"]],
                Tags=[
                    {"Key": "DeleteOn", "Value": delete_fmt},
                    {"Key": "Name", "Value": name},
                    {"Key": "SnapshotsTagged", "Value": "false"},
                ],
            )


def get_to_tag(ec2, instances, create_time):
    to_tag = collections.defaultdict(list)
    for instance in instances:
        retention_tag = find_tag(instance["Tags"], "Retention")

        if retention_tag:
            retention_days = int(retention_tag)
        else:
            retention_days = 7

        instance_name = find_tag(instance["Tags"], "Name")

        create_fmt = create_time.strftime("%Y-%m-%d--%H-%M-%S")
        ami_id = ec2.create_image(
            InstanceId=instance["InstanceId"],
            Name="LambdaAmiBackup - " + instance["InstanceId"] + " from " + create_fmt,
            Description="LambdaAmiBackup created AMI of instance "
            + instance["InstanceId"]
            + " from "
            + create_fmt,
            NoReboot=True,
            DryRun=False,
        )
        pprint.pprint(instance)

        to_tag[retention_days].append(
            {"ami_id": ami_id["ImageId"], "name": instance_name}
        )

        print(
            "Retaining AMI {} of instance {} for {} days".format(
                ami_id["ImageId"], instance["InstanceId"], retention_days
            )
        )

    return to_tag


def get_instances(ec2):
    instances = []
    paginator = ec2.get_paginator("describe_instances")
    response_iterator = paginator.paginate(
        Filters=[{"Name": "tag:BackupAmi", "Values": ["True"]}]
    )
    for response in response_iterator:
        for reservations in response["Reservations"]:
            for instance in reservations["Instances"]:
                instances.append(instance)

    return instances


def find_tag(tags, name):
    for tag in tags:
        if tag["Key"] == name:
            return tag["Value"]
