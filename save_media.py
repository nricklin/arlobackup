import json, boto3
import requests
s3 = boto3.client('s3')

def handler(event, context):

    print event
    print context

    message = json.loads( event['Records'][0]['body'] )
    bucket = message['metadata']['s3bucket']
    contentURL = message['media']['presignedContentUrl']
    content_key = message['metadata']['content_key']
    thumbURL = message['media']['presignedThumbnailUrl']
    thumb_key = message['metadata']['thumbnail_key']

    # get media itself
    r = requests.get(contentURL, stream=True)
    r.raw.decode_content = True 
    s3.upload_fileobj(r.raw, bucket, content_key)

    # get thumbnail
    r = requests.get(thumbURL, stream=True)
    r.raw.decode_content = True 
    s3.upload_fileobj(r.raw, bucket, thumb_key)


    