import io
from io import StringIO
import os
import boto3
import pandas as pd

def readbucketdata(file):

    if file == 'vaxx':
        filename = 'csv for Vaxx data'

    else:
        filename = 'csv for Full data'
    
    bucketname = 'BUCKET NAME'

    client = boto3.client('s3')

    csv_obj = client.get_object(Bucket=bucketname, Key=filename)
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')

    df = pd.read_csv(StringIO(csv_string), index_col = 0)

    return df
