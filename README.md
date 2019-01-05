# restore_from_glacier
Restore all S3 objects from Glacier.  Threaded for speed.

Will omit objects that are already temporarily restored, and that have restore in progress. 

## Requirements
+ python 2.7
+ boto3

## Invocation
```
restore_from_glacier.py --aws_access_key_id AWS_ACCESS_KEY_ID
                        --aws_secret_access_key AWS_SECRET_ACCESS_KEY
                        --bucket BUCKET
```
