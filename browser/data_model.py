# data_model.py
import pandas as pd
import re


class SampleDataModel:
    def __init__(self, csv_path):
        self.df_all = pd.read_csv(
            csv_path,
            # dtype=str  # vermeidet teure Typ-Inferezen
            low_memory=False,  # verhindert Warnungen bei gemischten Datentypen
        )
        self.df_filtered = self.df_all.copy()

    def filter_by_regex(self, pattern, column='stem'):
        if not pattern:
            self.df_filtered = self.df_all.copy()
            return self.df_filtered

        try:
            regex = re.compile(pattern, re.IGNORECASE)
            # **Vektorisiert mit Series.str.contains**
            mask = self.df_all[column].str.contains(regex, na=False)
            self.df_filtered = self.df_all[mask].copy()
            return self.df_filtered
        except re.error as e:
            print(f"Regex-Fehler: {e}")
            return self.df_filtered
