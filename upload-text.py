import boto3
from botocore.exceptions import ClientError
import os
import sys
import threading
import inspect

class ProgressPercentage(object):
    def __init__(self, filename, ):
        self._filename = filename
        seeker = inspect.stack()[1][4][0]
        lastSlash = filename.rfind('/')

        if("upload_file" in seeker):
            try:
                self._size = float(os.path.getsize(filename))
            except FileNotFoundError:
                print("Local File not found.")
                exit()
        elif("download_file" in seeker):
            try:
                self._size = float(boto3.resource('s3').Bucket(filename[:lastSlash]).Object(filename[lastSlash+1:]).content_length)
            except ClientError as e:
                print("Client Error:", e.response['ResponseMetadata']['HTTPStatusCode'], e.response['Error']['Message'])
                exit()
        else:
            print("Invalid stack.")
            exit()

        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            if(bytes_amount!=0):
                #sys.stdout.write("\r%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far, self._size,percentage))
                print("\r%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far, self._size,percentage),end='',flush=True)
            else:
                print()
