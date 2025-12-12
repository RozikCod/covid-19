from flask import Flask, request, jsonify
from flask_cors import CORS
from database import CovidDatabase, UserDatabase
import pandas as pd

app = Flask(__name__)
CORS(app)

# Initialize databases
covid_db = CovidDatabase()
user_db = UserDatabase()

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({'status': 'healthy', 'message': 'COVID-19 API is running'})

# Authentication endpoints
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Missing credentials'}), 400
        
        success, message = user_db.register_user(username, password)
        return jsonify({'success': success, 'message': message}), 200 if success else 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Missing credentials'}), 400
        
        success, message = user_db.authenticate_user(username, password)
        return jsonify({
            'success': success, 
            'message': message, 
            'username': username if success else None
        }), 200 if success else 401
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# COVID data endpoints
@app.route('/api/countries', methods=['GET'])
def get_countries():
    """Get all countries"""
    try:
        countries = covid_db.get_all_countries()
        return jsonify({'countries': countries, 'count': len(countries)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/country/<country_name>', methods=['GET'])
def get_country_data(country_name):
    """Get data for a specific country"""
    try:
        data = covid_db.get_country_data(country_name)
        if data is None:
            return jsonify({'error': 'Country not found'}), 404
        return jsonify({'country': country_name, 'data': data, 'count': len(data)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/global-summary', methods=['GET'])
def get_global_summary():
    """Get global COVID summary"""
    try:
        summary = covid_db.get_global_summary()
        if summary is None:
            return jsonify({'error': 'No data available'}), 404
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-countries', methods=['GET'])
def get_top_countries():
    """Get top countries by metric"""
    try:
        metric = request.args.get('metric', 'confirmed')
        limit = int(request.args.get('limit', 10))
        
        if limit < 1 or limit > 50:
            return jsonify({'error': 'Limit must be between 1 and 50'}), 400
        
        top_countries = covid_db.get_top_countries(metric, limit)
        return jsonify({'metric': metric, 'countries': top_countries, 'count': len(top_countries)})
    except ValueError:
        return jsonify({'error': 'Invalid limit parameter'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_countries():
    """Compare multiple countries"""
    try:
        data = request.json
        countries = data.get('countries', [])
        
        if not countries:
            return jsonify({'error': 'No countries provided'}), 400
        
        if len(countries) > 10:
            return jsonify({'error': 'Maximum 10 countries allowed'}), 400
        
        comparison = covid_db.compare_countries(countries)
        return jsonify({'comparison': comparison, 'count': len(comparison)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add-case', methods=['POST'])
def add_case():
    """Add a new COVID case"""
    try:
        data = request.json
        required_fields = ['country', 'confirmed', 'deaths', 'recovered']
        
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False, 
                'message': 'Missing required fields',
                'required': required_fields
            }), 400
        
        # Validate numeric fields
        for field in ['confirmed', 'deaths', 'recovered']:
            if not isinstance(data[field], (int, float)) or data[field] < 0:
                return jsonify({
                    'success': False,
                    'message': f'{field} must be non-negative'
                }), 400
        
        success = covid_db.add_new_case(data)
        return jsonify({
            'success': success,
            'message': 'Case added successfully' if success else 'Failed to add case'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get various statistics"""
    try:
        if covid_db.df is None or len(covid_db.df) == 0:
            return jsonify({'error': 'No data available'}), 404
        
        stats = {
            'total_records': len(covid_db.df),
            'date_range': {
                'start': str(covid_db.df['date'].min()) if 'date' in covid_db.df.columns else None,
                'end': str(covid_db.df['date'].max()) if 'date' in covid_db.df.columns else None
            },
            'countries_count': len(covid_db.get_all_countries()),
            'columns': list(covid_db.df.columns)
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("Starting COVID-19 Data Analysis API...")
    print("API: http://localhost:5000")
    print("=" * 50)
    print("\nEndpoints:")
    print("  GET  /api/health")
    print("  POST /api/register")
    print("  POST /api/login")
    print("  GET  /api/countries")
    print("  GET  /api/country/<name>")
    print("  GET  /api/global-summary")
    print("  GET  /api/top-countries")
    print("  POST /api/compare")
    print("  POST /api/add-case")
    print("  GET  /api/statistics")
    print("=" * 50)
    app.run(debug=True, port=5000)