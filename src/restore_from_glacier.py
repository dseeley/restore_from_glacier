#!/usr/bin/python -u

import threading
import Queue
import sys
import boto3
import argparse


class req(threading.Thread):
    def __init__(self, s3Bucket, s3SummaryObjQueue):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.s3Bucket = s3Bucket
        self.s3SummaryObjQueue = s3SummaryObjQueue

    def run(self):
        while not self.s3SummaryObjQueue.empty():
            s3SummaryObj = self.s3SummaryObjQueue.get()

            s3Obj = self.s3Bucket.Object(s3SummaryObj.key)

            reqResp = ""

            if s3Obj.restore is None:
                reqResp = str(s3Obj.restore_object(RestoreRequest={'Days': 7}))
            elif 'ongoing-request="true"' in s3Obj.restore:
                reqResp = 'Restoration in-progress: ' + s3Obj.key
            elif 'ongoing-request="false"' in s3Obj.restore:
                reqResp = 'Restoration already complete: ' + s3Obj.key

            sys.stdout.write(reqResp + '\n')

            self.s3SummaryObjQueue.task_done()


def main(args):
    s3SummaryObjQueue = Queue.Queue()
    s3Session = boto3.Session(aws_access_key_id=args.aws_access_key_id, aws_secret_access_key=args.aws_secret_access_key)

    s3Bucket = s3Session.resource('s3').Bucket(args.bucket)

    bucketObjs = s3Bucket.objects.all()
    # bucketObjs = s3Bucket.objects.limit(100)      #limit to 100 for testing
    fcnt = 1
    for s3SummaryObj in bucketObjs:
        if s3SummaryObj.storage_class == 'GLACIER':
            s3SummaryObjQueue.put(s3SummaryObj)
            sys.stdout.write("\rGetting item %i     " % fcnt)
            sys.stdout.flush()
            fcnt += 1
    sys.stdout.write("\n")

    # Create each request as a thread
    for t in range(200):
        o = req(s3Bucket, s3SummaryObjQueue)
        o.start()

    s3SummaryObjQueue.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws_access_key_id', required=True)
    parser.add_argument('--aws_secret_access_key', required=True)
    parser.add_argument('--bucket', help='S3 bucket name', required=True)
    args = parser.parse_args()

    main(args)
