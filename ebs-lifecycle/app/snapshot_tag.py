import boto3

SESSION = boto3.session.Session()


def lambda_handler(_event, _context):
    ec2 = SESSION.client("ec2")
    images = get_images(ec2)
    [process(ec2, image) for image in images]


def process(ec2, image):
    tags = [tag for tag in image["Tags"] if tag["Key"] != "SnapshotsTagged"]
    snapshot_ids = get_snapshot_ids(image)
    ec2.create_tags(Resources=snapshot_ids, Tags=tags)
    remove_tag(ec2, image)


def remove_tag(ec2, image):
    ec2.delete_tags(
        Resources=[image["ImageId"]], Tags=[{"Key": "SnapshotsTagged"}],
    )


def get_snapshot_ids(image):
    snapshot_ids = []

    for mapping in image["BlockDeviceMappings"]:
        snapshot_id = mapping.get("Ebs", {}).get("SnapshotId")
        if snapshot_id is not None:
            snapshot_ids.append(snapshot_id)

    return snapshot_ids


def get_images(ec2):
    return ec2.describe_images(
        Filters=[{"Name": "tag:SnapshotsTagged", "Values": ["false"]}]
    )["Images"]
