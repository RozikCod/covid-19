import pandas as pd
import sqlite3
from datetime import datetime
import os

def import_csv_to_database(csv_file='covid_data_cleaned.csv', db_file='data/covid_data.db'):
    """
    Import COVID-19 data from CSV file into SQLite database
    """
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found!")
        print("Please make sure the CSV file is in the same directory as this script.")
        return False
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print(f"📂 Reading CSV file: {csv_file}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        print(f"✅ Successfully read {len(df)} rows from CSV")
        
        # Display column names to help with mapping
        print(f"\n📋 CSV Columns found: {list(df.columns)}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS covid_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL,
                date TEXT NOT NULL,
                confirmed INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                recovered INTEGER DEFAULT 0,
                active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print(f"\n📊 Database table structure:")
        print("   - country (TEXT)")
        print("   - date (TEXT)")
        print("   - confirmed (INTEGER)")
        print("   - deaths (INTEGER)")
        print("   - recovered (INTEGER)")
        print("   - active (INTEGER)")
        
        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM covid_cases')
        existing_count = cursor.fetchone()[0]
        
        if existing_count > 0:
            print(f"\n⚠️  Warning: Database already contains {existing_count} records.")
            response = input("Do you want to:\n  1. Clear existing data and import fresh\n  2. Append to existing data\n  3. Cancel\nEnter choice (1/2/3): ")
            
            if response == '1':
                cursor.execute('DELETE FROM covid_cases')
                print("🗑️  Cleared existing data")
            elif response == '3':
                print("❌ Import cancelled")
                conn.close()
                return False
            # If 2, continue to append
        
        # Map CSV columns to database columns
        # Adjust these mappings based on your actual CSV column names
        column_mapping = {
            'country': None,
            'date': None,
            'confirmed': None,
            'deaths': None,
            'recovered': None,
            'active': None
        }
        
        # Try to auto-detect column names (case-insensitive)
        csv_cols_lower = {col.lower(): col for col in df.columns}
        
        for db_col in column_mapping.keys():
            # Try exact match (case-insensitive)
            if db_col in csv_cols_lower:
                column_mapping[db_col] = csv_cols_lower[db_col]
            # Try common alternatives
            elif db_col == 'country' and 'country/region' in csv_cols_lower:
                column_mapping[db_col] = csv_cols_lower['country/region']
            elif db_col == 'country' and 'countryregion' in csv_cols_lower:
                column_mapping[db_col] = csv_cols_lower['countryregion']
            elif db_col == 'confirmed' and 'total_confirmed' in csv_cols_lower:
                column_mapping[db_col] = csv_cols_lower['total_confirmed']
            elif db_col == 'deaths' and 'total_deaths' in csv_cols_lower:
                column_mapping[db_col] = csv_cols_lower['total_deaths']
            elif db_col == 'recovered' and 'total_recovered' in csv_cols_lower:
                column_mapping[db_col] = csv_cols_lower['total_recovered']
            elif db_col == 'active' and 'total_active' in csv_cols_lower:
                column_mapping[db_col] = csv_cols_lower['total_active']
        
        print(f"\n🔗 Column Mapping:")
        for db_col, csv_col in column_mapping.items():
            if csv_col:
                print(f"   {db_col:12} ← {csv_col}")
            else:
                print(f"   {db_col:12} ← NOT FOUND (will use default: 0 or current date)")
        
        # Ask user to confirm or manually map columns
        print("\n❓ Is this mapping correct?")
        confirm = input("Press Enter to continue, or 'n' to manually map columns: ")
        
        if confirm.lower() == 'n':
            print("\n📝 Manual Column Mapping:")
            print(f"Available CSV columns: {', '.join(df.columns)}")
            for db_col in column_mapping.keys():
                user_input = input(f"Enter CSV column name for '{db_col}' (or press Enter to skip): ").strip()
                if user_input and user_input in df.columns:
                    column_mapping[db_col] = user_input
                elif user_input:
                    print(f"   ⚠️  Warning: Column '{user_input}' not found in CSV")
        
        # Import data
        print(f"\n⏳ Importing data...")
        imported_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                # Extract values from CSV based on mapping
                country = row[column_mapping['country']] if column_mapping['country'] else 'Unknown'
                date = row[column_mapping['date']] if column_mapping['date'] else datetime.now().strftime('%Y-%m-%d')
                confirmed = int(row[column_mapping['confirmed']]) if column_mapping['confirmed'] and pd.notna(row[column_mapping['confirmed']]) else 0
                deaths = int(row[column_mapping['deaths']]) if column_mapping['deaths'] and pd.notna(row[column_mapping['deaths']]) else 0
                recovered = int(row[column_mapping['recovered']]) if column_mapping['recovered'] and pd.notna(row[column_mapping['recovered']]) else 0
                active = int(row[column_mapping['active']]) if column_mapping['active'] and pd.notna(row[column_mapping['active']]) else 0
                
                # Calculate active if not provided
                if column_mapping['active'] is None and column_mapping['confirmed']:
                    active = confirmed - deaths - recovered
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO covid_cases (country, date, confirmed, deaths, recovered, active)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (country, date, confirmed, deaths, recovered, active))
                
                imported_count += 1
                
                # Show progress every 1000 rows
                if imported_count % 1000 == 0:
                    print(f"   Imported {imported_count} rows...")
                
            except Exception as e:
                skipped_count += 1
                if skipped_count <= 5:  # Show first 5 errors
                    print(f"   ⚠️  Skipped row {index}: {str(e)}")
        
        # Commit changes
        conn.commit()
        
        # Get final count
        cursor.execute('SELECT COUNT(*) FROM covid_cases')
        total_count = cursor.fetchone()[0]
        
        print(f"\n✅ Import completed!")
        print(f"   📊 Total rows imported: {imported_count}")
        if skipped_count > 0:
            print(f"   ⚠️  Rows skipped: {skipped_count}")
        print(f"   💾 Total records in database: {total_count}")
        
        # Show sample data
        print(f"\n📋 Sample data (first 5 rows):")
        cursor.execute('SELECT country, date, confirmed, deaths, recovered, active FROM covid_cases LIMIT 5')
        results = cursor.fetchall()
        
        print(f"\n{'Country':<20} {'Date':<12} {'Confirmed':>12} {'Deaths':>12} {'Recovered':>12} {'Active':>12}")
        print("-" * 92)
        for row in results:
            print(f"{row[0]:<20} {row[1]:<12} {row[2]:>12,} {row[3]:>12,} {row[4]:>12,} {row[5]:>12,}")
        
        # Show statistics by country
        print(f"\n📊 Top 10 Countries by Confirmed Cases:")
        cursor.execute('''
            SELECT country, SUM(confirmed) as total_confirmed
            FROM covid_cases
            GROUP BY country
            ORDER BY total_confirmed DESC
            LIMIT 10
        ''')
        results = cursor.fetchall()
        
        print(f"\n{'Rank':<6} {'Country':<30} {'Total Confirmed':>20}")
        print("-" * 60)
        for i, row in enumerate(results, 1):
            print(f"{i:<6} {row[0]:<30} {row[1]:>20,}")
        
        conn.close()
        
        print(f"\n🎉 Database successfully created at: {db_file}")
        print(f"✅ You can now run your COVID-19 Dashboard application!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during import: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def show_csv_info(csv_file='covid_data_cleaned.csv'):
    """
    Display information about the CSV file
    """
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found!")
        return
    
    print(f"📂 CSV File Information: {csv_file}")
    print("=" * 60)
    
    df = pd.read_csv(csv_file)
    
    print(f"\n📊 Basic Statistics:")
    print(f"   Total rows: {len(df):,}")
    print(f"   Total columns: {len(df.columns)}")
    
    print(f"\n📋 Columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i}. {col} ({df[col].dtype})")
    
    print(f"\n🔍 Sample Data (first 3 rows):")
    print(df.head(3).to_string())
    
    print(f"\n📊 Data Summary:")
    print(df.describe())


if __name__ == "__main__":
    print("=" * 60)
    print("COVID-19 Data Import Tool")
    print("=" * 60)
    
    # Check if CSV file exists
    csv_file = 'covid_data_cleaned.csv'
    
    if not os.path.exists(csv_file):
        print(f"\n❌ CSV file not found: {csv_file}")
        print(f"Please ensure the file is in the current directory.")
        csv_file = input("\nEnter the path to your CSV file: ").strip()
    
    if os.path.exists(csv_file):
        print(f"\n1. Show CSV file information")
        print(f"2. Import CSV data to database")
        print(f"3. Exit")
        
        choice = input(f"\nEnter your choice (1/2/3): ").strip()
        
        if choice == '1':
            show_csv_info(csv_file)
        elif choice == '2':
            import_csv_to_database(csv_file)
        else:
            print("Exiting...")
    else:
        print(f"\n❌ Cannot proceed without CSV file.")