<template>
  <div class="dashboard">
    <!-- 顶部导航 -->
    <div class="header">
      <h2>印章管理系统</h2>
      <div class="user-info">
        <span class="role-tag">
          <el-tag :type="roleTagType">{{ userInfo.roleName }}</el-tag>
        </span>
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
          
          <!-- 成员看到的是我的审批 -->
          <el-menu-item v-if="userInfo.role === 'member'" index="myApprovals">
            <el-icon><Document /></el-icon>
            <span>我的审批</span>
          </el-menu-item>
          
          <!-- 审批人看到的是对外审批 -->
          <el-menu-item v-if="isReviewer" index="externalApproval">
            <el-icon><DocumentChecked /></el-icon>
            <span>对外审批</span>
          </el-menu-item>
          
          <!-- 公司内部审批（暂不做） -->
          <el-menu-item index="internalApproval">
            <el-icon><OfficeBuilding /></el-icon>
            <span>公司内部审批</span>
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
          <h3>组织成员</h3>
          <el-table :data="organizationMembers" style="width: 100%" border>
            <el-table-column prop="real_name" label="姓名" width="120" />
            <el-table-column prop="username" label="账号" width="120" />
            <el-table-column prop="department" label="部门" width="150" />
            <el-table-column prop="phone" label="电话" width="130" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.role === 'president'" type="danger">总经理</el-tag>
                <el-tag v-else-if="scope.row.role === 'vice_president'" type="warning">分管副总</el-tag>
                <el-tag v-else-if="scope.row.role === 'department_head'" type="success">部门负责人</el-tag>
                <el-tag v-else type="primary">成员</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 我的审批（成员） -->
        <div v-else-if="activeMenu === 'myApprovals'" class="section">
          <h3>提交审批申请</h3>
          
          <el-form :model="approvalForm" :rules="approvalRules" ref="approvalFormRef" label-width="120px">
            <!-- 基础信息 -->
            <el-divider content-position="left">基础信息</el-divider>
            <el-form-item label="申请人姓名" prop="applicant_name">
              <el-input v-model="approvalForm.applicant_name" placeholder="请输入申请人姓名" />
            </el-form-item>
            <el-form-item label="所属部门" prop="department">
              <el-input v-model="approvalForm.department" placeholder="请输入所属部门" />
            </el-form-item>
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="approvalForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
            
            <!-- 印章信息 -->
            <el-divider content-position="left">印章信息</el-divider>
            <el-form-item label="选择印章" prop="seal_type">
              <el-select v-model="approvalForm.seal_type" placeholder="请选择印章" style="width: 100%">
                <el-option label="公章" value="公章" />
                <el-option label="合同专用章" value="合同专用章" />
                <el-option label="财务章" value="财务章" />
              </el-select>
            </el-form-item>
            <el-form-item label="盖章次数" prop="seal_count">
              <el-input-number v-model="approvalForm.seal_count" :min="1" :max="100" />
            </el-form-item>
            
            <!-- 用印说明 -->
            <el-divider content-position="left">用印说明</el-divider>
            <el-form-item label="用印事由" prop="use_reason">
              <el-input v-model="approvalForm.use_reason" type="textarea" :rows="3" placeholder="请详细说明用印事由" />
            </el-form-item>
            <el-form-item label="文件名称" prop="file_name">
              <el-input v-model="approvalForm.file_name" placeholder="请输入文件名称" />
            </el-form-item>
            <el-form-item label="合作单位">
              <el-input v-model="approvalForm.partner_unit" placeholder="请输入合作单位（对外文件必填）" />
              <span class="form-tip">（对外文件必填）</span>
            </el-form-item>
            
            <!-- 使用地点 -->
            <el-divider content-position="left">使用地点</el-divider>
            <el-form-item label="使用地点" prop="location">
              <el-input v-model="approvalForm.location" placeholder="请如实填写使用地点" />
            </el-form-item>
            
            <!-- 附件 -->
            <el-divider content-position="left">附件上传</el-divider>
            <el-form-item label="PDF文件" prop="pdf_file">
              <el-upload
                ref="pdfUpload"
                :auto-upload="false"
                :limit="1"
                accept=".pdf"
                :on-change="handlePdfChange"
                :on-remove="handlePdfRemove"
              >
                <el-button type="primary">选择PDF文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">请上传完整的PDF文件</div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item label="附加材料">
              <el-upload
                ref="extraUpload"
                :auto-upload="false"
                multiple
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.png"
                :on-change="handleExtraChange"
              >
                <el-button type="default">选择附加材料</el-button>
                <template #tip>
                  <div class="el-upload__tip">报价单、审批备忘录、项目立项资料等（按需上传）</div>
                </template>
              </el-upload>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitApproval" :loading="submitting">提交审批</el-button>
            </el-form-item>
          </el-form>
          
          <!-- 审批记录 -->
          <div style="margin-top: 40px">
            <h4>我的审批记录</h4>
            <el-table :data="myApprovals" style="width: 100%" border>
              <el-table-column prop="seal_type" label="印章类型" width="100" />
              <el-table-column prop="file_name" label="文件名称" />
              <el-table-column prop="seal_count" label="次数" width="60" />
              <el-table-column prop="location" label="地点" width="100" />
              <el-table-column label="状态" width="100">
                <template #default="scope">
                  <el-tag v-if="scope.row.status === 'pending_level1'" type="warning">一级审核中</el-tag>
                  <el-tag v-else-if="scope.row.status === 'pending_level2'" type="warning">二级审核中</el-tag>
                  <el-tag v-else-if="scope.row.status === 'pending_level3'" type="warning">三级审核中</el-tag>
                  <el-tag v-else-if="scope.row.status === 'approved'" type="success">已通过</el-tag>
                  <el-tag v-else type="danger">已驳回</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="submit_time" label="提交时间" width="160" />
            </el-table>
          </div>
        </div>
        
        <!-- 对外审批（审批人） -->
        <div v-else-if="activeMenu === 'externalApproval' && isReviewer" class="section">
            <h3>对外审批 - 待审核列表</h3>
            <el-table :data="pendingApprovals" style="width: 100%" border>
                <el-table-column prop="submitter_name" label="申请人" width="100" />
                <el-table-column prop="applicant_name" label="姓名" width="80" />
                <el-table-column prop="department" label="部门" width="120" />
                <el-table-column prop="phone" label="电话" width="120" />
                <el-table-column prop="seal_type" label="印章" width="100" />
                <el-table-column prop="file_name" label="文件名称" width="150" />
                <el-table-column prop="seal_count" label="次数" width="60" />
                <el-table-column prop="location" label="地点" width="100" />
                <el-table-column prop="submit_time" label="提交时间" width="160" />
                <el-table-column label="操作" width="180" fixed="right">
                    <template #default="scope">
                        <el-button type="primary" size="small" @click="openReviewDialog(scope.row)">审核</el-button>
                    </template>
                </el-table-column>
            </el-table>
    
            <!-- 已审批记录 -->
            <h3 style="margin-top: 40px">已审批记录</h3>
            <el-table :data="reviewedApprovals" style="width: 100%" border>
                <el-table-column prop="submitter_name" label="申请人" width="100" />
                <el-table-column prop="file_name" label="文件名称" width="150" />
                <el-table-column prop="seal_type" label="印章" width="100" />
                <el-table-column prop="seal_count" label="次数" width="60" />
                <el-table-column label="状态" width="100">
                    <template #default="scope">
                        <el-tag v-if="scope.row.status === 'approved'" type="success">已通过</el-tag>
                        <el-tag v-else type="danger">已驳回</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="submit_time" label="提交时间" width="160" />
            </el-table>
        </div>
        
        <!-- 公司内部审批（暂不做） -->
        <div v-else-if="activeMenu === 'internalApproval'" class="section">
          <el-empty description="公司内部审批功能开发中，敬请期待...">
            <el-button type="primary" disabled>功能开发中</el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 编辑个人信息弹窗 -->
    <el-dialog v-model="profileDialogVisible" title="编辑个人信息" width="550px">
      <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="100px">
        <el-form-item label="姓名" prop="realName">
          <el-input v-model="profileForm.realName" />
        </el-form-item>
        <el-form-item label="出生日期" prop="birthDate">
          <el-date-picker v-model="profileForm.birthDate" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="身份证号" prop="idCard">
          <el-input v-model="profileForm.idCard" maxlength="18" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="profileForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="部门" prop="department">
          <el-input v-model="profileForm.department" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="profileForm.phone" />
        </el-form-item>
        <el-form-item label="角色">
          <el-tag :type="roleTagType">{{ userInfo.roleName }}</el-tag>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="profileDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <!-- 审核弹窗 -->
    <el-dialog v-model="reviewDialogVisible" :title="reviewTitle" width="700px" :close-on-click-modal="false">
      <div v-if="currentReview">
        <!-- 申请人信息 -->
        <el-descriptions title="申请人信息" :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="申请人">{{ currentReview.applicant_name }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ currentReview.department }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ currentReview.phone }}</el-descriptions-item>
          <el-descriptions-item label="提交人账号">{{ currentReview.submitter_name }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- 用印信息 -->
        <el-descriptions title="用印信息" :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="印章类型">{{ currentReview.seal_type }}</el-descriptions-item>
          <el-descriptions-item label="盖章次数">{{ currentReview.seal_count }}</el-descriptions-item>
          <el-descriptions-item label="使用地点">{{ currentReview.location }}</el-descriptions-item>
          <el-descriptions-item label="合作单位">{{ currentReview.partner_unit || '无' }}</el-descriptions-item>
          <el-descriptions-item label="文件名称" :span="2">{{ currentReview.file_name }}</el-descriptions-item>
          <el-descriptions-item label="用印事由" :span="2">{{ currentReview.use_reason }}</el-descriptions-item>
        </el-descriptions>
        
        <!-- PDF文件 -->
        <div style="margin-bottom: 20px">
            <strong>PDF文件：</strong>
            <a v-if="currentReview.pdf_file" :href="'http://localhost:5000/api/download/' + currentReview.pdf_file" target="_blank" style="color: #409EFF; text-decoration: underline;">
                {{ currentReview.pdf_file }}
            </a>
            <span v-else style="color: #999">未上传</span>
        </div>
        
        <!-- 附加材料 -->
        <div style="margin-bottom: 20px">
          <strong>附加材料：</strong>
          <span v-if="currentReview.extra_files && currentReview.extra_files !== '[]'">{{ currentReview.extra_files }}</span>
          <span v-else style="color: #999">无</span>
        </div>
        
        <!-- 一级审批：部门负责人 -->
        <div v-if="reviewLevel === 1">
          <el-divider content-position="left">一级审批 - 部门负责人审核</el-divider>
          <el-form label-width="100px">
            <el-form-item label="核查项">
              <el-checkbox-group v-model="level1Checks">
                <el-checkbox label="申请人信息正确" />
                <el-checkbox label="所属部门正确" />
                <el-checkbox label="联系电话正确" />
                <el-checkbox label="外出地点正确" />
                <el-checkbox label="业务与用章对应" />
                <el-checkbox label="用章次数合理" />
                <el-checkbox label="印章类别正确" />
                <el-checkbox label="批准外带用章" />
                <el-checkbox label="PDF文件与业务匹配" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="审批备注" prop="comment">
              <el-input v-model="reviewComment" type="textarea" :rows="3" placeholder="请输入审批备注" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="submitLevel1Review('approved')">初审通过</el-button>
              <el-button type="danger" @click="submitLevel1Review('rejected')">驳回</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 二级审批：分管副总 -->
        <div v-if="reviewLevel === 2">
          <el-divider content-position="left">二级审批 - 分管副总审核</el-divider>
          <el-form label-width="120px">
            <el-form-item label="风险评估">
              <el-select v-model="reviewRisk" placeholder="请选择风险等级" style="width: 200px">
                <el-option label="低" value="低" />
                <el-option label="中" value="中" />
                <el-option label="高" value="高" />
              </el-select>
            </el-form-item>
            <el-form-item label="审批备注">
              <el-input v-model="reviewComment" type="textarea" :rows="3" placeholder="请输入审批备注" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="submitLevel2Review('approved')">直接批准</el-button>
              <el-button type="warning" @click="submitLevel2Review('forward')">转审总经理</el-button>
              <el-button type="danger" @click="submitLevel2Review('rejected')">驳回</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 三级审批：总经理 -->
        <div v-if="reviewLevel === 3">
          <el-divider content-position="left">三级审批 - 总经理终审</el-divider>
          <el-form label-width="100px">
            <el-form-item label="审批备注">
              <el-input v-model="reviewComment" type="textarea" :rows="3" placeholder="请输入审批备注" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="submitLevel3Review('approved')">批准</el-button>
              <el-button type="danger" @click="submitLevel3Review('rejected')">驳回</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const api = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 30000
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
      profileComplete: false,
      profileDialogVisible: false,
      reviewDialogVisible: false,
      submitting: false,
      
      profileForm: {
        realName: '',
        birthDate: '',
        idCard: '',
        gender: '',
        department: '',
        phone: ''
      },
      profileRules: {
        realName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
        birthDate: [{ required: true, message: '请选择出生日期', trigger: 'change' }],
        idCard: [
          { required: true, message: '请输入身份证号', trigger: 'blur' },
          { pattern: /^\d{17}[\dXx]$/, message: '身份证号格式不正确', trigger: 'blur' }
        ],
        gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
        department: [{ required: true, message: '请输入部门', trigger: 'blur' }],
        phone: [
          { required: true, message: '请输入电话', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
        ]
      },
      
      approvalForm: {
        applicant_name: '',
        department: '',
        phone: '',
        seal_type: '',
        seal_count: 1,
        use_reason: '',
        file_name: '',
        partner_unit: '',
        location: '',
        pdf_file: null,
        extra_files: []
      },
      approvalRules: {
        applicant_name: [{ required: true, message: '请输入申请人姓名', trigger: 'blur' }],
        department: [{ required: true, message: '请输入所属部门', trigger: 'blur' }],
        phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
        seal_type: [{ required: true, message: '请选择印章', trigger: 'change' }],
        use_reason: [{ required: true, message: '请输入用印事由', trigger: 'blur' }],
        file_name: [{ required: true, message: '请输入文件名称', trigger: 'blur' }],
        location: [{ required: true, message: '请填写使用地点', trigger: 'blur' }]
      },
      
      organizationMembers: [],
      myApprovals: [],
      pendingApprovals: [],
      reviewedApprovals: [],
      
      currentReview: null,
      reviewLevel: 1,
      reviewComment: '',
      reviewRisk: '低',
      level1Checks: []
    }
  },
  computed: {
    isReviewer() {
      return ['department_head', 'vice_president', 'president'].includes(this.userInfo.role)
    },
    roleTagType() {
      const types = {
        'member': 'primary',
        'department_head': 'success',
        'vice_president': 'warning',
        'president': 'danger'
      }
      return types[this.userInfo.role] || 'info'
    },
    reviewTitle() {
      return `审核 - ${this.currentReview?.file_name || ''}`
    }
  },
  created() {
    this.loadProfile()
    this.loadOrganizationMembers()
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
            gender: response.data.profile.gender || '',
            department: response.data.profile.department || '',
            phone: response.data.profile.phone || ''
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
      } else if (index === 'myApprovals') {
        this.loadMyApprovals()
      } else if (index === 'externalApproval') {
        this.loadPendingApprovals()
        this.loadReviewedApprovals()
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
          user.department = this.profileForm.department
          user.phone = this.profileForm.phone
          localStorage.setItem('user', JSON.stringify(user))
          this.userInfo = user
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
    
    handlePdfChange(file) {
      this.approvalForm.pdf_file = file.raw
    },
    
    handlePdfRemove() {
      this.approvalForm.pdf_file = null
    },
    
    handleExtraChange(file, fileList) {
      this.approvalForm.extra_files = fileList.map(f => f.raw)
    },
    
    async submitApproval() {
      try {
        await this.$refs.approvalFormRef.validate()
        
        if (!this.approvalForm.pdf_file) {
          ElMessage.warning('请上传PDF文件')
          return
        }
        
        this.submitting = true
        
        const formData = new FormData()
        formData.append('applicant_name', this.approvalForm.applicant_name)
        formData.append('department', this.approvalForm.department)
        formData.append('phone', this.approvalForm.phone)
        formData.append('seal_type', this.approvalForm.seal_type)
        formData.append('seal_count', this.approvalForm.seal_count)
        formData.append('use_reason', this.approvalForm.use_reason)
        formData.append('file_name', this.approvalForm.file_name)
        formData.append('partner_unit', this.approvalForm.partner_unit)
        formData.append('location', this.approvalForm.location)
        formData.append('pdf_file', this.approvalForm.pdf_file)
        
        if (this.approvalForm.extra_files.length > 0) {
          this.approvalForm.extra_files.forEach(file => {
            formData.append('extra_files', file)
          })
        }
        
        const response = await api.post('/api/approvals', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        
        if (response.data.success) {
          ElMessage.success('审批提交成功')
          this.resetApprovalForm()
          this.loadMyApprovals()
        }
      } catch (error) {
        if (error.response?.data?.message) {
          ElMessage.error(error.response.data.message)
        }
      } finally {
        this.submitting = false
      }
    },
    
    resetApprovalForm() {
      this.approvalForm = {
        applicant_name: '',
        department: '',
        phone: '',
        seal_type: '',
        seal_count: 1,
        use_reason: '',
        file_name: '',
        partner_unit: '',
        location: '',
        pdf_file: null,
        extra_files: []
      }
      this.$refs.pdfUpload?.clearFiles()
      this.$refs.extraUpload?.clearFiles()
      this.$refs.approvalFormRef?.resetFields()
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

    async loadReviewedApprovals() {
      try {
        const response = await api.get('/api/approvals/reviewed')
        if (response.data.success) {
          this.reviewedApprovals = response.data.approvals
        }
      } catch (error) {
        console.error('加载已审批记录失败:', error)
      }
    },


    
    openReviewDialog(row) {
      this.currentReview = row
      this.reviewComment = ''
      this.reviewRisk = '低'
      this.level1Checks = []
      
      if (row.status === 'pending_level1') {
        this.reviewLevel = 1
      } else if (row.status === 'pending_level2') {
        this.reviewLevel = 2
      } else if (row.status === 'pending_level3') {
        this.reviewLevel = 3
      }
      
      this.reviewDialogVisible = true
    },
    
    async submitLevel1Review(result) {
      try {
        const response = await api.put(`/api/approvals/${this.currentReview.id}/review-level1`, {
          result: result,
          comment: this.reviewComment
        })
        if (response.data.success) {
          ElMessage.success(result === 'approved' ? '初审通过' : '已驳回')
          this.reviewDialogVisible = false
          this.loadPendingApprovals()
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
    },
    
    async submitLevel2Review(result) {
      try {
        const response = await api.put(`/api/approvals/${this.currentReview.id}/review-level2`, {
          result: result,
          comment: this.reviewComment,
          risk: this.reviewRisk
        })
        if (response.data.success) {
          const msgs = { 'approved': '已批准', 'rejected': '已驳回', 'forward': '已转审总经理' }
          ElMessage.success(msgs[result])
          this.reviewDialogVisible = false
          this.loadPendingApprovals()
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
    },
    
    async submitLevel3Review(result) {
      try {
        const response = await api.put(`/api/approvals/${this.currentReview.id}/review-level3`, {
          result: result,
          comment: this.reviewComment
        })
        if (response.data.success) {
          ElMessage.success(result === 'approved' ? '已批准' : '已驳回')
          this.reviewDialogVisible = false
          this.loadPendingApprovals()
        }
      } catch (error) {
        ElMessage.error(error.response?.data?.message || '操作失败')
      }
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

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.role-tag {
  font-size: 14px;
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

.form-tip {
  color: #999;
  font-size: 12px;
  margin-left: 5px;
}
</style>