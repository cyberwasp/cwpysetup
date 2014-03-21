import hashlib
import os


class Manifest(object):
    def __init__(self, root, ignore):
        self.root = root
        self.ignore = ignore
        self.md5sums = {}

    def refresh(self):
        for root_dir, dir_names, file_names in os.walk(self.root):
            for file_name in file_names:
                full_file_name = os.path.join(root_dir, file_name)
                relative_file_name = os.path.relpath(full_file_name, self.root)
                md5sum = hashlib.md5(open(full_file_name).read()).hexdigest()
                self.md5sums[relative_file_name] = md5sum

    def load(self):
        pass


