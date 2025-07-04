from setuptools import setup, find_packages
import os

setup(
    name='tracex',
    version='1.0.0',
    description='TraceX: FastAPI-based web app for extracting IPs and hashes from files and archives',
    author='Your Name',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'fastapi',
        'uvicorn',
        'python-multipart',
        'jinja2',
        'requests',
        'pydantic',
        'sqlalchemy',
    ],
    package_data={
        '': ['static/*', 'static/**/*', 'sample_data/*', 'sample_data/**/*'],
    },
    data_files=[
        ('static', [os.path.join('static', f) for f in os.listdir('static') if os.path.isfile(os.path.join('static', f))]),
    ],
    entry_points={
        'console_scripts': [
            'tracex=extractor.webapp:main',
        ],
    },
    python_requires='>=3.7',
) 