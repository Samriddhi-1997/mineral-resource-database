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
        sustainability_score FLOAT,
        FOREIGN KEY (mineral_id) REFERENCES minerals(id)
    );
''')
def calculate_sustainability_ratio(carbon_emissions, water_usage, land_degradation, energy_consumption, rehabilitation_efforts, extraction_cost):
    # Calculate the sustainability ratio using the given formula
    sustainability_ratio = (rehabilitation_efforts - (carbon_emissions + water_usage + land_degradation + energy_consumption)) / (rehabilitation_efforts + extraction_cost%1000)
    return sustainability_ratio
# Insert data into the environmental_impact table
# Insert data into the environmental_impact table
for _, row in impact_data.iterrows():
    # Extract values from the current row
    carbon_emissions = row['carbon_emissions']
    water_usage = row['water_usage']
    land_degradation = row['land_degradation']
    energy_consumption = row['energy_consumption']
    rehabilitation_efforts = row['rehabilitation_efforts']

    # Fetch the extraction cost from the minerals table using the mineral_id
    # Fetch the extraction cost from the minerals table using the mineral_id
cursor.execute('''
    SELECT extraction_cost FROM minerals WHERE id = ?
''', (row['mineral_id'],))
result = cursor.fetchone()

# Remove commas and convert to float
if result and result[0] is not None:
    try:
        extraction_cost = float(result[0].replace(',', ''))  # Remove commas before converting to float
    except ValueError:
        extraction_cost = 0.0  # Default to 0.0 if conversion fails
else:
    extraction_cost = 0.0  # Default to 0.0 if None

    # Calculate sustainability ratio
    try:
        sustainability_score = calculate_sustainability_ratio(
            carbon_emissions, 
            water_usage, 
            land_degradation, 
            energy_consumption, 
            rehabilitation_efforts, 
            extraction_cost
        )
    except ZeroDivisionError:
        sustainability_score = 0  # Handle division by zero gracefully

    # Insert data into the environmental_impact table
    cursor.execute('''
        INSERT INTO environmental_impact (mineral_id, carbon_emissions, water_usage, land_degradation, energy_consumption, rehabilitation_efforts, sustainability_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        row['mineral_id'], 
        carbon_emissions, 
        water_usage, 
        land_degradation, 
        energy_consumption, 
        rehabilitation_efforts,
        sustainability_score
    ))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data imported successfully!")
