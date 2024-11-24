import sqlite3

# Connect to SQLite database (creates a new file if it doesn't exist)
conn = sqlite3.connect("minerals.db")
cursor = conn.cursor()

# Create a table for minerals
cursor.execute("""
CREATE TABLE IF NOT EXISTS MineralResources (
    id INTEGER PRIMARY KEY,
    name TEXT,
    location TEXT,
    reserve_size REAL,
    carbon_emissions REAL,
    water_usage REAL
)
""")

# Add sample data (optional)
cursor.execute("INSERT INTO MineralResources (name, location, reserve_size, carbon_emissions, water_usage) VALUES (?, ?, ?, ?, ?)",
               ("Gold", "Australia", 5000, 5.0, 250))
cursor.execute("INSERT INTO MineralResources (name, location, reserve_size, carbon_emissions, water_usage) VALUES (?, ?, ?, ?, ?)",
               ("Copper", "Chile", 10000, 3.5, 200))
conn.commit()
print("Database and sample data created!")

def add_mineral():
    name = input("Enter mineral name: ")
    location = input("Enter location: ")
    reserve_size = float(input("Enter reserve size (in tons): "))
    carbon_emissions = float(input("Enter carbon emissions (kg CO2/ton): "))
    water_usage = float(input("Enter water usage (liters/ton): "))
    
    cursor.execute("INSERT INTO MineralResources (name, location, reserve_size, carbon_emissions, water_usage) VALUES (?, ?, ?, ?, ?)",
                   (name, location, reserve_size, carbon_emissions, water_usage))
    conn.commit()
    print("Mineral added successfully!")

def view_minerals():
    cursor.execute("SELECT * FROM MineralResources")
    results = cursor.fetchall()
    print("\nID | Name | Location | Reserve Size | Carbon Emissions | Water Usage")
    print("-" * 60)
    for row in results:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} tons | {row[4]} kg | {row[5]} liters")

# Menu
while True:
    print("\n1. Add Mineral\n2. View Minerals\n3. Exit")
    choice = input("Choose an option: ")
    if choice == "1":
        add_mineral()
    elif choice == "2":
        view_minerals()
    elif choice == "3":
        break
    else:
        print("Invalid choice. Please try again.")

import matplotlib.pyplot as plt

def visualize_data():
    cursor.execute("SELECT name, carbon_emissions, water_usage FROM MineralResources")
    results = cursor.fetchall()
    
    # Extract data for plotting
    minerals = [row[0] for row in results]
    emissions = [row[1] for row in results]
    water_usage = [row[2] for row in results]
    
    # Plot data
    plt.figure(figsize=(8, 5))
    bar_width = 0.4
    x = range(len(minerals))
    
    plt.bar(x, emissions, width=bar_width, label="Carbon Emissions (kg CO2/ton)", color='orange')
    plt.bar([i + bar_width for i in x], water_usage, width=bar_width, label="Water Usage (liters/ton)", color='blue')
    
    plt.xlabel("Minerals")
    plt.ylabel("Impact")
    plt.title("Environmental Impact of Minerals")
    plt.xticks([i + bar_width / 2 for i in x], minerals)
    plt.legend()
    plt.show()

print("\n1. Add Mineral\n2. View Minerals\n3. Visualize Data\n4. Exit")
if choice == "3":
    visualize_data()
