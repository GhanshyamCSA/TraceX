import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import uvicorn
import threading
from pathlib import Path

# Handle imports for both direct execution and module import
try:
    # When running as module (python -m extractor.webapp)
    from extractor.file_discovery import FileDiscovery
    from extractor.archive_handler import ArchiveHandler
    from extractor.ip_extractor import TraceXExtractor
    from extractor.db_manager import DBManager
except ImportError:
    # When running directly (python webapp.py)
    from file_discovery import FileDiscovery
    from archive_handler import ArchiveHandler
    from ip_extractor import TraceXExtractor
    from db_manager import DBManager

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the correct path to static directory
current_dir = Path(__file__).parent
static_dir = current_dir / "static"

# Serve static frontend
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

TEMP_UPLOAD_DIR = tempfile.gettempdir()

@app.post("/extract")
def extract_ips(
    use_multithreading: bool = Form(...),
    threads: int = Form(4),
    upload: Optional[List[UploadFile]] = File(None),
    local_path: Optional[str] = Form(None),
    extract_ips: bool = Form(True),
    extract_hashes: bool = Form(False),
    input_mode: str = Form('file')
):
    temp_files = []
    input_paths = []
    if upload:
        if not isinstance(upload, list):
            upload = [upload]
        for upfile in upload:
            if not upfile.filename:
                continue
            rel_path = upfile.filename.replace("..", "_")
            upload_path = os.path.join(TEMP_UPLOAD_DIR, rel_path)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            with open(upload_path, "wb") as f:
                f.write(upfile.file.read())
            temp_files.append(upload_path)
        input_paths = temp_files
    elif local_path:
        input_paths = [local_path.strip()]
        if not input_paths[0]:
            return JSONResponse({"error": "Local path cannot be empty."}, status_code=400)
    else:
        return JSONResponse({"error": "No input provided."}, status_code=400)
    # Validate input paths exist and match mode
    for path in input_paths:
        if not os.path.exists(path):
            return JSONResponse({
                "error": f"Path '{path}' does not exist. Please check the path and try again."
            }, status_code=400)
        # If the path was provided via the path field (not upload), validate according to mode
        if local_path:
            if input_mode == 'file' and not os.path.isfile(path):
                return JSONResponse({
                    "error": "Only file path can be given as input in file mode."
                }, status_code=400)
            if input_mode == 'folder' and not os.path.isdir(path):
                return JSONResponse({
                    "error": "Only folder path can be given as input in folder mode."
                }, status_code=400)
    db_path = os.path.join(TEMP_UPLOAD_DIR, "webapp_output.db")
    db = DBManager(db_path)
    db.clear_ips()
    db.clear_hashes()
    file_discovery = FileDiscovery()
    archive_handler = ArchiveHandler()
    ip_extractor = TraceXExtractor()
    all_files = []
    for input_path in input_paths:
        try:
            if local_path:
                if input_mode == 'file' and os.path.isfile(input_path):
                    all_files.append(input_path)
                elif input_mode == 'folder' and os.path.isdir(input_path):
                    files = file_discovery.discover(input_path)
                    all_files.extend(files)
            else:
                if os.path.isfile(input_path):
                    all_files.append(input_path)
        except FileNotFoundError as e:
            return JSONResponse({
                "error": f"File not found: {str(e)}. Please check the path and try again."
            }, status_code=400)
    ip_results = []
    hash_results = []
    if use_multithreading:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from queue import Queue
        lock = threading.Lock()
        result_queue = Queue()
        def process_file(file_path):
            if archive_handler.is_archive(file_path):
                try:
                    extracted_files = archive_handler.extract(file_path)
                    for extracted_file in extracted_files:
                        process_file(extracted_file)
                except Exception:
                    pass
            else:
                if extract_ips:
                    for ip_info in ip_extractor.extract_ips(file_path):
                        result_queue.put(('ip', ip_info))
                if extract_hashes:
                    for hash_info in ip_extractor.extract_hashes(file_path):
                        result_queue.put(('hash', hash_info))
        def db_writer():
            while True:
                item = result_queue.get()
                if item is None:
                    break
                kind, data = item
                with lock:
                    if kind == 'ip':
                        db.save_ip(data)
                    elif kind == 'hash':
                        db.save_hash(data)
                result_queue.task_done()
        writer_thread = threading.Thread(target=db_writer)
        writer_thread.start()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(process_file, file_path) for file_path in all_files]
            for future in as_completed(futures):
                pass
        result_queue.put(None)
        writer_thread.join()
    else:
        for file_path in all_files:
            if archive_handler.is_archive(file_path):
                try:
                    extracted_files = archive_handler.extract(file_path)
                    for extracted_file in extracted_files:
                        if extract_ips:
                            for ip_info in ip_extractor.extract_ips(extracted_file):
                                db.save_ip(ip_info)
                        if extract_hashes:
                            for hash_info in ip_extractor.extract_hashes(extracted_file):
                                db.save_hash(hash_info)
                except Exception:
                    pass
            else:
                if extract_ips:
                    for ip_info in ip_extractor.extract_ips(file_path):
                        db.save_ip(ip_info)
                if extract_hashes:
                    for hash_info in ip_extractor.extract_hashes(file_path):
                        db.save_hash(hash_info)
    if extract_ips:
        ip_results = db.fetch_all_ips()
    if extract_hashes:
        cursor = db.conn.execute('SELECT hash_value, hash_type, path, line_number FROM hashes ORDER BY path, line_number;')
        columns = [desc[0] for desc in cursor.description]
        hash_results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    db.close()
    # Clean up temp files
    for path in temp_files:
        try:
            os.remove(path)
        except Exception:
            pass
    if extract_ips and extract_hashes:
        return {"ips": ip_results, "hashes": hash_results}
    elif extract_ips:
        return ip_results
    elif extract_hashes:
        return hash_results
    else:
        return {"error": "No extraction type selected."}

@app.get("/")
def serve_index():
    index_path = static_dir / "index.html"
    return FileResponse(str(index_path))

def main():
    uvicorn.run(app, host="127.0.0.1", port=55555)

if __name__ == "__main__":
    main() 