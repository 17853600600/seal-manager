from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pymysql
import bcrypt
from datetime import timedelta
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'seal-management-secret-key-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
jwt = JWTManager(app)

if not os.path.exists('uploads'):
    os.makedirs('uploads')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'wcr_20070430',
    'database': 'seal_management',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

def init_database():
    try:
        conn = pymysql.connect(host='localhost', user='root', password='wcr_20070430', charset='utf8mb4')
        cursor = conn.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS seal_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 数据库创建成功")
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                real_name VARCHAR(50),
                birth_date DATE,
                id_card VARCHAR(18),
                gender VARCHAR(10),
                department VARCHAR(50),
                phone VARCHAR(20),
                organization VARCHAR(50) DEFAULT '默认组织',
                role ENUM('member', 'department_head', 'vice_president', 'president', 'file_manager') DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        print("✅ users 表创建成功")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS approvals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                approval_type VARCHAR(20) DEFAULT 'external',
                applicant_name VARCHAR(50),
                department VARCHAR(50),
                phone VARCHAR(20),
                seal_type VARCHAR(50),
                use_reason TEXT,
                file_name VARCHAR(255),
                partner_unit VARCHAR(255),
                seal_count INT DEFAULT 1,
                location VARCHAR(255),
                pdf_file VARCHAR(255),
                extra_files TEXT,
                
                status ENUM('pending_level1', 'pending_level2', 'pending_level3', 'approved', 'rejected') DEFAULT 'pending_level1',
                
                level1_reviewer INT,
                level1_comment TEXT,
                level1_result ENUM('approved', 'rejected'),
                level1_time DATETIME,
                
                level2_reviewer INT,
                level2_comment TEXT,
                level2_result ENUM('approved', 'rejected', 'forward'),
                level2_time DATETIME,
                level2_risk VARCHAR(20),
                
                level3_reviewer INT,
                level3_comment TEXT,
                level3_result VARCHAR(30),
                level3_time DATETIME,
                level3_amount VARCHAR(100),
                level3_risk_items TEXT,
                level3_project_risk TEXT,
                
                submit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        print("✅ approvals 表创建成功")
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                file_type ENUM('internal', 'external') DEFAULT 'external',
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        print("✅ files 表创建成功")
        
        conn.commit()
        print("✅ 数据库初始化完成！")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# ==================== 注册 ====================
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        real_name = data.get('realName', '').strip()
        department = data.get('department', '').strip()
        phone = data.get('phone', '').strip()
        role = data.get('role', 'member')
        
        if not all([username, password, real_name, department, phone]):
            return jsonify({'success': False, 'message': '请填写所有必填字段'}), 400
        
        if role not in ['member', 'department_head', 'vice_president', 'president', 'file_manager']:
            return jsonify({'success': False, 'message': '角色无效'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            'INSERT INTO users (username, password, real_name, department, phone, role) VALUES (%s, %s, %s, %s, %s, %s)',
            (username, hashed.decode('utf-8'), real_name, department, phone, role)
        )
        conn.commit()
        return jsonify({'success': True, 'message': '注册成功'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 登录 ====================
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        token_data = {'id': user['id'], 'username': user['username'], 'role': user['role'], 'department': user['department'], 'real_name': user['real_name']}
        token = create_access_token(identity=json.dumps(token_data))
        
        role_names = {'member': '成员', 'department_head': '部门负责人', 'vice_president': '分管副总', 'president': '总经理', 'file_manager': '文件管理员'}
        user_info = {
            'id': user['id'], 'username': user['username'], 'realName': user['real_name'] or '',
            'role': user['role'], 'roleName': role_names.get(user['role'], ''),
            'department': user['department'] or '', 'phone': user['phone'] or '',
            'organization': user['organization'] or '默认组织'
        }
        return jsonify({'success': True, 'token': token, 'user': user_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 个人信息 ====================
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_data = json.loads(get_jwt_identity())
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_data['id'],))
        user = cursor.fetchone()
        role_names = {'member': '成员', 'department_head': '部门负责人', 'vice_president': '分管副总', 'president': '总经理', 'file_manager': '文件管理员'}
        profile_complete = all([user['real_name'], user['birth_date'], user['id_card'], user['gender'], user['department'], user['phone']])
        return jsonify({
            'success': True,
            'profile': {
                'realName': user['real_name'] or '', 'birthDate': str(user['birth_date']) if user['birth_date'] else '',
                'idCard': user['id_card'] or '', 'gender': user['gender'] or '',
                'department': user['department'] or '', 'phone': user['phone'] or '',
                'organization': user['organization'] or '默认组织', 'role': user['role'], 'roleName': role_names.get(user['role'], '')
            },
            'profileComplete': profile_complete
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_data = json.loads(get_jwt_identity())
        data = request.get_json()
        real_name = data.get('realName', '').strip()
        birth_date = data.get('birthDate', '').strip()
        id_card = data.get('idCard', '').strip()
        gender = data.get('gender', '').strip()
        department = data.get('department', '').strip()
        phone = data.get('phone', '').strip()
        
        if not all([real_name, birth_date, id_card, gender, department, phone]):
            return jsonify({'success': False, 'message': '请填写所有个人信息'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET real_name=%s, birth_date=%s, id_card=%s, gender=%s, department=%s, phone=%s WHERE id=%s',
                       (real_name, birth_date, id_card, gender, department, phone, user_data['id']))
        conn.commit()
        return jsonify({'success': True, 'message': '更新成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 组织成员 ====================
@app.route('/api/organization/members', methods=['GET'])
@jwt_required()
def get_members():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, real_name, role, department, phone FROM users ORDER BY role, real_name')
        return jsonify({'success': True, 'members': cursor.fetchall()}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 文件下载 ====================
@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)
    except:
        return jsonify({'success': False, 'message': '文件不存在'}), 404

# ==================== 文件管理 ====================
@app.route('/api/files', methods=['GET'])
@jwt_required()
def get_files():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM files ORDER BY created_at DESC')
        files = cursor.fetchall()
        for f in files:
            if f['created_at']: f['created_at'] = f['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'success': True, 'files': files}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/files', methods=['POST'])
@jwt_required()
def add_file():
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'file_manager':
            return jsonify({'success': False, 'message': '只有文件管理员可以操作'}), 403
        
        data = request.get_json()
        file_name = data.get('file_name', '').strip()
        file_type = data.get('file_type', 'external')
        
        if not file_name:
            return jsonify({'success': False, 'message': '请输入文件名称'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO files (file_name, file_type, created_by) VALUES (%s, %s, %s)',
                       (file_name, file_type, user_data['id']))
        conn.commit()
        return jsonify({'success': True, 'message': '添加成功'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/files/<int:fid>', methods=['DELETE'])
@jwt_required()
def delete_file(fid):
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'file_manager':
            return jsonify({'success': False, 'message': '只有文件管理员可以操作'}), 403
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM files WHERE id=%s', (fid,))
        conn.commit()
        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 提交审批 ====================
@app.route('/api/approvals', methods=['POST'])
@jwt_required()
def submit_approval():
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'member':
            return jsonify({'success': False, 'message': '只有成员可以提交审批'}), 403
        
        approval_type = request.form.get('approval_type', 'external')
        pdf_file = request.files.get('pdf_file')
        extra_files = request.files.getlist('extra_files')
        
        pdf_filename = ''
        if pdf_file and pdf_file.filename:
            pdf_filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))
        
        extra_filenames = []
        for f in extra_files:
            if f.filename:
                fname = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                extra_filenames.append(fname)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM approvals WHERE user_id=%s AND approval_type=%s AND status LIKE %s',
                       (user_data['id'], approval_type, 'pending%'))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '您已有一个待审批的申请'}), 400
        
        cursor.execute('''
            INSERT INTO approvals (user_id, approval_type, applicant_name, department, phone, seal_type, use_reason, file_name, partner_unit, seal_count, location, pdf_file, extra_files)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            user_data['id'], approval_type,
            request.form.get('applicant_name'), request.form.get('department'), request.form.get('phone'),
            request.form.get('seal_type'), request.form.get('use_reason'), request.form.get('file_name'),
            request.form.get('partner_unit', ''), int(request.form.get('seal_count', 1)),
            request.form.get('location', ''), pdf_filename, json.dumps(extra_filenames)
        ))
        conn.commit()
        return jsonify({'success': True, 'message': '审批提交成功'}), 201
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 获取我的审批 ====================
@app.route('/api/approvals/my', methods=['GET'])
@jwt_required()
def my_approvals():
    try:
        user_data = json.loads(get_jwt_identity())
        approval_type = request.args.get('type', 'external')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u1.real_name as level1_name, u2.real_name as level2_name, u3.real_name as level3_name
            FROM approvals a LEFT JOIN users u1 ON a.level1_reviewer = u1.id
            LEFT JOIN users u2 ON a.level2_reviewer = u2.id LEFT JOIN users u3 ON a.level3_reviewer = u3.id
            WHERE a.user_id=%s AND a.approval_type=%s ORDER BY a.created_at DESC
        ''', (user_data['id'], approval_type))
        approvals = cursor.fetchall()
        for a in approvals:
            if a['submit_time']: a['submit_time'] = a['submit_time'].strftime('%Y-%m-%d %H:%M:%S')
            if a['level1_time']: a['level1_time'] = a['level1_time'].strftime('%Y-%m-%d %H:%M:%S')
            if a['level2_time']: a['level2_time'] = a['level2_time'].strftime('%Y-%m-%d %H:%M:%S')
            if a['level3_time']: a['level3_time'] = a['level3_time'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'success': True, 'approvals': approvals}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 待审批列表 ====================
@app.route('/api/approvals/pending', methods=['GET'])
@jwt_required()
def pending_approvals():
    try:
        user_data = json.loads(get_jwt_identity())
        role = user_data['role']
        approval_type = request.args.get('type', 'external')
        
        conn = get_db()
        cursor = conn.cursor()
        
        if role == 'department_head':
            cursor.execute('SELECT a.*, u.real_name as submitter_name FROM approvals a JOIN users u ON a.user_id = u.id WHERE a.status=%s AND a.approval_type=%s ORDER BY a.created_at ASC', ('pending_level1', approval_type))
        elif role == 'vice_president':
            cursor.execute('SELECT a.*, u.real_name as submitter_name FROM approvals a JOIN users u ON a.user_id = u.id WHERE a.status=%s AND a.approval_type=%s ORDER BY a.created_at ASC', ('pending_level2', approval_type))
        elif role == 'president':
            cursor.execute('SELECT a.*, u.real_name as submitter_name FROM approvals a JOIN users u ON a.user_id = u.id WHERE a.status=%s AND a.approval_type=%s ORDER BY a.created_at ASC', ('pending_level3', approval_type))
        else:
            return jsonify({'success': True, 'approvals': []}), 200
        
        approvals = cursor.fetchall()
        for a in approvals:
            if a['submit_time']: a['submit_time'] = a['submit_time'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'success': True, 'approvals': approvals}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 已审批记录 ====================
@app.route('/api/approvals/reviewed', methods=['GET'])
@jwt_required()
def reviewed_approvals():
    try:
        user_data = json.loads(get_jwt_identity())
        user_id = user_data['id']
        approval_type = request.args.get('type', 'external')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT a.*, u.real_name as submitter_name FROM approvals a JOIN users u ON a.user_id = u.id WHERE (a.level1_reviewer=%s OR a.level2_reviewer=%s OR a.level3_reviewer=%s) AND a.approval_type=%s AND a.status NOT LIKE %s ORDER BY a.created_at DESC',
                       (user_id, user_id, user_id, approval_type, 'pending%'))
        approvals = cursor.fetchall()
        for a in approvals:
            if a['submit_time']: a['submit_time'] = a['submit_time'].strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({'success': True, 'approvals': approvals}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 一级审批 ====================
@app.route('/api/approvals/<int:aid>/review-level1', methods=['PUT'])
@jwt_required()
def review_level1(aid):
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'department_head':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        data = request.get_json()
        result = data.get('result')
        comment = data.get('comment', '')
        
        if result == 'rejected' and not comment:
            return jsonify({'success': False, 'message': '驳回必须填写备注'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        if result == 'rejected':
            cursor.execute('UPDATE approvals SET status=%s, level1_reviewer=%s, level1_comment=%s, level1_result=%s, level1_time=NOW() WHERE id=%s AND status=%s',
                           ('rejected', user_data['id'], comment, 'rejected', aid, 'pending_level1'))
        else:
            cursor.execute('UPDATE approvals SET status=%s, level1_reviewer=%s, level1_comment=%s, level1_result=%s, level1_time=NOW() WHERE id=%s AND status=%s',
                           ('pending_level2', user_data['id'], comment, 'approved', aid, 'pending_level1'))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '审批不存在或已处理'}), 404
        conn.commit()
        return jsonify({'success': True, 'message': '操作成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 二级审批 ====================
@app.route('/api/approvals/<int:aid>/review-level2', methods=['PUT'])
@jwt_required()
def review_level2(aid):
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'vice_president':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        data = request.get_json()
        result = data.get('result')
        comment = data.get('comment', '')
        risk = data.get('risk', '低')
        
        if result == 'rejected' and not comment:
            return jsonify({'success': False, 'message': '驳回必须填写备注'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        if result == 'rejected':
            cursor.execute('UPDATE approvals SET status=%s, level2_reviewer=%s, level2_comment=%s, level2_result=%s, level2_risk=%s, level2_time=NOW() WHERE id=%s AND status=%s',
                           ('rejected', user_data['id'], comment, 'rejected', risk, aid, 'pending_level2'))
        elif result == 'forward':
            cursor.execute('UPDATE approvals SET status=%s, level2_reviewer=%s, level2_comment=%s, level2_result=%s, level2_risk=%s, level2_time=NOW(), level3_amount=%s, level3_risk_items=%s, level3_project_risk=%s WHERE id=%s AND status=%s',
                           ('pending_level3', user_data['id'], comment, 'forward', risk, data.get('amount', ''), data.get('risk_items', ''), data.get('project_risk', ''), aid, 'pending_level2'))
        elif result == 'approved':
            cursor.execute('UPDATE approvals SET status=%s, level2_reviewer=%s, level2_comment=%s, level2_result=%s, level2_risk=%s, level2_time=NOW() WHERE id=%s AND status=%s',
                           ('approved', user_data['id'], comment, 'approved', risk, aid, 'pending_level2'))
            # 删除已使用的文件
            cursor.execute('SELECT file_name FROM approvals WHERE id=%s', (aid,))
            row = cursor.fetchone()
            if row and row['file_name']:
                cursor.execute('DELETE FROM files WHERE file_name=%s', (row['file_name'],))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '审批不存在或已处理'}), 404
        conn.commit()
        return jsonify({'success': True, 'message': '操作成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ==================== 三级审批 ====================
@app.route('/api/approvals/<int:aid>/review-level3', methods=['PUT'])
@jwt_required()
def review_level3(aid):
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'president':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        data = request.get_json()
        result = data.get('result')
        comment = data.get('comment', '')
        
        if result == 'rejected' and not comment:
            return jsonify({'success': False, 'message': '驳回必须填写备注'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        status = 'approved' if result != 'rejected' else 'rejected'
        cursor.execute('UPDATE approvals SET status=%s, level3_reviewer=%s, level3_comment=%s, level3_result=%s, level3_time=NOW() WHERE id=%s AND status=%s',
                       (status, user_data['id'], comment, result, aid, 'pending_level3'))
        
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '审批不存在或已处理'}), 404
        
        # 批准后删除文件
        if status == 'approved':
            cursor.execute('SELECT file_name FROM approvals WHERE id=%s', (aid,))
            row = cursor.fetchone()
            if row and row['file_name']:
                cursor.execute('DELETE FROM files WHERE file_name=%s', (row['file_name'],))
        
        conn.commit()
        return jsonify({'success': True, 'message': '操作成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("  印章管理系统后端启动中...")
    print("=" * 50)
    init_database()
    print("\n📍 后端: http://localhost:5000")
    print("📍 前端: http://localhost:8080\n")
    app.run(debug=False, host='0.0.0.0', port=5000)