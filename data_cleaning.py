import pandas as pd
import numpy as np
from datetime import datetime

class CovidDataCleaner:
    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        
    def load_data(self):
        """Load COVID-19 dataset"""
        try:
            self.df = pd.read_csv(self.filepath)
            print(f"Data loaded successfully: {self.df.shape}")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def clean_data(self):
        """Clean and preprocess the data"""
        if self.df is None:
            print("Please load data first")
            return None
        
        # Make a copy
        df_clean = self.df.copy()
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates()
        
        # Handle missing values
        # Fill numeric columns with 0
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(0)
        
        # Fill categorical columns with 'Unknown'
        categorical_cols = df_clean.select_dtypes(include=['object']).columns
        df_clean[categorical_cols] = df_clean[categorical_cols].fillna('Unknown')
        
        # Convert date columns
        date_columns = [col for col in df_clean.columns if 'date' in col.lower()]
        for col in date_columns:
            try:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            except:
                pass
        
        # Remove negative values in case/death counts and ensure numeric
        count_cols = [col for col in df_clean.columns if any(x in col.lower() 
                     for x in ['case', 'death', 'confirmed', 'recovered', 'active'])]
        for col in count_cols:
            if col in df_clean.columns:
                # Convert to numeric first, then clip
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
                df_clean[col] = df_clean[col].clip(lower=0)
                # Convert to integer
                df_clean[col] = df_clean[col].astype(int)
        
        # Standardize country names
        if 'country' in df_clean.columns:
            df_clean['country'] = df_clean['country'].str.strip().str.title()
        
        self.df = df_clean
        print(f"Data cleaned successfully: {self.df.shape}")
        return self.df
    
    def get_summary_statistics(self):
        """Get summary statistics of the cleaned data"""
        if self.df is None:
            return None
        
        summary = {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'missing_values': self.df.isnull().sum().to_dict(),
            'numeric_summary': self.df.describe().to_dict()
        }
        return summary
    
    def save_cleaned_data(self, output_path):
        """Save cleaned data to CSV"""
        if self.df is None:
            print("No data to save")
            return False
        
        try:
            self.df.to_csv(output_path, index=False)
            print(f"Cleaned data saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

# Example usage
if __name__ == "__main__":
    cleaner = CovidDataCleaner('covid_data.csv')
    if cleaner.load_data():
        cleaner.clean_data()
        cleaner.save_cleaned_data('covid_data_cleaned.csv')
        summary = cleaner.get_summary_statistics()
        if summary:
            print("\n=== Summary Statistics ===")
            print(f"Total rows: {summary['total_rows']}")
            print(f"Total columns: {summary['total_columns']}")