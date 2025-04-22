import logging
import os
import zipfile
import re
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

LOG_DIR_NAME = "app/log"
LOG_FILENAME_PREFIX = "megaphone-api"
LOG_FILENAME_SUFFIX = ".log"
ARCHIVE_DIR_NAME = "archive"
ARCHIVE_FILENAME_SUFFIX = ".zip"
LOG_DATE_FORMAT = "%Y-%m-%d"
LOG_FILENAME_FORMAT = f"{LOG_FILENAME_PREFIX}.{LOG_DATE_FORMAT}{LOG_FILENAME_SUFFIX}"
ARCHIVE_FILENAME_FORMAT = f"{LOG_FILENAME_PREFIX}.{LOG_DATE_FORMAT}{ARCHIVE_FILENAME_SUFFIX}"


class CompressedTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, archive_dir=ARCHIVE_DIR_NAME, keep_days=7, **kwargs):
        super().__init__(*args, **kwargs)
        self.archive_dir = os.path.join(os.path.dirname(self.baseFilename), archive_dir)
        self.keep_days = keep_days

        self.suffix = LOG_DATE_FORMAT + LOG_FILENAME_SUFFIX
        self.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}\.log$")

    def doRollover(self):
        super().doRollover()
        self.compress_old_logs()
        self.cleanup_old_archives()

    def compress_old_logs(self):
        os.makedirs(self.archive_dir, exist_ok=True)
        log_dir = os.path.dirname(self.baseFilename)
        base_filename = os.path.basename(self.baseFilename)

        for filename in os.listdir(log_dir):
            # Find files like megaphone-api.YYYY-MM-DD.log
            if filename.startswith(base_filename + '.') and filename != base_filename:
                try:
                    # Try to extract the date part from the filename
                    date_part = filename.replace(base_filename + '.', '')
                    if date_part.endswith('.log'):
                        date_part = date_part[:-4]
                    date_obj = datetime.strptime(date_part, "%Y-%m-%d")

                    today = datetime.now().date()
                    file_date = date_obj.date()
                    if file_date < today:
                        log_file_path = os.path.join(log_dir, filename)
                        # Create zip filename (megaphone-api.YYYY-MM-DD.zip)
                        date_str = date_part
                        zip_filename = f"{LOG_FILENAME_PREFIX}.{date_str}{ARCHIVE_FILENAME_SUFFIX}"
                        zip_path = os.path.join(self.archive_dir, zip_filename)

                        # Compress the file
                        try:
                            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                zipf.write(log_file_path, arcname=filename)
                            # Delete the original file after successful compression
                            os.remove(log_file_path)
                            logging.info(f"Compressed log file {filename} to {zip_filename}")
                        except Exception as e:
                            logging.error(f"Failed to compress {filename}: {e}")
                except ValueError:
                    continue

    def cleanup_old_archives(self):
        cutoff = datetime.now() - timedelta(days=self.keep_days)
        for filename in os.listdir(self.archive_dir):
            if not filename.endswith(ARCHIVE_FILENAME_SUFFIX):
                continue
            date_part = filename.replace(LOG_FILENAME_PREFIX + ".", "").replace(ARCHIVE_FILENAME_SUFFIX, "")
            try:
                file_date = datetime.strptime(date_part, LOG_DATE_FORMAT)
                if file_date < cutoff:
                    os.remove(os.path.join(self.archive_dir, filename))
            except ValueError:
                continue


def configure_logging(log_dir=LOG_DIR_NAME, log_filename=LOG_FILENAME_PREFIX + LOG_FILENAME_SUFFIX, keep_days=90):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_filename)
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = CompressedTimedRotatingFileHandler(
        filename=log_path,
        when="midnight",
        interval=1,
        backupCount=keep_days,
        encoding="utf-8",
        utc=False,
        archive_dir=ARCHIVE_DIR_NAME,
        keep_days=keep_days
    )
    file_handler.setFormatter(log_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # Set root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [file_handler, console_handler]

    # Set Uvicorn loggers
    for logger_name in ("uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.handlers = [file_handler, console_handler]