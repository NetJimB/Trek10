#############################################################################################################
# A lambda function that will copy EC2 tags to all related Volumes and Network Interfaces.
# A full writeup can be found on the site http://mlapida.com/thoughts/tagging-and-snapshotting-with-lambda
#
# EC2-Tag-Assets-LambdaV1.1.py
# last update 20170927jb
from __future__ import print_function

import logging

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.ERROR)
SESSION = boto3.session.Session(region_name="us-gov-west-1")
DEBUG_MODE = False


def lambda_handler(_event, _context):
    ec2 = SESSION.resource("ec2")
    # List all EC2 instances
    base = ec2.instances.all()
    # loop through by running instances
    for instance in base:
        # Tag the Volumes
        for vol in instance.volumes.all():
            # print(vol.attachments[0]['Device'])
            if DEBUG_MODE:
                print("[DEBUG] " + str(vol))
                tag_cleanup(instance, vol.attachments[0]["Device"])
            else:
                tag = vol.create_tags(
                    Tags=tag_cleanup(instance, vol.attachments[0]["Device"])
                )
                print("[INFO]: " + str(tag))
        # Tag the Network Interfaces
        for eni in instance.network_interfaces:
            # print(eni.attachment['DeviceIndex'])
            if DEBUG_MODE:
                print("[DEBUG] " + str(eni))
                tag_cleanup(instance, "eth" + str(eni.attachment["DeviceIndex"]))
            else:
                tag = eni.create_tags(
                    Tags=tag_cleanup(
                        instance, "eth" + str(eni.attachment["DeviceIndex"])
                    )
                )
                print("[INFO]: " + str(tag))


# ------------- Functions ------------------
# returns the type of configuration that was performed
def tag_cleanup(instance, detail):
    tempTags = []
    v = {}
    for t in instance.tags:
        # pull the name tag
        if t["Key"] == "Name":
            v["Value"] = t["Value"] + " - " + str(detail)
            v["Key"] = "Name"
            tempTags.append(v)
        # Set the important tags that should be written here
        elif t["Key"] == "User":
            print("[INFO]: User Tag " + str(t))
            tempTags.append(t)
        elif t["Key"] == "Environment":
            print("[INFO]: Environment Tag " + str(t))
            tempTags.append(t)
        elif t["Key"] == "Deleton":
            print("[INFO]: Deleteon Tag " + str(t))
            tempTags.append(t)
        elif t["Key"] == "Purpose":
            print("[INFO]: Purpose Tag " + str(t))
            tempTags.append(t)
        elif t["Key"] == "Availability Zone":
            print("[INFO]: Availability Zone Tag " + str(t))
            tempTags.append(t)
        elif t["Key"] == "BackupDate":
            print("[INFO]: BackupDate " + str(t))
            tempTags.append(t)
        else:
            print("[INFO]: Skip Tag - " + str(t))
    print("[INFO] " + str(tempTags))

    return tempTags
