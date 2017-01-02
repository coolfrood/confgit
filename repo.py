import datetime
from git import Repo
import os
import shutil
import sys
import yaml

class File:
    def __init__(self, original_name, mode, uid, gid, backup_name):
        self.original_name = original_name
        self.mode = mode
        self.uid = uid
        self.gid = gid
        self.backup_name = backup_name

    def update(self, root):
        shutil.copy2(self.original_name, self.backup_name)
        repo = Repo(root)
        repo.index.add([self.backup_name])
        repo.index.commit("Updated {}".format(self.original_name))

    def __repr__(self):
        return "{{ 'original_name': '{}', 'backup_name': '{}' }}".format(self.original_name, self.backup_name)

    @staticmethod
    def to_dict(o):
        return { 
            'original_name': o.original_name,
            'backup_name': o.backup_name,
            'mode': o.mode,
            'uid': o.uid,
            'gid': o.gid
        }

    @classmethod
    def from_dict(cls, d):
        return File(
            d['original_name'],
            d['backup_name'],
            d['mode'],
            d['uid'],
            d['gid']
        )

    @classmethod
    def create(cls, root, original_name):
        try:
            st = os.stat(original_name)
            basename = os.path.basename(original_name)
            backup_name = '{}/{}'.format(root, basename)
            ctr = 0
            while os.path.exists(backup_name):
                backup_name = '{}/{}-{}'.format(root, basename, ctr)
                ctr += 1
            shutil.copy2(original_name, backup_name)

            repo = Repo(root)
            repo.index.add([backup_name])
            repo.index.commit("Added {}".format(backup_name))
            return cls(original_name, st.st_mode, st.st_uid, st.st_gid, backup_name)
        except Exception as e:
            sys.exit("Could not find or access file: {} {}".format(original_name, e))

class Repository:
    def __init__(self, root):
        self.root = root
        self.config_file = "{}/.files.yaml".format(root)
        self._load_config()

    def _load_config(self):
        self.origname_to_file = {}
        if os.path.isfile(self.config_file):
            config = yaml.load(file(self.config_file))
            for f in config['files']:
                the_file = File.from_dict(f)
                self.origname_to_file[the_file.original_name] = the_file

    def _save_config(self):
        files = sorted(self.origname_to_file.values(), key=lambda f: f.original_name)
        yaml.dump({ 'files': map(File.to_dict, files) },
            file(self.config_file, 'w'),
            default_flow_style=False)
        repo = Repo(self.root)
        repo.index.add([self.config_file])
        repo.index.commit('Updated index')
    
    def add(self, filename):
        filename = os.path.normpath(filename)
        if not filename.startswith('/'):
            sys.exit('Must provide absolute path')
        if filename in self.origname_to_file:
            sys.exit('{} already added, use `update` to update existing file'.format(filename))
        f = File.create(self.root, filename)
        self.origname_to_file[filename] = f
        self._save_config()

    def list(self):
        for v in self.origname_to_file.keys():
            print v

    def update(self, filename):
        filename = os.path.normpath(filename)
        if not filename in self.origname_to_file:
            sys.exit('{} is not being tracked, use `add`'.format(filename))
        f = self.origname_to_file[filename]
        f.update(self.root)

    def push(self):
        repo = Repo(self.root)
        try:
            origin = repo.remotes.origin
            origin.push()
        except AttributeError:
            sys.exit('No remote `origin` found in repo {}'.format(self.root))

    def __repr__(self):
        out = "{{ 'root': {}, 'files': [\n".format(self.root)
        out += ',\n'.join(map(str, self.files))
        out += "] }"
        return out 

    def yaml(self):
        print yaml.dump({ 'files': map(File.to_dict, self.files) }, default_flow_style=False)
