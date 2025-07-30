import pandas as pd
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_distances


class SampleDataModel:
    def __init__(self, csv_path):
        self.df_all = pd.read_csv(
            csv_path,
            # dtype=str  # vermeidet teure Typ-Inferezen
            low_memory=False,  # verhindert Warnungen bei gemischten Datentypen
        )
        if 'distance' not in self.df_all.columns:
            self.df_all['distance'] = np.nan
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

    def compute_distances(self, reference_file, selected_features):
        """
        Compute distances of all filtered files to the reference_file,
        based on selected numerical features.
        """
        df = self.df_filtered
        ref_row = df[df['stem'] == reference_file]
        if ref_row.empty:
            print("Referenzdatei nicht gefunden!")
            return df

        ref_values = ref_row[selected_features].astype(float).values[0]
        other_values = df[selected_features].astype(float).values

        distances = np.linalg.norm(other_values - ref_values, axis=1)
        df_with_dist = df.copy()
        df_with_dist['distance'] = distances

        df_sorted = df_with_dist.sort_values('distance')
        return df_sorted

    def compute_cosine_distances(self, reference_file, selected_features):
        df = self.df_filtered
        ref_row = df[df['stem'] == reference_file]
        if ref_row.empty:
            return df

        ref_values = ref_row[selected_features].astype(float).values
        other_values = df[selected_features].astype(float).values

        distances = cosine_distances(other_values, ref_values).flatten()
        df_with_dist = df.copy()
        df_with_dist['distance'] = distances
        return df_with_dist.sort_values('distance')
