from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/minerals', methods=['GET', 'POST'])
def minerals():
    search_query = request.args.get('query', '')  # Get search query from URL parameters
    conn = sqlite3.connect('database/mineral_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT minerals.*, environmental_impact.*
    FROM minerals
    LEFT JOIN environmental_impact ON minerals.id = environmental_impact.mineral_id
    """
    params = []

    if search_query:
        query += " WHERE name LIKE ? OR location LIKE ? OR applications LIKE ?"
        like_pattern = f"%{search_query}%"
        params = [like_pattern, like_pattern, like_pattern]

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return render_template('mineral.html', minerals=rows, search_query=search_query)
if __name__ == '__main__':
    app.run(debug=True)
