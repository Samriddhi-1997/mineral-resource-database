import sqlite3
import pandas as pd

# Define the CSV file paths
mineral_csv_file = '/workspaces/mineral-resource-database/explo/mineral.csv'
impact_csv_file = '/workspaces/mineral-resource-database/explo/environmental_impact.csv'

# Define the SQLite database file path (single database for both tables)
db_file = 'database/mineral_data.db'

# Read the CSV data into pandas DataFrames
mineral_data = pd.read_csv(mineral_csv_file)
impact_data = pd.read_csv(impact_csv_file)

# Clean the column names by removing the units (i.e., remove anything inside parentheses)
mineral_data.columns = mineral_data.columns.str.replace(r' \([^)]*\)', '', regex=True)
impact_data.columns = impact_data.columns.str.replace(r' \([^)]*\)', '', regex=True)

# Connect to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create the minerals table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS minerals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        reserve_size REAL,
        grade REAL,
        extraction_cost REAL,
        applications TEXT
    );
''')

# Insert data into the minerals table
for _, row in mineral_data.iterrows():
    cursor.execute('''
        INSERT INTO minerals (name, location, reserve_size, grade, extraction_cost, applications)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['name'], row['location'], row['reserve_size'], row['grade'], row['extraction_cost'], row['applications']))

# Create the environmental_impact table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS environmental_impact (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mineral_id INTEGER,
        carbon_emissions FLOAT,
        water_usage FLOAT,
        land_degradation FLOAT,
        energy_consumption FLOAT,
        rehabilitation_efforts INTEGER,
        sustainability_score INTEGER,
        FOREIGN KEY (mineral_id) REFERENCES minerals(id)
    );
''')

# Insert data into the environmental_impact table
for _, row in impact_data.iterrows():
    cursor.execute('''
        INSERT INTO environmental_impact (mineral_id, carbon_emissions, water_usage, land_degradation, energy_consumption, rehabilitation_efforts)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['mineral_id'], row['carbon_emissions'], row['water_usage'], row['land_degradation'], row['energy_consumption'], row['rehabilitation_efforts']))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data imported successfully!")
