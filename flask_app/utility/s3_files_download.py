import os

import boto
from boto.exception import S3ResponseError
from boto.s3.connection import OrdinaryCallingFormat


def download_s3_bucket_contents(path):
    AWS_ACCESS_KEY_ID = 'AKIAIR3MZNYSTJA5H2XA'
    AWS_SECRET_ACCESS_KEY = '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'
    S3_BUCKET = 'politic-ai-ml-data'
    s3_conn = boto.s3.connect_to_region('eu-central-1',
                                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        calling_format=OrdinaryCallingFormat())

    bucket = s3_conn.get_bucket(S3_BUCKET)

    bucket_list = bucket.list()

    for l in bucket_list:
        key_string = str(l.key)
        s3_path = path + key_string
        # create directory if it doesn't exist
        if not os.path.exists(os.path.dirname(s3_path)):
            try:
                os.makedirs(os.path.dirname(s3_path))
            except OSError as exc:
                # let guard againts race conditions
                import errno

                if exc.errno != errno.EEXIST:
                    raise

        try:
            print("Current File is ", s3_path)
            l.get_contents_to_filename(s3_path)
        except (OSError, S3ResponseError) as e:
            print("Error for file ", s3_path)
            pass
