import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
from extractor.file_discovery import FileDiscovery
from extractor.archive_handler import ArchiveHandler
from extractor.db_manager import DBManager
from extractor.ip_extractor import TraceXExtractor

def process_file(file_path, archive_handler, ip_extractor, result_queue):
    if archive_handler.is_archive(file_path):
        try:
            extracted_files = archive_handler.extract(file_path)
            for extracted_file in extracted_files:
                process_file(extracted_file, archive_handler, ip_extractor, result_queue)
        except Exception:
            pass
    else:
        for ip_info in ip_extractor.extract_ips(file_path):
            result_queue.put(ip_info)

def main():
    parser = argparse.ArgumentParser(description="Extract public IP addresses from files and archives.")
    parser.add_argument("input_path", help="Path to file or directory to scan.")
    parser.add_argument("--db", default="ip_addresses.db", help="Path to output SQLite database.")
    parser.add_argument("--print-db", action="store_true", help="Print all extracted IPs from the database after processing.")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use for processing.")
    args = parser.parse_args()
    db = DBManager(args.db)
    file_discovery = FileDiscovery()
    archive_handler = ArchiveHandler()
    ip_extractor = TraceXExtractor()
    files = file_discovery.discover(args.input_path)
    result_queue = Queue()
    lock = threading.Lock()
    def db_writer():
        while True:
            ip_info = result_queue.get()
            if ip_info is None:
                break
            with lock:
                db.save_ip(ip_info)
            result_queue.task_done()
    writer_thread = threading.Thread(target=db_writer)
    writer_thread.start()
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(process_file, file_path, archive_handler, ip_extractor, result_queue) for file_path in files]
        for future in as_completed(futures):
            pass
    result_queue.put(None)
    writer_thread.join()
    db.close()
    
    # Clean up archive handler temporary directories
    try:
        archive_handler.cleanup_all()
    except Exception:
        pass
    if args.print_db:
        db = DBManager(args.db)
        all_ips = db.fetch_all_ips()
        for row in all_ips:
            print(row)
        db.close()
if __name__ == "__main__":
    main() 