import pandas as pd
import logging
from datetime import datetime
import math

logger = logging.getLogger("expenses")


class ExpensesProcessor:

    def __init__(self, csv_file):
        self.required_expenses_columns = ["date", "amount", "source", "destination", "type", "content", "person", "labels"]
        df = pd.read_csv(csv_file, header=0)
        df.columns = df.columns.str.lower()
        assert self.validate_csv_schema(df)
        df["date"] = pd.to_datetime(df["date"])
        df["source"].fillna("", inplace=True)
        df["destination"].fillna("", inplace=True)
        df["type"].fillna("", inplace=True)
        df["content"].fillna("", inplace=True)
        df["person"].fillna("", inplace=True)
        df["labels"].fillna("", inplace=True)
        df = df[self.required_expenses_columns]  # make sure columns are in the correct order
        self.df = df

    def query_from_str(self, query_str, page_size=100, page=1, ascending=True, to_format="list"):
        # TODO - parse query string and query
        data = self.query(ascending=ascending)
        num_pages = math.ceil(data.shape[0] / page_size)
        if page > num_pages:
            page = num_pages
        if page < 1:
            page = 1
        start_index = (page - 1) * page_size
        end_index = page * page_size
        data = data.iloc[start_index:end_index]

        columns = data.columns.tolist()
        column_names = [co.title() for co in columns]
        if to_format == "list":
            data = data.values.tolist()
        elif to_format == "json":
            data = data.to_json(orient='values')
        return data, column_names, num_pages, page


    def query(self, date_range=None, amount_range=None, source_list=None, destination_list=None,
              type_list=None, person_list=None, label_list=None, ascending=True, ):
        result = self.df
        if date_range:
            start_date = date_range[0]
            end_date = date_range[1]
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                result = result[result["date"] >= start_date]
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                result = result[result["date"] <= end_date]
        if amount_range:
            low_amount = amount_range[0]
            high_amount = amount_range[1]
            if low_amount:
                result = result[result["amount"] >= low_amount]
            if high_amount:
                result = result[result["amount"] <= high_amount]
        if source_list:
            result = result[result["source"].isin(source_list)]
        if destination_list:
            result = result[result["destination"].isin(destination_list)]
        if type_list:
            result = result[result["type"].isin(type_list)]
        if person_list:
            result = result[result["type"].isin(person_list)]
        if label_list:
            mask = result["labels"].apply(lambda x: all(label in x.split('|') for label in label_list))
            result = result[mask]

        # convert pipe into comma for label list
        result["labels"] = result["labels"].apply(lambda x: x.replace('|', ','))

        # keep only date part of date
        result["date"] = result["date"].dt.strftime('%Y-%m-%d')

        # sort by date
        result = result.sort_values(by="date", ascending=ascending)
        return result

    def validate_csv_schema(self, df):
        columns = df.columns
        for req_col in self.required_expenses_columns:
            if req_col not in columns:
                return False
        return True

    def get_chart_info(self):
        pass

    def save_csv(self, save_path):
        pass
