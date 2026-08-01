<template>
  <div class="register-container">
    <div class="register-box">
      <h2>用户注册</h2>
      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="registerForm.realName" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-input v-model="registerForm.department" placeholder="请输入所属部门" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="registerForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="成员（申请人）" value="member" />
            <el-option label="部门负责人" value="department_head" />
            <el-option label="分管副总" value="vice_president" />
            <el-option label="总经理" value="president" />
            <el-option label="文件管理员" value="file_manager" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" style="width: 100%">注册</el-button>
        </el-form-item>
        <div class="login-link">
          已有账号？<router-link to="/login">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000'
})

export default {
  name: 'Register',
  data() {
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        username: '',
        password: '',
        confirmPassword: '',
        realName: '',
        department: '',
        phone: '',
        role: 'member'
      },
      rules: {
        username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ],
        realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
        department: [{ required: true, message: '请输入所属部门', trigger: 'blur' }],
        phone: [
          { required: true, message: '请输入联系电话', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
        ],
        role: [{ required: true, message: '请选择角色', trigger: 'change' }]
      }
    }
  },
  methods: {
    async handleRegister() {
      const valid = await this.$refs.registerFormRef.validate()
      if (!valid) return
      
      try {
        const response = await api.post('/api/register', this.registerForm)
        if (response.data.success) {
          this.$message.success('注册成功，请登录')
          this.$router.push('/login')
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || '注册失败')
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-box {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 480px;
}

.register-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.login-link a {
  color: #409EFF;
  text-decoration: none;
}
</style>