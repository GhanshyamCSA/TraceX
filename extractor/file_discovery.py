import os

class FileDiscovery:
    def discover(self, input_path):
        files = []
        input_path = os.path.abspath(input_path)
        if os.path.isfile(input_path):
            files.append(input_path)
        elif os.path.isdir(input_path):
            for root, _, filenames in os.walk(input_path):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        else:
            raise FileNotFoundError(f"Input path '{input_path}' does not exist.")
        return files 