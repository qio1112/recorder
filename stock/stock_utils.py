import os
import shutil
import datetime
import yfinance as yf


def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    print(source, destination, archive_from, archive_to)
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)


# make_archive('/path/to/folder', '/path/to/folder.zip')


def zip_and_delete_source(source_dir: str, target_path: str, delete_unzipped: False):
    print(f"archiving dir: {source_dir} to {target_path}")
    make_archive(source_dir, target_path)
    if delete_unzipped:
        print(f"removing dir: {source_dir}")
        shutil.rmtree(source_dir)
    print(f"zip finished, delete_unzipped={delete_unzipped}")


def get_today():
    return str(datetime.date.today())


def is_trade_day(date=None):
    if not date:
        date = get_today()
    qqq = yf.Ticker('QQQ')
    recent_trade_dt = str(qqq.history(interval="1d", start="2023-01-01").index[-1])[0:10]
    return date == recent_trade_dt
