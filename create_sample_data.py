import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_sample_covid_data():
    """Create sample COVID-19 dataset"""
    
    countries = [
        'United States', 'India', 'Brazil', 'United Kingdom', 'France',
        'Germany', 'Italy', 'Spain', 'Canada', 'Australia',
        'Japan', 'South Korea', 'China', 'Mexico', 'Argentina',
        'Russia', 'Turkey', 'Netherlands', 'Belgium', 'Sweden'
    ]
    
    start_date = datetime.now() - timedelta(days=100)
    dates = [start_date + timedelta(days=i) for i in range(100)]
    
    data = []
    
    for country in countries:
        base_confirmed = np.random.randint(100000, 5000000)
        base_deaths = int(base_confirmed * np.random.uniform(0.01, 0.03))
        base_recovered = int(base_confirmed * np.random.uniform(0.80, 0.95))
        
        for i, date in enumerate(dates):
            growth = 1 + (i / 100) * np.random.uniform(0.1, 0.3)
            
            confirmed = int(base_confirmed * growth + np.random.randint(-10000, 50000))
            deaths = int(base_deaths * growth + np.random.randint(-100, 1000))
            recovered = int(base_recovered * growth + np.random.randint(-5000, 20000))
            active = confirmed - deaths - recovered
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'country': country,
                'confirmed': max(0, confirmed),
                'deaths': max(0, deaths),
                'recovered': max(0, recovered),
                'active': max(0, active)
            })
            
            base_confirmed = confirmed
            base_deaths = deaths
            base_recovered = recovered
    
    df = pd.DataFrame(data)
    df.to_csv('covid_data.csv', index=False)
    
    print("=" * 60)
    print("Sample Dataset Created!")
    print("=" * 60)
    print(f"✓ Records: {len(df):,}")
    print(f"✓ Countries: {len(countries)}")
    print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"✓ Saved as: covid_data.csv")
    print("=" * 60)
    
    return df

if __name__ == "__main__":
    create_sample_covid_data()