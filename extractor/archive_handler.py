import os
import zipfile
import tarfile
import tempfile
import shutil

class ArchiveHandler:
    SUPPORTED_EXTENSIONS = {'.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2'}

    def __init__(self):
        self.temp_dirs = []

    def is_archive(self, file_path):
        file_path = file_path.lower()
        for ext in self.SUPPORTED_EXTENSIONS:
            if file_path.endswith(ext):
                return True
        return False

    def extract(self, archive_path):
        temp_dir = tempfile.mkdtemp(prefix="ipextract_")
        self.temp_dirs.append(temp_dir)
        extracted_files = []
        try:
            if archive_path.lower().endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(temp_dir)
                    for name in zf.namelist():
                        abs_path = os.path.join(temp_dir, name)
                        if os.path.isfile(abs_path):
                            extracted_files.append(abs_path)
            elif any(archive_path.lower().endswith(ext) for ext in ['.tar', '.tar.gz', '.tgz', '.tar.bz2']):
                with tarfile.open(archive_path, 'r:*') as tf:
                    tf.extractall(temp_dir)
                    for member in tf.getmembers():
                        abs_path = os.path.join(temp_dir, member.name)
                        if os.path.isfile(abs_path):
                            extracted_files.append(abs_path)
            else:
                raise ValueError(f"Unsupported archive type: {archive_path}")
        except Exception as e:
            self.cleanup_temp_dir(temp_dir)
            raise e
        return extracted_files

    def cleanup_temp_dir(self, temp_dir):
        try:
            if temp_dir in self.temp_dirs:
                self.temp_dirs.remove(temp_dir)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception:
            pass

    def cleanup_all(self):
        for temp_dir in self.temp_dirs[:]:
            self.cleanup_temp_dir(temp_dir) 