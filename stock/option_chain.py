import yfinance as yf
import os
from .stock_utils import zip_and_delete_source, get_today
from Recorder.recorder_utils import read_secret_keys

# get all existing option expiration dates for a symbol
def get_option_expiration_dates(symbol: str):
    try:
        if not symbol or not isinstance(symbol, str):
            raise ValueError()
        stock = yf.Ticker(symbol)
        return stock.options
    except:
        print("get_options: Cannot get options of stock: " + str(symbol))


# get option chain data of a symbol and exercise date
def get_option_chain(symbol: str, exercise_date: str):
    try:
        if not symbol or not isinstance(symbol, str):
            raise ValueError()
        stock = yf.Ticker(symbol)
        return stock.option_chain(exercise_date)
    except:
        print("get_options: Cannot get options of stock: " + str(symbol) + 'with exercise date=' + exercise_date)


# get monitored tickers (symbols) from a reference file
def get_tickers_for_options(input_path: str):
    with open(input_path, 'r') as input:
        symbols = []
        for line in input:
            symbols.append(line.strip())
        print('tickers for option: ', symbols)
        return yf.Tickers(" ".join(symbols)).tickers


# get monitored symbols from reference file and write option chain data to files
# output_dir: dir of output files
# input_path: path of input reference file with symbols
# revised_date: the date of current day, this is only used if downloading data in a holiday
def write_monitored_options_to_csv(output_dir: str, tickers_list: list[str], revised_date='',
                                   dry_run=False):
    today = get_today()
    if revised_date:
        today = revised_date

    tickers = yf.Tickers(" ".join(tickers_list)).tickers
    print('Getting option chain for symbols:', tickers_list)
    for symbol in tickers:
        ticker = tickers[symbol]
        symbol = ticker.ticker
        exp_dates = ticker.options

        for exp_date in exp_dates:
            call_file_dir = os.path.join(output_dir, today, symbol, 'call', 'expire=' + exp_date)
            put_file_dir = os.path.join(output_dir, today, symbol, 'put', 'expire=' + exp_date)

            if not dry_run:
                os.makedirs(call_file_dir, exist_ok=True)
                os.makedirs(put_file_dir, exist_ok=True)

            call_file_name = ''.join([symbol, '_call_exp=', exp_date, '_on=', today, '.csv'])
            put_file_name = ''.join([symbol, '_put_exp=', exp_date, '_on=', today, '.csv'])

            option_chain = ticker.option_chain(exp_date)
            if not dry_run:
                option_chain[0].to_csv(os.path.join(call_file_dir, call_file_name), sep='\t', encoding='utf-8')
            print(' '.join([symbol, 'Call options with', 'expire date =', exp_date, 'on =', today, 'is written to',
                            call_file_dir]))
            if not dry_run:
                option_chain[1].to_csv(os.path.join(put_file_dir, put_file_name), sep='\t', encoding='utf-8')
            print(' '.join(
                [symbol, 'Put options with', 'expire date =', exp_date, 'on =', today, 'is written to', put_file_dir]))

    # zip and delete unzipped
    unzipped_dir = os.path.join(output_dir, today)
    zipped_path = os.path.join(output_dir, f"{today}_option_chain.zip")
    zip_and_delete_source(unzipped_dir, zipped_path, True)


def get_option_chain_output_dir():
    return read_secret_keys()['OPTION_CHAIN_OUTPUT_DIR']