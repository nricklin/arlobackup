
init:
	virtualenv venv ;\
	source ./venv/bin/activate ;\
	pip install -U pip ;\
	pip install -r requirements.txt ;\

clean:
	rm -rf *.pyc
	rm -rf dist
	rm -rf build
	rm -rf __pycache__
	rm -rf arlo.egg-info
	rm -rf venv

# build should be done on an ec2 machine 
build: 
	rm deploy.zip ;\
	rm -rf dist ;\
	./build.sh