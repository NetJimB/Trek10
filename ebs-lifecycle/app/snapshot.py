###############################################################################################
# Reference: Da-ebs-backup-worker_TESTv1.2.py
# This version adds the Name Tag for identification.
# https://stackoverflow.com/questions/42659418/add-tag-while-creating-ebs-snapshot-using-boto3
#
# Working in Commercial and GovCloud, not region specific
#
import datetime

import boto3

SESSION = boto3.session.Session()


def lambda_handler(_event, _context):
    ec = SESSION.client("ec2")
    reservations = ec.describe_instances(
        Filters=[{"Name": "tag-key", "Values": ["backup", "Backup"]}]
    ).get("Reservations", [])
    instances = [i for r in reservations for i in r["Instances"]]
    print("Found %d instances that need backing up" % len(instances))
    for instance in instances:
        retention_days = find_tag(instance["Tags"], "Retention")

        if retention_days is None:
            retention_days = 16  # Changed retention_days from 30 to 16 20180227 JB

        for dev in instance["BlockDeviceMappings"]:
            if dev.get("Ebs", None) is None:
                continue

            vol_id = dev["Ebs"]["VolumeId"]
            print(
                "Found EBS volume %s on instance %s" % (vol_id, instance["InstanceId"])
            )
            snapshot_name = find_tag(instance["Tags"], "Name")

            if snapshot_name is None:
                snapshot_name = "N/A"

            delete_date = datetime.date.today() + datetime.timedelta(
                days=retention_days
            )
            delete_fmt = delete_date.strftime("%Y-%m-%d")
            desc = f"Created by lambda automated backups. {instance['InstanceId']} - {vol_id}"
            snap = ec.create_snapshot(
                VolumeId=vol_id,
                # Description="Created by lambda automated backups - Da-ebs-backup-worker",
                Description=desc,
                TagSpecifications=[
                    {
                        "ResourceType": "snapshot",
                        "Tags": [
                            {"Key": "Name", "Value": snapshot_name},
                            {"Key": "DeleteOn", "Value": delete_fmt},
                        ],
                    }
                ],
            )
            print(
                "Retaining snapshot %s of volume %s from instance %s for %d days"
                % snap["SnapshotId"],
                vol_id,
                instance["InstanceId"],
                retention_days,
            )
            print("Will delete %s snapshots on %s" % (snap["SnapshotId"], delete_fmt))


def find_tag(tags, name):
    for tag in tags:
        if tag["Key"] == name:
            return tag["Value"]
