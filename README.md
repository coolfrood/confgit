confgit
=======
A tool to backup your config files using git.

Installation
------------

On Ubuntu/Debian, the following packages are needed:
* virtualenv
* libpython-dev
* libyaml-dev
* git

Create a new virtualenv:
```
virtualenv venv
```

Activate virtualenv:
```
source venv/bin/activate
```

Install needed Python packages
```
pip install -r requirements.txt
```

How it works
------------
`confgit` using git to manage configuration files.
Files are kept in a flat hierarchy.  Metadata for
added files is maintained as a YAML file `.files.yaml`.
This metadata includes the original path of the file.

Using
-----

* Set up an empty git repo:
```
mkdir ~/config.repo
cd ~/config.repo
git init .
touch .files.yaml
git add .files.yaml
git remote add origin <remote URL>
git push -u origin master
```

* Create a configuration file:
```
mkdir ~/.confgit
cp config.yaml.example ~/.confgit/config.yaml
```
Edit as needed.

* Add a config file to track (example):
```
confgit add /etc/hosts
confgit push
```

* Update a config file (example):
```
confgit update /etc/hosts
confgit push
```

TODO
----
* Support for encrypted files
* Support for directories
* `confgit restore`
