from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pymysql
import bcrypt
from datetime import timedelta
import json

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 配置直接写在代码里
app.config['SECRET_KEY'] = 'seal-management-secret-key-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'wcr_20070430',
    'database': 'seal_management',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def init_database():
    """初始化数据库"""
    try:
        # 创建数据库连接（不指定数据库）
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='wcr_20070430',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS seal_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 数据库创建成功")
        
        # 创建表
        conn = get_db()
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                real_name VARCHAR(50),
                birth_date DATE,
                id_card VARCHAR(18),
                gender VARCHAR(10),
                organization VARCHAR(50),
                role ENUM('member', 'admin') DEFAULT 'member',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 审批表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS approvals (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                submit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                location VARCHAR(255) NOT NULL,
                seal_count INT DEFAULT 1,
                material VARCHAR(255) NOT NULL,
                seal_type VARCHAR(100) NOT NULL,
                status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                admin_id INT,
                approve_time DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (admin_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        conn.commit()
        print("✅ 数据表创建成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ========== 注册接口 ==========
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        real_name = data.get('realName', '').strip()
        organization = data.get('organization', '').strip()
        role = data.get('role', 'member')
        
        if not all([username, password, real_name, organization]):
            return jsonify({'success': False, 'message': '请填写所有必填字段'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查用户名
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 加密密码
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # 插入用户
        cursor.execute(
            'INSERT INTO users (username, password, real_name, organization, role) VALUES (%s, %s, %s, %s, %s)',
            (username, hashed.decode('utf-8'), real_name, organization, role)
        )
        conn.commit()
        
        return jsonify({'success': True, 'message': '注册成功'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 登录接口 ==========
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        # 生成token
        token_data = {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'organization': user['organization']
        }
        token = create_access_token(identity=json.dumps(token_data))
        
        # 返回用户信息
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'realName': user['real_name'] or '',
            'role': user['role'],
            'organization': user['organization'],
            'birthDate': str(user['birth_date']) if user['birth_date'] else '',
            'idCard': user['id_card'] or '',
            'gender': user['gender'] or ''
        }
        
        return jsonify({'success': True, 'token': token, 'user': user_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 获取个人信息 ==========
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_data = json.loads(get_jwt_identity())
        user_id = user_data['id']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT real_name, birth_date, id_card, gender, organization, role FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        profile_complete = all([user['real_name'], user['birth_date'], user['id_card'], user['gender']])
        
        return jsonify({
            'success': True,
            'profile': {
                'realName': user['real_name'] or '',
                'birthDate': str(user['birth_date']) if user['birth_date'] else '',
                'idCard': user['id_card'] or '',
                'gender': user['gender'] or '',
                'organization': user['organization'],
                'role': user['role']
            },
            'profileComplete': profile_complete
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 更新个人信息 ==========
@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_data = json.loads(get_jwt_identity())
        user_id = user_data['id']
        data = request.get_json()
        
        real_name = data.get('realName', '').strip()
        birth_date = data.get('birthDate', '').strip()
        id_card = data.get('idCard', '').strip()
        gender = data.get('gender', '').strip()
        
        if not all([real_name, birth_date, id_card, gender]):
            return jsonify({'success': False, 'message': '请填写所有个人信息'}), 400
        
        if len(id_card) != 18:
            return jsonify({'success': False, 'message': '身份证号必须为18位'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET real_name=%s, birth_date=%s, id_card=%s, gender=%s WHERE id=%s',
            (real_name, birth_date, id_card, gender, user_id)
        )
        conn.commit()
        
        return jsonify({'success': True, 'message': '个人信息更新成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 获取组织成员 ==========
@app.route('/api/organization/members', methods=['GET'])
@jwt_required()
def get_members():
    try:
        user_data = json.loads(get_jwt_identity())
        organization = user_data['organization']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, real_name, role, organization FROM users WHERE organization=%s ORDER BY role, real_name',
            (organization,)
        )
        members = cursor.fetchall()
        
        return jsonify({'success': True, 'members': members}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 提交审批 ==========
@app.route('/api/approvals', methods=['POST'])
@jwt_required()
def submit_approval():
    try:
        user_data = json.loads(get_jwt_identity())
        user_id = user_data['id']
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否已有待审批
        cursor.execute('SELECT id FROM approvals WHERE user_id=%s AND status="pending"', (user_id,))
        if cursor.fetchone():
            return jsonify({'success': False, 'message': '您已有一个待审批的申请'}), 400
        
        # 插入审批
        cursor.execute(
            'INSERT INTO approvals (user_id, location, seal_count, material, seal_type) VALUES (%s, %s, %s, %s, %s)',
            (user_id, data.get('location'), data.get('sealCount', 1), data.get('material'), data.get('sealType'))
        )
        conn.commit()
        
        return jsonify({'success': True, 'message': '审批提交成功'}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 获取我的审批 ==========
@app.route('/api/approvals/my', methods=['GET'])
@jwt_required()
def my_approvals():
    try:
        user_data = json.loads(get_jwt_identity())
        user_id = user_data['id']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM approvals WHERE user_id=%s ORDER BY created_at DESC', (user_id,))
        approvals = cursor.fetchall()
        
        # 格式化时间
        for a in approvals:
            if a['submit_time']:
                a['submit_time'] = a['submit_time'].strftime('%Y-%m-%d %H:%M:%S')
            if a['approve_time']:
                a['approve_time'] = a['approve_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'approvals': approvals}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 获取待审批（管理员） ==========
@app.route('/api/approvals/pending', methods=['GET'])
@jwt_required()
def pending_approvals():
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'admin':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, u.real_name as submitter_name
            FROM approvals a JOIN users u ON a.user_id = u.id
            WHERE a.status = 'pending'
            ORDER BY a.created_at ASC
        ''')
        approvals = cursor.fetchall()
        
        for a in approvals:
            if a['submit_time']:
                a['submit_time'] = a['submit_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'approvals': approvals}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 通过审批 ==========
@app.route('/api/approvals/<int:aid>/approve', methods=['PUT'])
@jwt_required()
def approve(aid):
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'admin':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE approvals SET status="approved", admin_id=%s, approve_time=NOW() WHERE id=%s AND status="pending"',
            (user_data['id'], aid)
        )
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '审批不存在或已处理'}), 404
        
        conn.commit()
        return jsonify({'success': True, 'message': '审批已通过'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ========== 拒绝审批 ==========
@app.route('/api/approvals/<int:aid>/reject', methods=['PUT'])
@jwt_required()
def reject(aid):
    try:
        user_data = json.loads(get_jwt_identity())
        if user_data['role'] != 'admin':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE approvals SET status="rejected", admin_id=%s, approve_time=NOW() WHERE id=%s AND status="pending"',
            (user_data['id'], aid)
        )
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '审批不存在或已处理'}), 404
        
        conn.commit()
        return jsonify({'success': True, 'message': '审批已拒绝'}), 200
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
    print("\n后端地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务器\n")
    app.run(debug=False, host='0.0.0.0', port=5000)