# Reference: ebs-snapshot-expiration-worker-GovCloudV1.1.py
# https://serverlesscode.com/post/lambda-schedule-ebs-snapshot-backups-2/
## GovCloud
import datetime

import boto3

SESSION = boto3.session.SESSION()
ACCOUNT_IDS = ["061529257154"]

"""
This function looks at *all* snapshots that have a "DeleteOn" tag containing
the current day formatted as YYYY-MM-DD. This function should be run at least
daily.
"""
def lambda_handler(_event, _context):
    ec2 = SESSION.client("ec2")

    delete_on = datetime.date.today().strftime("%Y-%m-%d")
    filters = [
        {"Name": "tag-key", "Values": ["DeleteOn"]},
        {"Name": "tag-value", "Values": [delete_on]},
    ]
    snapshot_response = ec2.describe_snapshots(OwnerIds=ACCOUNT_IDS, Filters=filters)
    for snap in snapshot_response["Snapshots"]:
        print("Deleting snapshot %s" % snap["SnapshotId"])
        ec2.delete_snapshot(SnapshotId=snap["SnapshotId"])
