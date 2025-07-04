# TraceX

A modern, web-based tool for extracting **public** IP addresses and cryptographic hashes from files and archives. Built with FastAPI and a beautiful frontend, TraceX is designed for digital forensics, threat intelligence, and data analysis workflows.

---

## Features
- Extract **public** IPv4 and IPv6 addresses from text files and archives (private IPs are not extracted)
- Extract cryptographic hashes (MD5, SHA1, SHA256, SHA512)
- Supports ZIP and TAR.GZ archives
- Multithreaded extraction for speed
- Web-based UI (FastAPI + HTML/CSS)
- SQLite database backend for results
- Downloadable and extensible

---

## Installation

### Option 1: Development Setup (Recommended for Testing)

#### Prerequisites
- Python 3.8+
- pip

#### Quick Start
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/TraceX.git
   cd TraceX
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the application:
   ```sh
   python -m extractor.webapp
   ```
5. Open [http://127.0.0.1:55555](http://127.0.0.1:55555) in your browser

### Option 2: Linux System Installation (Shell Script)

#### Prerequisites
- Python 3.8+
- bash

#### Installation Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/TraceX.git
   cd TraceX
   ```
2. Run the installer:
   ```sh
   bash install_tracex.sh
   ```
3. Follow the instructions to activate the virtual environment and run the app.

### Option 3: Docker Installation
```sh
# Build and run with Docker
# (from the project root)
docker build -t tracex .
docker run -p 55555:55555 tracex
```
Or use docker-compose:
```sh
docker-compose up --build
```

---

## Usage
- Upload files or specify a local path via the web UI
- Select extraction options (IPs, hashes, multithreading)
- View and download results
- Sample data is available in the `sample_data/` directory
- **Note:** Only public IPs are extracted; private IPs are ignored

---

## API Endpoints
- `POST /extract` — Extract IPs and/or hashes from uploaded file or local path
- `GET /` — Serve the frontend
- Static files served at `/static/`

---

## Project Structure
```
TraceX/
  extractor/           # Backend FastAPI app and core logic
  static/              # Frontend HTML/CSS/JS
  sample_data/         # Example files and archives
  sample_data_generator.py  # Script to generate sample data
  requirements.txt     # Python dependencies
  setup.py             # Package configuration
  pyproject.toml       # Modern Python packaging config
  Dockerfile           # Docker build file
  docker-compose.yml   # Docker Compose config
  install_tracex.sh    # Linux shell installer
  README.md            # Project documentation
```

---

## Packaging & Distribution

- **PEP 517/518 compatible:**
  - `pyproject.toml` and `setup.py` included for modern Python packaging
  - Build a package with:
    ```sh
    python3 -m build
    ```
- **Wheel and source distributions** are created in the `dist/` directory
- **Docker**: See Docker instructions above
- **Shell script**: See `install_tracex.sh`

---

## Troubleshooting

### Common Issues

#### Port Already in Use
If port 55555 is already in use, you can:
- Kill the process using the port: `sudo lsof -ti:55555 | xargs kill -9`
- Or change the port in the command: `--port 8080`

#### Permission Denied
- Ensure you have the correct permissions to install dependencies and run the app

#### Web Interface Not Accessible
- Verify the app is running
- Check firewall settings: `sudo ufw status`
- Try accessing via localhost: `curl http://127.0.0.1:55555`

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change. 