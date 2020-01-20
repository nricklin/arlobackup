from arlo import Arlo
import os, datetime, boto3
import requests

def handler(event, context):

	# config values
	USERNAME = os.getenv('USERNAME')
	PASSWORD = os.getenv('PASSWORD')
	S3BUCKET = os.getenv('S3BUCKET')
	prefix = os.getenv('prefix')

	arlo = Arlo(USERNAME, PASSWORD)

	s3 = boto3.client('s3')

	# get basestation, camera pairs
	# camera['parentId'] refers to basestation['deviceId']
	basestations = arlo.GetDevices('basestation')
	cameras = arlo.GetDevices('camera')

	for camera in cameras:
		basestation = [b for b in basestations if b['deviceId'] == camera['parentId']][0]

		url = arlo.TriggerFullFrameSnapshot(basestation, camera)
		print(url)

		content_key = prefix + camera['deviceName'] + '/' + str(datetime.datetime.now()) + '.jpg'
		r = requests.get(url, stream=True)
		r.raw.decode_content = True 

		print('uploading to: s3://'+S3BUCKET+'/'+content_key)
		s3.upload_fileobj(r.raw, S3BUCKET, content_key)

if __name__ == '__main__':
	handler("run from commandline",None)