
# Install python (default python3) in ubuntu 20.04

https://towardsdatascience.com/virtual-environments-104c62d48c54

	sudo apt update
	sudo apt -y install python3
	python3 -V
	sudo apt install -y python3-pip
	pip3 install package_name
	sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

## python venv

There have several python virtual env, please stick on the python3 build-in module 'venv'.

	sudo apt install -y python3-venv

	### create/enter a virtual env
	python3 -m venv my-test-proj-env
	source venv/bin/activate

	### save the env to git repo
	(venv) % pip freeze > requirements.txt
	(venv) % deactivate

	### after new git clone, create a new env, then restore it from the `requirements.txt`
	pip install -r requirements.txt

### venv usage

	mkdir test-proj
	cd test-proj
	python3 -m venv my-test-proj-env
	source venv/bin/activate
	(venv) % tree
		test-project/venv/               # Our environment's root directory
		├── bin
		│   ├── activate                           # Scripts to activate
		│   ├── activate.csh                       # our project's
		│   ├── activate.fish                      # virtual environment.
		│   ├── easy_install
		│   ├── easy_install-3.7
		│   ├── pip
		│   ├── pip3
		│   ├── pip3.7
		│   ├── python -> /usr/local/bin/python    # Symlinks to system-wide
		│   └── python3 -> python3.7               # Python instances.
		├── include
		├── lib
		│   └── python3.7
		│       └── site-packages              # Stores local site packages
		└── pyvenv.cfg

	### By default, only pip and setuptools are installed inside a new environment.
	(venv) % pip list                    # Inside an active environment
		Package    Version
		---------- -------
		pip        19.1.1
		setuptools 40.8.0

	(venv) % pip install numpy==1.15.3
	(venv) % pip list

	...

	(venv) % pip freeze > requirements.txt
	(venv) % deactivate


### Troubleshooting

	cd test-proj
	rm -r venv/
	python3 -m venv venv
	pip install -r requirements.txt


### How Virtual Environments Do Their Thing

	% echo $PATH
		/usr/local/bin:/usr/bin:/usr/sbin:/bin:/sbin

	% which python3
		/usr/local/bin/python3
	% python3                           # Activates a Python shell
		>>> import site
		>>> site.getsitepackages()          # Points to site-packages folder
		['/usr/local/Cellar/python/3.7.3/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages']


	% cd ~/test-project/
	% source venv/bin/activate
	(venv) % echo $PATH
		~/test-project/venv/bin:/usr/local/bin:/usr/bin:/usr/sbin:/bin:/sbin
	(venv) % which python3
		~/test-project/venv/bin/python3
	(venv) % python3
		>>> import site
		>>> site.getsitepackages()
		['~/test-project/venv/lib/python3.7/site-packages']

