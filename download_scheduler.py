# 1. Get all media available since the last time we grabbed media.
# 2. Dump each media item onto an SQS queue for async download 

# Schema for SQS messages: {"content": content_object, "metadata": metadata_object}
# the metadata_object looks like this:
# {
# 	"s3bucket": "<s3 bucket>",
# 	"content_key": "/path/to/where/content/should/be/stored",
# 	"thumbnail_key": "/path/to/where/thumbnail/should/be/stored"
# }

# save media to s3://s3bucket/prefix/media/<camera_name>_<mediafilename>.<ext>
# save thumbnail to s3://s3bucket/prefix/media/<camera_name>_<mediafilename>_thumbnail.<ext>



from arlo import Arlo
from datetime import timedelta, date
import json, os, datetime, boto3
from py_s3_cache import Cache



def handler(event, context):

	# config values
	USERNAME = os.getenv('USERNAME')
	PASSWORD = os.getenv('PASSWORD')
	QUEUENAME = os.getenv('QUEUENAME')
	S3BUCKET = os.getenv('S3BUCKET')
	prefix = os.getenv('prefix')
	cacheprefix = prefix + 'cache/'

	cache = Cache(S3BUCKET,cacheprefix)


	sqs = boto3.client('sqs')



	print(event)
	print(context)
	print(USERNAME)
	print(PASSWORD)
	print(QUEUENAME)
	print(S3BUCKET)
	print(prefix)
	print(cache)


	# get list of recent arlo media objects from past 7 days
	arlo = Arlo(USERNAME, PASSWORD)
	today = (date.today()-timedelta(days=0)).strftime("%Y%m%d")
	seven_days_ago = (date.today()-timedelta(days=7)).strftime("%Y%m%d")
	library = arlo.GetLibrary(seven_days_ago, today)

	# only process library items that have arrived since our last processing time
	latest_saved_media_timestamp = cache.get('latest_saved_media_timestamp')
	library = [l for l in library if l['lastModified'] > latest_saved_media_timestamp]

	if len(library) > 0:
		latest_saved_media_timestamp = max([l['lastModified'] for l in library])

	cameras = arlo.GetDevices('camera')
	camera_id2name = {}
	for c in cameras:
		camera_id2name[c['deviceId']] = c['deviceName']

	for media in library:
		camera_name = camera_id2name.get(media['deviceId'],'unknown_device')
		filename = camera_name + '_' + datetime.datetime.fromtimestamp(int(media['name'])//1000).strftime('%Y-%m-%d %H-%M-%S')
		message = {
			"media": media,
			"metadata": {
				"s3bucket": S3BUCKET,
				"content_key": prefix + 'media/' + filename + '.mp4',
				"thumbnail_key": prefix + 'media/' + filename + '_thumbnail.jpg'
			}
		} 
		print(message)

		response = sqs.send_message(
			QueueUrl=QUEUENAME,
			MessageBody=json.dumps(message)
		)


	cache.set('latest_saved_media_timestamp', latest_saved_media_timestamp, 3600*24*30)

if __name__ == "__main__":
	handler("Running from command line",None)

