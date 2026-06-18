import sqlite3
import json
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Database initialization
def init_database():
    conn = sqlite3.connect('grievance_system.db')
    cursor = conn.cursor()
    
    # Create grievances table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grievances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference_number TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            student_id TEXT,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            evidence_filename TEXT,
            status TEXT DEFAULT 'Submitted',
            assigned_officer TEXT,
            progress INTEGER DEFAULT 0,
            submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolution TEXT,
            notes TEXT
        )
    ''')
    
    # Create admin users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            email TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Create status history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grievance_id INTEGER,
            old_status TEXT,
            new_status TEXT,
            changed_by TEXT,
            changed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (grievance_id) REFERENCES grievances (id)
        )
    ''')
    
    # Insert default admin user (username: admin, password: admin123)
    cursor.execute('''
        INSERT OR IGNORE INTO admin_users (username, password, full_name, email)
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin123', 'System Administrator', 'admin@nimbusacademy.edu'))
    
    conn.commit()
    conn.close()

# API Routes

@app.route('/')
def index():
    return render_template('redresal.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/grievances', methods=['POST'])
def submit_grievance():
    try:
        data = request.get_json()
        
        # Generate reference number
        ref_number = 'NAM-' + str(int(datetime.datetime.now().timestamp()))[-6:]
        
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO grievances (
                reference_number, full_name, email, phone, student_id,
                category, priority, subject, description, evidence_filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ref_number, data['fullName'], data['email'], data['phone'],
            data.get('studentId', ''), data['category'], data['priority'],
            data['subject'], data['description'], data.get('evidenceFilename', '')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'reference_number': ref_number,
            'message': 'Grievance submitted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/grievances/<reference_number>', methods=['GET'])
def track_grievance(reference_number):
    try:
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM grievances WHERE reference_number = ?', (reference_number,))
        grievance = cursor.fetchone()
        
        if grievance:
            columns = [description[0] for description in cursor.description]
            grievance_dict = dict(zip(columns, grievance))
            
            # Calculate days since submission
            submitted_date = datetime.datetime.fromisoformat(grievance_dict['submitted_date'])
            days_since = (datetime.datetime.now() - submitted_date).days
            
            conn.close()
            
            return jsonify({
                'success': True,
                'grievance': grievance_dict,
                'days_since_submission': days_since
            })
        else:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Grievance not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/grievances', methods=['GET'])
def get_all_grievances():
    try:
        status_filter = request.args.get('status', '')
        category_filter = request.args.get('category', '')
        priority_filter = request.args.get('priority', '')
        search_term = request.args.get('search', '')
        
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM grievances WHERE 1=1
        '''
        params = []
        
        if status_filter:
            query += ' AND status = ?'
            params.append(status_filter)
            
        if category_filter:
            query += ' AND category = ?'
            params.append(category_filter)
            
        if priority_filter:
            query += ' AND priority = ?'
            params.append(priority_filter)
            
        if search_term:
            query += ' AND (reference_number LIKE ? OR full_name LIKE ? OR subject LIKE ?)'
            search_pattern = f'%{search_term}%'
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += ' ORDER BY submitted_date DESC'
        
        cursor.execute(query, params)
        grievances = cursor.fetchall()
        
        if grievances:
            columns = [description[0] for description in cursor.description]
            grievances_list = [dict(zip(columns, row)) for row in grievances]
        else:
            grievances_list = []
        
        conn.close()
        
        return jsonify({
            'success': True,
            'grievances': grievances_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/grievances/<int:grievance_id>', methods=['GET'])
def get_grievance_details(grievance_id):
    try:
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()
        
        # Get grievance details
        cursor.execute('SELECT * FROM grievances WHERE id = ?', (grievance_id,))
        grievance = cursor.fetchone()
        
        if grievance:
            columns = [description[0] for description in cursor.description]
            grievance_dict = dict(zip(columns, grievance))
            
            # Get status history
            cursor.execute('''
                SELECT * FROM status_history 
                WHERE grievance_id = ? 
                ORDER BY changed_date DESC
            ''', (grievance_id,))
            
            history = cursor.fetchall()
            if history:
                history_columns = [description[0] for description in cursor.description]
                history_list = [dict(zip(history_columns, row)) for row in history]
            else:
                history_list = []
            
            grievance_dict['status_history'] = history_list
            conn.close()
            
            return jsonify({
                'success': True,
                'grievance': grievance_dict
            })
        else:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Grievance not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/grievances/<int:grievance_id>', methods=['PUT'])
def update_grievance(grievance_id):
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()
        
        # Get current status for history
        cursor.execute('SELECT status FROM grievances WHERE id = ?', (grievance_id,))
        current = cursor.fetchone()
        
        if not current:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Grievance not found'
            }), 404
        
        old_status = current[0]
        new_status = data.get('status', old_status)
        
        # Update grievance
        update_query = '''
            UPDATE grievances SET 
                status = ?, assigned_officer = ?, progress = ?, 
                resolution = ?, notes = ?, updated_date = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        
        cursor.execute(update_query, (
            new_status, data.get('assigned_officer'), data.get('progress', 0),
            data.get('resolution', ''), data.get('notes', ''), grievance_id
        ))
        
        # Add to status history if status changed
        if old_status != new_status:
            cursor.execute('''
                INSERT INTO status_history (grievance_id, old_status, new_status, changed_by, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (grievance_id, old_status, new_status, data.get('changed_by', 'Admin'), data.get('notes', '')))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Grievance updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/grievances/<int:grievance_id>', methods=['DELETE'])
def delete_grievance(grievance_id):
    try:
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM grievances WHERE id = ?', (grievance_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Grievance deleted successfully'
            })
        else:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Grievance not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM admin_users WHERE username = ? AND password = ?
        ''', (data['username'], data['password']))
        
        user = cursor.fetchone()
        
        if user:
            # Update last login
            cursor.execute('''
                UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE username = ?
            ''', (data['username'],))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'full_name': user[3],
                    'role': user[4],
                    'email': user[5]
                }
            })
        else:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/statistics', methods=['GET'])
def get_statistics():
    try:
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()

        # Total grievances
        cursor.execute('SELECT COUNT(*) FROM grievances')
        total = cursor.fetchone()[0]

        # Status distribution
        cursor.execute('SELECT status, COUNT(*) FROM grievances GROUP BY status')
        status_counts = dict(cursor.fetchall())

        # Category distribution
        cursor.execute('SELECT category, COUNT(*) FROM grievances GROUP BY category')
        category_counts = dict(cursor.fetchall())

        # Priority distribution
        cursor.execute('SELECT priority, COUNT(*) FROM grievances GROUP BY priority')
        priority_counts = dict(cursor.fetchall())

        # Recent grievances (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) FROM grievances
            WHERE submitted_date >= date('now', '-7 days')
        ''')
        recent_count = cursor.fetchone()[0]

        # Average resolution time (for resolved grievances)
        cursor.execute('''
            SELECT AVG(julianday(updated_date) - julianday(submitted_date)) as avg_days
            FROM grievances
            WHERE status = 'Resolved'
        ''')
        avg_resolution = cursor.fetchone()[0] or 0

        conn.close()

        return jsonify({
            'success': True,
            'statistics': {
                'total_grievances': total,
                'status_distribution': status_counts,
                'category_distribution': category_counts,
                'priority_distribution': priority_counts,
                'recent_grievances': recent_count,
                'average_resolution_days': round(avg_resolution, 1)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/users', methods=['GET'])
def get_admin_users():
    try:
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()

        cursor.execute('SELECT id, username, full_name, role, email, created_date, last_login FROM admin_users')
        users = cursor.fetchall()

        if users:
            columns = [description[0] for description in cursor.description]
            users_list = [dict(zip(columns, row)) for row in users]
        else:
            users_list = []

        conn.close()

        return jsonify({
            'success': True,
            'users': users_list
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/users', methods=['POST'])
def create_admin_user():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'password', 'full_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400

        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute('SELECT id FROM admin_users WHERE username = ?', (data['username'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 400

        cursor.execute('''
            INSERT INTO admin_users (username, password, full_name, role, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['username'],
            data['password'],  # In production, this should be hashed
            data['full_name'],
            data.get('role', 'admin'),
            data.get('email', '')
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Admin user created successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_admin_user(user_id):
    try:
        conn = sqlite3.connect('grievance_system.db')
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute('SELECT username FROM admin_users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Admin user not found'
            }), 404

        # Prevent deletion of the default admin
        if user[0] == 'admin':
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Cannot delete default admin user'
            }), 400

        cursor.execute('DELETE FROM admin_users WHERE id = ?', (user_id,))

        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Admin user deleted successfully'
            })
        else:
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Failed to delete admin user'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
