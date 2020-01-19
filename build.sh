mkdir dist
pip3 install -r requirements.txt -t ./dist
cp save_media.py dist/save_media.py
cp download_scheduler.py dist/download_scheduler.py
cd dist
zip -r ../deploy.zip *
cd ..