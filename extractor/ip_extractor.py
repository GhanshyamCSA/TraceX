import re
import ipaddress
import os

class TraceXExtractor:
    IPV4_PATTERN = re.compile(r'(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)')
    IPV6_PATTERN = re.compile(r'(?<![\w:])([A-Fa-f0-9]{1,4}:){2,7}[A-Fa-f0-9]{1,4}(?![\w:])')
    MD5_PATTERN = re.compile(r'\b[a-fA-F0-9]{32}\b')
    SHA1_PATTERN = re.compile(r'\b[a-fA-F0-9]{40}\b')
    SHA256_PATTERN = re.compile(r'\b[a-fA-F0-9]{64}\b')
    SHA512_PATTERN = re.compile(r'\b[a-fA-F0-9]{128}\b')

    def extract_ips(self, file_path):
        abs_path = os.path.abspath(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_number, line in enumerate(f, 1):
                    for match in self.IPV4_PATTERN.findall(line):
                        ip = match
                        if self.is_valid_public_ip(ip, 4):
                            yield {
                                'ip': ip,
                                'version': 4,
                                'path': abs_path,
                                'line_number': line_number
                            }
                    for match in self.IPV6_PATTERN.findall(line):
                        ip = match if ':' in match else line.strip()
                        if self.is_valid_public_ip(ip, 6):
                            yield {
                                'ip': ip,
                                'version': 6,
                                'path': abs_path,
                                'line_number': line_number
                            }
        except Exception as e:
            return

    def is_valid_public_ip(self, ip, version):
        try:
            if version == 4:
                ip_obj = ipaddress.IPv4Address(ip)
            else:
                ip_obj = ipaddress.IPv6Address(ip)
            return ip_obj.is_global
        except Exception:
            return False

    def extract_hashes(self, file_path):
        abs_path = os.path.abspath(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_number, line in enumerate(f, 1):
                    for match in self.MD5_PATTERN.findall(line):
                        yield {
                            'hash_value': match,
                            'hash_type': 'MD5',
                            'path': abs_path,
                            'line_number': line_number
                        }
                    for match in self.SHA1_PATTERN.findall(line):
                        yield {
                            'hash_value': match,
                            'hash_type': 'SHA1',
                            'path': abs_path,
                            'line_number': line_number
                        }
                    for match in self.SHA256_PATTERN.findall(line):
                        yield {
                            'hash_value': match,
                            'hash_type': 'SHA256',
                            'path': abs_path,
                            'line_number': line_number
                        }
                    for match in self.SHA512_PATTERN.findall(line):
                        yield {
                            'hash_value': match,
                            'hash_type': 'SHA512',
                            'path': abs_path,
                            'line_number': line_number
                        }
        except Exception as e:
            return

    @staticmethod
    def detect_hash_type(hash_value):
        length = len(hash_value)
        if length == 32:
            return 'MD5'
        elif length == 40:
            return 'SHA1'
        elif length == 64:
            return 'SHA256'
        elif length == 128:
            return 'SHA512'
        else:
            return 'Unknown' 