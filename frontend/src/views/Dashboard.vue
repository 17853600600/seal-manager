<template>
  <div class="dashboard">
    <!-- 顶部导航 -->
    <div class="header">
      <h2>印章管理系统</h2>
      <div class="user-info">
        <el-dropdown @command="handleUserCommand">
          <span class="user-name">
            {{ userInfo.realName || userInfo.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">编辑个人信息</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="main-container">
      <!-- 左侧菜单 -->
      <div class="sidebar">
        <el-menu :default-active="activeMenu" class="sidebar-menu" @select="handleMenuSelect">
          <el-menu-item index="organization">
            <el-icon><UserFilled /></el-icon>
            <span>组织成员</span>
          </el-menu-item>
          <el-menu-item index="approval">
            <el-icon><Document /></el-icon>
            <span>盖章审批</span>
          </el-menu-item>
        </el-menu>
        
        <div class="logout-btn">
          <el-button @click="handleLogout" type="danger" style="width: 100%">退出登录</el-button>
        </div>
      </div>
      
      <!-- 右侧内容区 -->
      <div class="content">
        <!-- 组织成员 -->
        <div v-if="activeMenu === 'organization'" class="section">
          <h3>组织成员 - {{ userInfo.organization }}</h3>
          <el-table :data="organizationMembers" style="width: 100%" border>
            <el-table-column prop="real_name" label="姓名" width="150" />
            <el-table-column prop="username" label="账号" width="150" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'primary'">
                  {{ scope.row.role === 'admin' ? '管理员' : '成员' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 盖章审批 -->
        <div v-else-if="activeMenu === 'approval'" class="section">
          <h3>盖章审批</h3>
          
          <el-tabs v-model="approvalTab">
            <!-- 提交审批 -->
            <el-tab-pane label="提交审批" name="submit">
              <div v-if="userInfo.role === 'member'">
                <el-form :model="approvalForm" :rules="approvalRules" ref="approvalFormRef" label-width="100px">
                  <el-form-item label="地点" prop="location">
                    <el-input v-model="approvalForm.location" placeholder="请输入用印地点" />
                  </el-form-item>
                  <el-form-item label="印章次数" prop="sealCount">
                    <el-input-number v-model="approvalForm.sealCount" :min="1" :max="10" />
                  </el-form-item>
                  <el-form-item label="材料" prop="material">
                    <el-input v-model="approvalForm.material" type="textarea" :rows="3" placeholder="请输入用印材料" />
                  </el-form-item>
                  <el-form-item label="印章类型" prop="sealType">
                    <el-input v-model="approvalForm.sealType" placeholder="请输入印章类型" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="submitApproval">提交审批</el-button>
                  </el-form-item>
                </el-form>
                
                <div v-if="myApprovals.length > 0" style="margin-top: 30px">
                  <h4>我的审批记录</h4>
                  <el-table :data="myApprovals" style="width: 100%" border>
                    <el-table-column prop="location" label="地点" />
                    <el-table-column prop="seal_count" label="次数" width="80" />
                    <el-table-column prop="seal_type" label="印章类型" />
                    <el-table-column prop="material" label="材料" />
                    <el-table-column prop="status" label="状态" width="120">
                      <template #default="scope">
                        <el-tag v-if="scope.row.status === 'pending'" type="warning">审批中</el-tag>
                        <el-tag v-else-if="scope.row.status === 'approved'" type="success">已通过</el-tag>
                        <el-tag v-else type="danger">已拒绝</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="submit_time" label="提交时间" width="160" />
                    <el-table-column label="操作" width="120">
                      <template #default="scope">
                        <el-button v-if="scope.row.status === 'approved'" size="small" @click="returnSeal">退回印章</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
              <div v-else>
                <el-alert title="管理员账户，请在审核审批标签页进行审批操作" type="info" :closable="false" />
              </div>
            </el-tab-pane>
            
            <!-- 审核审批（仅管理员可见） -->
            <el-tab-pane v-if="userInfo.role === 'admin'" label="审核审批" name="review">
              <h4>待审批列表</h4>
              <el-table :data="pendingApprovals" style="width: 100%" border>
                <el-table-column prop="submitter_name" label="提交人" width="120" />
                <el-table-column prop="location" label="地点" />
                <el-table-column prop="seal_count" label="次数" width="80" />
                <el-table-column prop="seal_type" label="印章类型" />
                <el-table-column prop="material" label="材料" />
                <el-table-column prop="submit_time" label="提交时间" width="160" />
                <el-table-column label="操作" width="180">
                  <template #default="scope">
                    <el-button type="success" size="small" @click="approveApproval(scope.row.id)">通过</el-button>
                    <el-button type="danger" size="small" @click="rejectApproval(scope.row.id)">拒绝</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- 编辑个人信息弹窗 -->
    <el-dialog v-model="profileDialogVisible" title="编辑个人信息" width="500px">
      <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="100px">
        <el-form-item label="姓名" prop="realName">
          <el-input v-model="profileForm.realName" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="出生日期" prop="birthDate">
          <el-date-picker v-model="profileForm.birthDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="身份证号" prop="idCard">
          <el-input v-model="profileForm.idCard" placeholder="请输入18位身份证号" maxlength="18" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="profileForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="组织">
          <el-input v-model="userInfo.organization" disabled />
        </el-form-item>
        <el-form-item label="角色">
          <el-tag :type="userInfo.role === 'admin' ? 'danger' : 'primary'">
            {{ userInfo.role === 'admin' ? '管理员' : '成员' }}
          </el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="profileDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const api = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  name: 'Dashboard',
  data() {
    return {
      userInfo: JSON.parse(localStorage.getItem('user') || '{}'),
      activeMenu: 'organization',
      approvalTab: 'submit',
      profileComplete: false,
      profileDialogVisible: false,
      profileForm: {
        realName: '',
        birthDate: '',
        idCard: '',
        gender: ''
      },
      profileRules: {
        realName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
        birthDate: [{ required: true, message: '请选择出生日期', trigger: 'change' }],
        idCard: [
          { required: true, message: '请输入身份证号', trigger: 'blur' },
          { pattern: /^\d{17}[\dXx]$/, message: '身份证号格式不正确', trigger: 'blur' }
        ],
        gender: [{ required: true, message: '请选择性别', trigger: 'change' }]
      },
      approvalForm: {
        location: '',
        sealCount: 1,
        material: '',
        sealType: ''
      },
      approvalRules: {
        location: [{ required: true, message: '请输入地点', trigger: 'blur' }],
        material: [{ required: true, message: '请输入材料', trigger: 'blur' }],
        sealType: [{ required: true, message: '请输入印章类型', trigger: 'blur' }]
      },
      organizationMembers: [],
      myApprovals: [],
      pendingApprovals: []
    }
  },
  created() {
    this.loadProfile()
  },
  methods: {
    async loadProfile() {
      try {
        const response = await api.get('/api/profile')
        if (response.data.success) {
          this.profileForm = {
            realName: response.data.profile.realName || '',
            birthDate: response.data.profile.birthDate || '',
            idCard: response.data.profile.idCard || '',
            gender: response.data.profile.gender || ''
          }
          this.profileComplete = response.data.profileComplete
        }
      } catch (error) {
        console.error('加载个人信息失败:', error)
      }
    },
    
    handleUserCommand(command) {
      if (command === 'profile') {
        this.profileDialogVisible = true
      } else if (command === 'logout') {
        this.handleLogout()
      }
    },
    
    handleMenuSelect(index) {
      if (!this.profileComplete) {
        ElMessage.warning('请先编辑个人信息（点击右上角用户名）')
        this.profileDialogVisible = true
        return
      }
      
      this.activeMenu = index
      
      if (index === 'organization') {
        this.loadOrganizationMembers()
      } else if (index === 'approval') {
        this.loadMyApprovals()
        if (this.userInfo.role === 'admin') {
          this.loadPendingApprovals()
        }
      }
    },
    
    async saveProfile() {
      try {
        await this.$refs.profileFormRef.validate()
        const response = await api.put('/api/profile', this.profileForm)
        if (response.data.success) {
          ElMessage.success('个人信息保存成功')
          this.profileComplete = true
          this.profileDialogVisible = false
          const user = JSON.parse(localStorage.getItem('user') || '{}')
          user.realName = this.profileForm.realName
          localStorage.setItem('user', JSON.stringify(user))
          this.userInfo.realName = this.profileForm.realName
        }
      } catch (error) {
        if (error.response?.data?.message) {
          ElMessage.error(error.response.data.message)
        }
      }
    },
    
    async loadOrganizationMembers() {
      try {
        const response = await api.get('/api/organization/members')
        if (response.data.success) {
          this.organizationMembers = response.data.members
        }
      } catch (error) {
        console.error('加载组织成员失败:', error)
      }
    },
    
    async submitApproval() {
      try {
        await this.$refs.approvalFormRef.validate()
        const response = await api.post('/api/approvals', this.approvalForm)
        if (response.data.success) {
          ElMessage.success('审批提交成功')
          this.approvalForm = { location: '', sealCount: 1, material: '', sealType: '' }
          this.loadMyApprovals()
        }
      } catch (error) {
        if (error.response?.data?.message) {
          ElMessage.error(error.response.data.message)
        }
      }
    },
    
    async loadMyApprovals() {
      try {
        const response = await api.get('/api/approvals/my')
        if (response.data.success) {
          this.myApprovals = response.data.approvals
        }
      } catch (error) {
        console.error('加载审批记录失败:', error)
      }
    },
    
    async loadPendingApprovals() {
      try {
        const response = await api.get('/api/approvals/pending')
        if (response.data.success) {
          this.pendingApprovals = response.data.approvals
        }
      } catch (error) {
        console.error('加载待审批列表失败:', error)
      }
    },
    
    async approveApproval(id) {
      try {
        await ElMessageBox.confirm('确定要通过此审批吗？', '确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        const response = await api.put(`/api/approvals/${id}/approve`)
        if (response.data.success) {
          ElMessage.success('审批已通过')
          this.loadPendingApprovals()
        }
      } catch (error) {
        if (error !== 'cancel' && error.response?.data?.message) {
          ElMessage.error(error.response.data.message)
        }
      }
    },
    
    async rejectApproval(id) {
      try {
        await ElMessageBox.confirm('确定要拒绝此审批吗？', '确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        const response = await api.put(`/api/approvals/${id}/reject`)
        if (response.data.success) {
          ElMessage.success('审批已拒绝')
          this.loadPendingApprovals()
        }
      } catch (error) {
        if (error !== 'cancel' && error.response?.data?.message) {
          ElMessage.error(error.response.data.message)
        }
      }
    },
    
    returnSeal() {
      ElMessage.info('退回印章功能暂未开放')
    },
    
    handleLogout() {
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        this.$router.push('/login')
        ElMessage.success('已退出登录')
      }).catch(() => {})
    }
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f0f2f5;
}

.header {
  background: white;
  padding: 0 20px;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header h2 {
  color: #333;
  font-size: 20px;
}

.user-name {
  cursor: pointer;
  font-size: 16px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 5px;
}

.main-container {
  display: flex;
  height: calc(100vh - 60px);
}

.sidebar {
  width: 200px;
  background: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.logout-btn {
  padding: 20px;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.section {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section h3 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409EFF;
  color: #333;
}

.section h4 {
  margin-bottom: 15px;
  color: #666;
}
</style>