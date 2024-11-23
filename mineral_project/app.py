import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import make_response
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from werkzeug.security import generate_password_hash, check_password_hash
from weasyprint import HTML
import plotly.graph_objs as go
from plotly.offline import plot
from werkzeug.utils import secure_filename
import os

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Use SQLite for database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mineral_db.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models
from models import Mineral, EnvironmentalMetric

# Routes
@app.route('/')
def home():
    return render_template('index.html')
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Initialize DB
with app.app_context():
    db.create_all()

# Route to handle login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

# Route to handle logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Admin Dashboard (Requires Login)
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Load user for authentication
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/minerals', methods=['GET', 'POST'])
def manage_minerals():
    if request.method == 'POST':
        data = request.json
        new_mineral = Mineral(
            name=data['name'],
            location=data['location'],
            reserve_size=data['reserve_size'],
            grade=data['grade'],
            extraction_cost=data['extraction_cost'],
            applications=data['applications']
        )
        db.session.add(new_mineral)
        db.session.commit()
        return jsonify({'message': 'Mineral added successfully'}), 201

    minerals = Mineral.query.all()
    return jsonify([mineral.to_dict() for mineral in minerals])
@app.route('/visualizations', methods=['GET', 'POST'])
def visualizations():
    # Initially get all minerals from the database
    minerals = Mineral.query.all()

    # Apply search filter (for both GET and POST requests)
    search_query = request.form.get('search', '') if request.method == 'POST' else request.args.get('search', '')
    if search_query:
        minerals = Mineral.query.filter(Mineral.name.contains(search_query)).all()
    
    # Extracting mineral data for charting
    mineral_names = [mineral.name for mineral in minerals]
    reserve_sizes = [mineral.reserve_size for mineral in minerals]
    
    # Handle POST request (when filter is applied)
    if request.method == 'POST' and 'mineral_type' in request.form:
        selected_mineral = request.form['mineral_type']
        if selected_mineral:
            filtered_minerals = [mineral for mineral in minerals if mineral.name == selected_mineral]
            reserve_sizes = [mineral.reserve_size for mineral in filtered_minerals]
            mineral_names = [mineral.name for mineral in filtered_minerals]

    # Plotly chart for reserve sizes
    trace = go.Bar(
        x=mineral_names,
        y=reserve_sizes,
        name='Reserve Size'
    )

    layout = go.Layout(
        title='Mineral Resource Reserve Size',
        xaxis={'title': 'Mineral'},
        yaxis={'title': 'Reserve Size'},
    )

    fig = go.Figure(data=[trace], layout=layout)

    # Convert the plot to HTML
    chart = plot(fig, output_type='div')
    
    return render_template('visualizations.html', chart=chart, minerals=minerals)


# Set up upload folder and allowed file types
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_data', methods=['GET', 'POST'])
@login_required
def upload_data():
    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Process the file based on its type
            if filename.endswith('.csv'):
                try:
                    data = pd.read_csv(file_path)
                except Exception as e:
                    return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 500
            elif filename.endswith('.json'):
                try:
                    data = pd.read_json(file_path)
                except Exception as e:
                    return jsonify({'error': f'Error reading JSON file: {str(e)}'}), 500
            else:
                return jsonify({'error': 'Unsupported file format'}), 400

            # Add data to the database
            for _, row in data.iterrows():
                new_mineral = Mineral(
                    name=row.get('name'),
                    location=row.get('location'),
                    reserve_size=row.get('reserve_size'),
                    grade=row.get('grade'),
                    extraction_cost=row.get('extraction_cost'),
                    applications=row.get('applications')
                )
                db.session.add(new_mineral)
            db.session.commit()

            return jsonify({'message': 'Data uploaded and added to the database successfully'}), 200
    return render_template('upload_data.html')



@app.route('/generate_report', methods=['GET'])
def generate_report():
    try:
        minerals = Mineral.query.all()
        metrics = EnvironmentalMetric.query.all()
        
        # Debugging: Print out the fetched data
        print(minerals)
        print(metrics)

        if not minerals:
            raise ValueError("No minerals found in the database.")
        if not metrics:
            raise ValueError("No metrics found in the database.")
        
        # Create a PDF in memory
        response = make_response()
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=report.pdf'

        # Set up the PDF document
        pdf = canvas.Canvas(response, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(100, 750, "Mineral Resource Sustainability Report")
        y_position = 720

        # Add mineral and sustainability data to the PDF
        for mineral in minerals:
            pdf.drawString(100, y_position, f"Mineral: {mineral.name} | Location: {mineral.location}")
            y_position -= 20

            for metric in metrics:
                if metric.mineral_id == mineral.id:
                    pdf.drawString(100, y_position, f"Carbon Emissions: {metric.carbon_emissions}")
                    y_position -= 20
                    pdf.drawString(100, y_position, f"Water Usage: {metric.water_usage}")
                    y_position -= 20
                    pdf.drawString(100, y_position, f"Land Degradation: {metric.land_degradation}")
                    y_position -= 20
                    pdf.drawString(100, y_position, f"Energy Consumption: {metric.energy_consumption}")
                    y_position -= 20
                    pdf.drawString(100, y_position, f"Rehabilitation Efforts: {metric.rehabilitation_efforts}")
                    y_position -= 30

            if y_position < 50:
                pdf.showPage()
                y_position = 750

        pdf.save()
        return response
    
    except Exception as e:
        # Log the error to the console
        print(f"Error: {str(e)}")
        return "Internal Server Error", 500

@app.route('/ai_suggestions', methods=['GET'])
def ai_suggestions():
    # Simulated dataset for predictions
    data = {
        'carbon_emissions': [100, 200, 150, 300],
        'water_usage': [50, 80, 60, 100],
        'land_degradation': [10, 20, 15, 25],
        'energy_consumption': [200, 400, 300, 600],
        'sustainability_score': [80, 60, 70, 50]
    }
    
    # Create a DataFrame from the dataset
    df = pd.DataFrame(data)

    # Define feature variables (X) and target variable (y)
    X = df[['carbon_emissions', 'water_usage', 'land_degradation', 'energy_consumption']]
    y = df['sustainability_score']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # Initialize and train the linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make a prediction (input values for prediction are just examples)
    prediction = model.predict([[120, 70, 15, 250]])  # New data point for prediction

    # Return the prediction as a JSON response
    return jsonify({'sustainability_score': prediction[0]})


@app.route('/generate_pdf_report')
@login_required
def generate_pdf_report():
    # Generate some data to include in the report
    minerals = Mineral.query.all()

    # Render HTML template for the report
    html = render_template('pdf_report.html', minerals=minerals)

    # Generate PDF from the HTML
    pdf = HTML(string=html).write_pdf()

    # Return the generated PDF file as a response
    return Response(pdf, content_type='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)