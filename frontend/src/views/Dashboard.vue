<template>
  <div class="dashboard">
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
      <div class="sidebar">
        <el-menu :default-active="activeMenu" class="sidebar-menu" @select="handleMenuSelect">
          <el-menu-item index="organization">
            <el-icon><UserFilled /></el-icon>
            <span>组织成员</span>
          </el-menu-item>
          
          <el-menu-item v-if="userInfo.role === 'member'" index="myApprovals">
            <el-icon><Document /></el-icon>
            <span>我的审批</span>
          </el-menu-item>
          
          <el-menu-item v-if="isReviewer" index="reviewApprovals">
            <el-icon><DocumentChecked /></el-icon>
            <span>审批列表</span>
          </el-menu-item>
          
          <el-menu-item v-if="userInfo.role === 'file_manager'" index="fileManage">
            <el-icon><FolderOpened /></el-icon>
            <span>文件管理</span>
          </el-menu-item>
        </el-menu>
        
        <div class="logout-btn">
          <el-button @click="handleLogout" type="danger" style="width: 100%">退出登录</el-button>
        </div>
      </div>
      
      <div class="content">
        <!-- 组织成员 -->
        <div v-if="activeMenu === 'organization'" class="section">
          <h3>组织成员</h3>
          <el-table :data="organizationMembers" style="width: 100%" border>
            <el-table-column prop="real_name" label="姓名" width="120" />
            <el-table-column prop="username" label="账号" width="120" />
            <el-table-column prop="department" label="部门" width="150" />
            <el-table-column prop="phone" label="电话" width="130" />
            <el-table-column prop="role" label="角色" width="140">
              <template #default="scope">
                <el-tag v-if="scope.row.role === 'president'" type="danger">总经理</el-tag>
                <el-tag v-else-if="scope.row.role === 'vice_president'" type="warning">分管副总</el-tag>
                <el-tag v-else-if="scope.row.role === 'department_head'" type="success">部门负责人</el-tag>
                <el-tag v-else-if="scope.row.role === 'file_manager'" type="info">文件管理员</el-tag>
                <el-tag v-else type="primary">成员</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- ==================== 文件管理（文件管理员） ==================== -->
        <div v-else-if="activeMenu === 'fileManage'" class="section">
          <h3>文件管理</h3>
          <el-form :model="fileForm" ref="fileFormRef" label-width="120px">
            <el-form-item label="文件名称" prop="file_name">
              <el-input v-model="fileForm.file_name" placeholder="请输入文件名称" />
            </el-form-item>
            <el-form-item label="文件类型" prop="file_type">
              <el-select v-model="fileForm.file_type" placeholder="请选择" style="width: 200px">
                <el-option label="对内" value="internal" />
                <el-option label="对外" value="external" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="addFile">添加文件</el-button>
            </el-form-item>
          </el-form>
          
          <h4 style="margin-top: 30px">文件列表</h4>
          <el-table :data="fileList" style="width: 100%" border>
            <el-table-column prop="file_name" label="文件名称" />
            <el-table-column prop="file_type" label="类型" width="100">
              <template #default="scope">
                <el-tag v-if="scope.row.file_type === 'external'" type="warning">对外</el-tag>
                <el-tag v-else type="success">对内</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="添加时间" width="160" />
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button type="danger" size="small" @click="deleteFile(scope.row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- ==================== 我的审批（成员） ==================== -->
        <div v-else-if="activeMenu === 'myApprovals'" class="section">
          <el-tabs v-model="myApprovalTab">
            <el-tab-pane label="对外用章申请" name="external">
              <h3>对外用章审批申请</h3>
              <el-form :model="approvalForm" :rules="approvalRules" ref="approvalFormRef" label-width="120px">
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
                
                <el-divider content-position="left">用印说明</el-divider>
                <el-form-item label="用印事由" prop="use_reason">
                  <el-input v-model="approvalForm.use_reason" type="textarea" :rows="3" placeholder="请详细说明用印事由" />
                </el-form-item>
                <el-form-item label="文件名称" prop="file_name">
                  <el-select v-model="approvalForm.file_name" placeholder="请选择文件" style="width: 100%" filterable>
                    <el-option v-for="f in externalFiles" :key="f.id" :label="f.file_name" :value="f.file_name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="合作单位">
                  <el-input v-model="approvalForm.partner_unit" placeholder="请输入合作单位（对外文件必填）" />
                  <span class="form-tip">（对外文件必填）</span>
                </el-form-item>
                
                <el-divider content-position="left">使用地点</el-divider>
                <el-form-item label="使用地点" prop="location">
                  <el-input v-model="approvalForm.location" placeholder="请如实填写使用地点" />
                </el-form-item>
                
                <el-divider content-position="left">附件上传</el-divider>
                <el-form-item label="PDF文件" prop="pdf_file">
                  <el-upload ref="pdfUpload" :auto-upload="false" :limit="1" accept=".pdf" :on-change="handlePdfChange" :on-remove="handlePdfRemove">
                    <el-button type="primary">选择PDF文件</el-button>
                  </el-upload>
                </el-form-item>
                <el-form-item label="附加材料">
                  <el-upload ref="extraUpload" :auto-upload="false" multiple accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.png" :on-change="handleExtraChange">
                    <el-button type="default">选择附加材料</el-button>
                  </el-upload>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="submitApproval('external')" :loading="submitting">提交审批</el-button>
                </el-form-item>
              </el-form>
              
              <h4 style="margin-top: 30px">对外审批记录</h4>
              <el-table :data="myExternalApprovals" style="width: 100%" border>
                <el-table-column prop="seal_type" label="印章" width="100" />
                <el-table-column prop="file_name" label="文件名称" />
                <el-table-column prop="seal_count" label="次数" width="60" />
                <el-table-column prop="location" label="地点" width="100" />
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag v-if="scope.row.status === 'pending_level1'" type="warning">一级审核</el-tag>
                    <el-tag v-else-if="scope.row.status === 'pending_level2'" type="warning">二级审核</el-tag>
                    <el-tag v-else-if="scope.row.status === 'pending_level3'" type="warning">三级审核</el-tag>
                    <el-tag v-else-if="scope.row.status === 'approved'" type="success">已通过</el-tag>
                    <el-tag v-else type="danger">已驳回</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="submit_time" label="提交时间" width="160" />
                <el-table-column label="驳回备注" width="200">
                  <template #default="scope">
                    <div v-if="scope.row.status === 'rejected'" style="color: #f56c6c;">
                      <p v-if="scope.row.level1_result === 'rejected'">一级: {{ scope.row.level1_comment }}</p>
                      <p v-if="scope.row.level2_result === 'rejected'">二级: {{ scope.row.level2_comment }}</p>
                      <p v-if="scope.row.level3_result === 'rejected'">三级: {{ scope.row.level3_comment }}</p>
                    </div>
                    <span v-else style="color: #999">-</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="公司内部用章" name="internal">
              <h3>公司内部用章申请</h3>
              <el-form :model="internalForm" :rules="internalRules" ref="internalFormRef" label-width="120px">
                <el-divider content-position="left">基础信息</el-divider>
                <el-form-item label="申请人姓名" prop="applicant_name">
                  <el-input v-model="internalForm.applicant_name" placeholder="请输入申请人姓名" />
                </el-form-item>
                <el-form-item label="所属部门" prop="department">
                  <el-input v-model="internalForm.department" placeholder="请输入所属部门" />
                </el-form-item>
                <el-form-item label="联系电话" prop="phone">
                  <el-input v-model="internalForm.phone" placeholder="请输入联系电话" />
                </el-form-item>
                
                <el-divider content-position="left">印章信息</el-divider>
                <el-form-item label="选择印章" prop="seal_type">
                  <el-select v-model="internalForm.seal_type" placeholder="请选择印章" style="width: 100%">
                    <el-option label="公章" value="公章" />
                    <el-option label="合同专用章" value="合同专用章" />
                    <el-option label="财务章" value="财务章" />
                  </el-select>
                </el-form-item>
                <el-form-item label="盖章次数" prop="seal_count">
                  <el-input-number v-model="internalForm.seal_count" :min="1" :max="100" />
                </el-form-item>
                
                <el-divider content-position="left">用印说明</el-divider>
                <el-form-item label="用印事由" prop="use_reason">
                  <el-input v-model="internalForm.use_reason" type="textarea" :rows="3" placeholder="请详细说明用印事由" />
                </el-form-item>
                <el-form-item label="文件名称" prop="file_name">
                  <el-select v-model="internalForm.file_name" placeholder="请选择文件" style="width: 100%" filterable>
                    <el-option v-for="f in internalFiles" :key="f.id" :label="f.file_name" :value="f.file_name" />
                  </el-select>
                </el-form-item>
                <el-form-item label="合作单位">
                  <el-input v-model="internalForm.partner_unit" placeholder="请输入合作单位（对外文件必填）" />
                  <span class="form-tip">（对外文件必填）</span>
                </el-form-item>
                
                <el-divider content-position="left">附件上传</el-divider>
                <el-form-item label="PDF文件">
                  <el-upload ref="internalPdfUpload" :auto-upload="false" :limit="1" accept=".pdf" :on-change="handleInternalPdfChange" :on-remove="handleInternalPdfRemove">
                    <el-button type="primary">选择PDF文件</el-button>
                  </el-upload>
                </el-form-item>
                <el-form-item label="附加材料">
                  <el-upload ref="internalExtraUpload" :auto-upload="false" multiple accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.png" :on-change="handleInternalExtraChange">
                    <el-button type="default">选择附加材料</el-button>
                  </el-upload>
                </el-form-item>
                
                <el-form-item>
                  <el-button type="primary" @click="submitApproval('internal')" :loading="submitting">提交审批</el-button>
                </el-form-item>
              </el-form>
              
              <h4 style="margin-top: 30px">内部审批记录</h4>
              <el-table :data="myInternalApprovals" style="width: 100%" border>
                <el-table-column prop="seal_type" label="印章" width="100" />
                <el-table-column prop="file_name" label="文件名称" />
                <el-table-column prop="seal_count" label="次数" width="60" />
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag v-if="scope.row.status === 'pending_level1'" type="warning">一级审核</el-tag>
                    <el-tag v-else-if="scope.row.status === 'pending_level2'" type="warning">二级审核</el-tag>
                    <el-tag v-else-if="scope.row.status === 'pending_level3'" type="warning">三级审核</el-tag>
                    <el-tag v-else-if="scope.row.status === 'approved'" type="success">已通过</el-tag>
                    <el-tag v-else type="danger">已驳回</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="submit_time" label="提交时间" width="160" />
                <el-table-column label="驳回备注" width="200">
                  <template #default="scope">
                    <div v-if="scope.row.status === 'rejected'" style="color: #f56c6c;">
                      <p v-if="scope.row.level1_result === 'rejected'">一级: {{ scope.row.level1_comment }}</p>
                      <p v-if="scope.row.level2_result === 'rejected'">二级: {{ scope.row.level2_comment }}</p>
                      <p v-if="scope.row.level3_result === 'rejected'">三级: {{ scope.row.level3_comment }}</p>
                    </div>
                    <span v-else style="color: #999">-</span>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <!-- ==================== 审批列表（审批人） ==================== -->
        <div v-else-if="activeMenu === 'reviewApprovals' && isReviewer" class="section">
          <el-tabs v-model="reviewTab" @tab-change="handleReviewTabChange">
            <el-tab-pane label="对外审批" name="external">
              <h3>待审核 - 对外审批</h3>
              <el-table :data="pendingExternal" style="width: 100%" border>
                <el-table-column label="类型" width="70"><template #default><el-tag type="warning">对外</el-tag></template></el-table-column>
                <el-table-column prop="submitter_name" label="申请人" width="100" />
                <el-table-column prop="department" label="部门" width="120" />
                <el-table-column prop="seal_type" label="印章" width="100" />
                <el-table-column prop="file_name" label="文件名称" width="150" />
                <el-table-column prop="seal_count" label="次数" width="60" />
                <el-table-column prop="location" label="地点" width="100" />
                <el-table-column prop="submit_time" label="提交时间" width="160" />
                <el-table-column label="操作" width="100">
                  <template #default="scope">
                    <el-button type="primary" size="small" @click="openReviewDialog(scope.row)">审核</el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <h4 style="margin-top: 30px">已审批 - 对外</h4>
              <el-table :data="reviewedExternal" style="width: 100%" border>
                <el-table-column label="类型" width="70"><template #default><el-tag type="warning">对外</el-tag></template></el-table-column>
                <el-table-column prop="submitter_name" label="申请人" width="100" />
                <el-table-column prop="file_name" label="文件名称" width="150" />
                <el-table-column prop="seal_type" label="印章" width="100" />
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag v-if="scope.row.status === 'approved'" type="success">已通过</el-tag>
                    <el-tag v-else type="danger">已驳回</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="submit_time" label="提交时间" width="160" />
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="公司内部审批" name="internal">
              <h3>待审核 - 公司内部审批</h3>
              <el-table :data="pendingInternal" style="width: 100%" border>
                <el-table-column label="类型" width="70"><template #default><el-tag type="success">内部</el-tag></template></el-table-column>
                <el-table-column prop="submitter_name" label="申请人" width="100" />
                <el-table-column prop="department" label="部门" width="120" />
                <el-table-column prop="seal_type" label="印章" width="100" />
                <el-table-column prop="file_name" label="文件名称" width="150" />
                <el-table-column prop="seal_count" label="次数" width="60" />
                <el-table-column prop="submit_time" label="提交时间" width="160" />
                <el-table-column label="操作" width="100">
                  <template #default="scope">
                    <el-button type="primary" size="small" @click="openReviewDialog(scope.row)">审核</el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <h4 style="margin-top: 30px">已审批 - 内部</h4>
              <el-table :data="reviewedInternal" style="width: 100%" border>
                <el-table-column label="类型" width="70"><template #default><el-tag type="success">内部</el-tag></template></el-table-column>
                <el-table-column prop="submitter_name" label="申请人" width="100" />
                <el-table-column prop="file_name" label="文件名称" width="150" />
                <el-table-column prop="seal_type" label="印章" width="100" />
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag v-if="scope.row.status === 'approved'" type="success">已通过</el-tag>
                    <el-tag v-else type="danger">已驳回</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="submit_time" label="提交时间" width="160" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- 编辑个人信息弹窗 -->
    <el-dialog v-model="profileDialogVisible" title="编辑个人信息" width="550px">
      <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="100px">
        <el-form-item label="姓名" prop="realName"><el-input v-model="profileForm.realName" /></el-form-item>
        <el-form-item label="出生日期" prop="birthDate"><el-date-picker v-model="profileForm.birthDate" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="身份证号" prop="idCard"><el-input v-model="profileForm.idCard" maxlength="18" /></el-form-item>
        <el-form-item label="性别" prop="gender"><el-radio-group v-model="profileForm.gender"><el-radio label="男">男</el-radio><el-radio label="女">女</el-radio></el-radio-group></el-form-item>
        <el-form-item label="部门" prop="department"><el-input v-model="profileForm.department" /></el-form-item>
        <el-form-item label="电话" prop="phone"><el-input v-model="profileForm.phone" /></el-form-item>
        <el-form-item label="角色"><el-tag :type="roleTagType">{{ userInfo.roleName }}</el-tag></el-form-item>
      </el-form>
      <template #footer><el-button @click="profileDialogVisible = false">取消</el-button><el-button type="primary" @click="saveProfile">保存</el-button></template>
    </el-dialog>

    <!-- 审核弹窗 -->
    <el-dialog v-model="reviewDialogVisible" :title="'审核 - ' + (currentReview?.file_name || '')" width="750px" :close-on-click-modal="false">
      <div v-if="currentReview">
        <el-descriptions title="申请人信息" :column="2" border>
          <el-descriptions-item label="申请人">{{ currentReview.applicant_name }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ currentReview.department }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ currentReview.phone }}</el-descriptions-item>
          <el-descriptions-item label="提交人">{{ currentReview.submitter_name }}</el-descriptions-item>
        </el-descriptions>
        <el-descriptions title="用印信息" :column="2" border style="margin-top: 20px">
          <el-descriptions-item label="印章类型">{{ currentReview.seal_type }}</el-descriptions-item>
          <el-descriptions-item label="盖章次数">{{ currentReview.seal_count }}</el-descriptions-item>
          <el-descriptions-item v-if="currentReview.location" label="使用地点">{{ currentReview.location }}</el-descriptions-item>
          <el-descriptions-item label="合作单位">{{ currentReview.partner_unit || '无' }}</el-descriptions-item>
          <el-descriptions-item label="文件名称" :span="2">{{ currentReview.file_name }}</el-descriptions-item>
          <el-descriptions-item label="用印事由" :span="2">{{ currentReview.use_reason }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="reviewLevel >= 2" style="margin-top: 20px">
          <strong>PDF文件：</strong>
          <a v-if="currentReview.pdf_file" :href="pdfUrl + currentReview.pdf_file" target="_blank" style="color: #409EFF;">{{ currentReview.pdf_file }}</a>
          <span v-else style="color: #999">未上传</span>
        </div>
        <div v-else style="margin-top: 20px">
          <strong>PDF文件：</strong>
          <span v-if="currentReview.pdf_file">{{ currentReview.pdf_file }}（无权查看内容）</span>
          <span v-else style="color: #999">未上传</span>
        </div>
        
        <!-- 一级审批 -->
        <div v-if="reviewLevel === 1">
          <el-divider content-position="left">一级审批 - 部门负责人审核</el-divider>
          <el-form label-width="100px">
            <el-form-item label="核查项">
              <el-checkbox-group v-model="level1Checks">
                <el-checkbox label="申请人信息正确" />
                <el-checkbox label="所属部门正确" />
                <el-checkbox label="联系电话正确" />
                <el-checkbox v-if="currentReview.approval_type === 'external'" label="外出地点正确" />
                <el-checkbox label="业务与用章对应" />
                <el-checkbox label="用章次数合理" />
                <el-checkbox label="印章类别正确" />
                <el-checkbox v-if="currentReview.approval_type === 'external'" label="批准外带用章" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="审批备注"><el-input v-model="reviewComment" type="textarea" :rows="3" placeholder="驳回必填备注" /></el-form-item>
            <el-form-item>
              <el-button type="success" @click="submitLevel1('approved')" :disabled="!canLevel1Approve">初审通过</el-button>
              <el-button type="danger" @click="submitLevel1('rejected')">驳回</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 二级审批 -->
        <div v-if="reviewLevel === 2">
          <el-divider content-position="left">二级审批 - 分管副总审核</el-divider>
          <el-form label-width="120px">
            <el-form-item label="核查项">
              <el-checkbox-group v-model="level2Checks">
                <el-checkbox label="PDF文件内容与业务匹配" />
                <el-checkbox label="用章符合公司印章管理制度" />
                <el-checkbox label="印章使用范围合规" />
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="风险评估"><el-select v-model="reviewRisk"><el-option label="低" value="低" /><el-option label="中" value="中" /><el-option label="高" value="高" /></el-select></el-form-item>
            <el-form-item label="审批备注"><el-input v-model="reviewComment" type="textarea" :rows="3" placeholder="驳回必填备注" /></el-form-item>
            <el-form-item v-if="currentReview.approval_type === 'external'">
              <el-button type="success" @click="openLevel3Dialog" :disabled="!canLevel2Approve">二审通过</el-button>
              <el-button type="danger" @click="submitLevel2('rejected')">驳回</el-button>
            </el-form-item>
            <el-form-item v-else>
              <el-button type="success" @click="submitLevel2('approved')" :disabled="!canLevel2Approve">直接批准</el-button>
              <el-button type="warning" @click="openLevel3Dialog" :disabled="!canLevel2Approve">转审总经理</el-button>
              <el-button type="danger" @click="submitLevel2('rejected')">驳回</el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 三级审批 -->
        <div v-if="reviewLevel === 3">
          <el-divider content-position="left">三级审批 - 总经理终审</el-divider>
          <div v-if="currentReview.level3_amount" style="background: #f5f7fa; padding: 15px; border-radius: 5px; margin-bottom: 20px">
            <p><strong>金额：</strong>{{ currentReview.level3_amount }}</p>
            <p><strong>风险条目：</strong>{{ currentReview.level3_risk_items }}</p>
            <p><strong>项目风险评估：</strong>{{ currentReview.level3_project_risk }}</p>
          </div>
          <el-form label-width="100px">
            <el-form-item label="审批选项">
              <el-checkbox-group v-model="level3Checks">
                <el-checkbox v-if="currentReview.approval_type === 'external'" label="批准外带">批准外带</el-checkbox>
                <el-checkbox label="批准用章">批准用章</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="审批备注"><el-input v-model="reviewComment" type="textarea" :rows="3" placeholder="驳回必填备注" /></el-form-item>
            <el-form-item>
              <el-button type="success" @click="submitLevel3('approved')" :disabled="!canLevel3Approve">审批通过</el-button>
              <el-button type="danger" @click="submitLevel3('rejected')">驳回</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-dialog>

    <!-- 二级转三级弹窗 -->
    <el-dialog v-model="level3DialogVisible" title="填写转审信息" width="500px">
      <el-form label-width="120px">
        <el-form-item label="金额"><el-input v-model="level3Info.amount" placeholder="请输入金额" /></el-form-item>
        <el-form-item label="风险条目"><el-input v-model="level3Info.riskItems" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="项目风险评估"><el-input v-model="level3Info.projectRisk" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="level3DialogVisible = false">取消</el-button><el-button type="primary" @click="confirmLevel2Forward">确认提交</el-button></template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const api = axios.create({ baseURL: 'http://localhost:5000', timeout: 30000 })
api.interceptors.request.use(c => { const t = localStorage.getItem('token'); if (t) c.headers.Authorization = `Bearer ${t}`; return c })
api.interceptors.response.use(r => r, e => { if (e.response?.status === 401) { localStorage.clear(); window.location.href = '/login' } return Promise.reject(e) })

export default {
  name: 'Dashboard',
  data() {
    return {
      userInfo: JSON.parse(localStorage.getItem('user') || '{}'),
      activeMenu: 'organization',
      myApprovalTab: 'external',
      reviewTab: 'external',
      profileComplete: false,
      profileDialogVisible: false,
      reviewDialogVisible: false,
      level3DialogVisible: false,
      submitting: false,
      pdfUrl: 'http://localhost:5000/api/download/',
      
      profileForm: { realName: '', birthDate: '', idCard: '', gender: '', department: '', phone: '' },
      profileRules: {
        realName: [{ required: true }], birthDate: [{ required: true }],
        idCard: [{ required: true }, { pattern: /^\d{17}[\dXx]$/, message: '格式不正确' }],
        gender: [{ required: true }], department: [{ required: true }],
        phone: [{ required: true }, { pattern: /^1[3-9]\d{9}$/, message: '格式不正确' }]
      },
      
      fileForm: { file_name: '', file_type: 'external' },
      fileList: [],
      externalFiles: [],
      internalFiles: [],
      
      approvalForm: { applicant_name: '', department: '', phone: '', seal_type: '', seal_count: 1, use_reason: '', file_name: '', partner_unit: '', location: '', pdf_file: null, extra_files: [] },
      approvalRules: {
        applicant_name: [{ required: true }], department: [{ required: true }], phone: [{ required: true }],
        seal_type: [{ required: true }], use_reason: [{ required: true }], file_name: [{ required: true, message: '请选择文件' }], location: [{ required: true }]
      },
      
      internalForm: { applicant_name: '', department: '', phone: '', seal_type: '', seal_count: 1, use_reason: '', file_name: '', partner_unit: '', pdf_file: null, extra_files: [] },
      internalRules: {
        applicant_name: [{ required: true }], department: [{ required: true }], phone: [{ required: true }],
        seal_type: [{ required: true }], use_reason: [{ required: true }], file_name: [{ required: true, message: '请选择文件' }]
      },
      
      organizationMembers: [],
      myExternalApprovals: [], myInternalApprovals: [],
      pendingExternal: [], pendingInternal: [],
      reviewedExternal: [], reviewedInternal: [],
      
      currentReview: null, reviewLevel: 1, reviewComment: '', reviewRisk: '低',
      level1Checks: [], level2Checks: [], level3Checks: [],
      level3Info: { amount: '', riskItems: '', projectRisk: '' }
    }
  },
  computed: {
    isReviewer() { return ['department_head', 'vice_president', 'president'].includes(this.userInfo.role) },
    roleTagType() {
      const t = { 'member': 'primary', 'department_head': 'success', 'vice_president': 'warning', 'president': 'danger', 'file_manager': 'info' }
      return t[this.userInfo.role] || 'info'
    },
    canLevel1Approve() {
      const req = this.currentReview?.approval_type === 'external' ? 8 : 6
      return this.level1Checks.length >= req
    },
    canLevel2Approve() { return this.level2Checks.length >= 3 },
    canLevel3Approve() {
      if (this.currentReview?.approval_type === 'external') return this.level3Checks.length >= 2
      return this.level3Checks.includes('批准用章')
    }
  },
  created() { this.loadProfile(); this.loadOrganizationMembers(); if (this.userInfo.role === 'file_manager') this.loadFiles() },
  methods: {
    async loadProfile() {
      const r = await api.get('/api/profile')
      if (r.data.success) {
        const p = r.data.profile
        this.profileForm = { realName: p.realName || '', birthDate: p.birthDate || '', idCard: p.idCard || '', gender: p.gender || '', department: p.department || '', phone: p.phone || '' }
        this.profileComplete = r.data.profileComplete
      }
    },
    handleUserCommand(c) { if (c === 'profile') this.profileDialogVisible = true; else if (c === 'logout') this.handleLogout() },
    handleMenuSelect(i) {
      if (!this.profileComplete) { ElMessage.warning('请先编辑个人信息'); this.profileDialogVisible = true; return }
      this.activeMenu = i
      if (i === 'organization') this.loadOrganizationMembers()
      else if (i === 'myApprovals') { this.loadMyApprovals('external'); this.loadMyApprovals('internal'); this.loadFiles() }
      else if (i === 'reviewApprovals') this.handleReviewTabChange('external')
      else if (i === 'fileManage') this.loadFiles()
    },
    handleReviewTabChange(t) { this.reviewTab = t; this.loadPendingApprovals(t); this.loadReviewedApprovals(t) },
    async saveProfile() {
      await this.$refs.profileFormRef.validate()
      const r = await api.put('/api/profile', this.profileForm)
      if (r.data.success) { ElMessage.success('保存成功'); this.profileComplete = true; this.profileDialogVisible = false }
    },
    async loadOrganizationMembers() { const r = await api.get('/api/organization/members'); if (r.data.success) this.organizationMembers = r.data.members },
    
    // 文件管理
    async loadFiles() {
      const r = await api.get('/api/files')
      if (r.data.success) {
        this.fileList = r.data.files
        this.externalFiles = r.data.files.filter(f => f.file_type === 'external')
        this.internalFiles = r.data.files.filter(f => f.file_type === 'internal')
      }
    },
    async addFile() {
      if (!this.fileForm.file_name.trim()) { ElMessage.warning('请输入文件名称'); return }
      const r = await api.post('/api/files', this.fileForm)
      if (r.data.success) { ElMessage.success('添加成功'); this.fileForm.file_name = ''; this.loadFiles() }
    },
    async deleteFile(id) {
      await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
      const r = await api.delete(`/api/files/${id}`)
      if (r.data.success) { ElMessage.success('已删除'); this.loadFiles() }
    },
    
    handlePdfChange(f) { this.approvalForm.pdf_file = f.raw },
    handlePdfRemove() { this.approvalForm.pdf_file = null },
    handleExtraChange(f, fl) { this.approvalForm.extra_files = fl.map(x => x.raw) },
    handleInternalPdfChange(f) { this.internalForm.pdf_file = f.raw },
    handleInternalPdfRemove() { this.internalForm.pdf_file = null },
    handleInternalExtraChange(f, fl) { this.internalForm.extra_files = fl.map(x => x.raw) },
    
    async submitApproval(type) {
      const formRef = type === 'external' ? 'approvalFormRef' : 'internalFormRef'
      const form = type === 'external' ? this.approvalForm : this.internalForm
      await this.$refs[formRef].validate()
      this.submitting = true
      const fd = new FormData()
      Object.keys(form).forEach(k => { if (k !== 'pdf_file' && k !== 'extra_files') fd.append(k, form[k]) })
      fd.append('approval_type', type)
      if (form.pdf_file) fd.append('pdf_file', form.pdf_file)
      if (form.extra_files) form.extra_files.forEach(f => fd.append('extra_files', f))
      const r = await api.post('/api/approvals', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      if (r.data.success) { ElMessage.success('提交成功'); this.loadMyApprovals(type) }
      this.submitting = false
    },
    
    async loadMyApprovals(type) {
      const r = await api.get('/api/approvals/my?type=' + type)
      if (r.data.success) { if (type === 'external') this.myExternalApprovals = r.data.approvals; else this.myInternalApprovals = r.data.approvals }
    },
    async loadPendingApprovals(type) {
      const r = await api.get('/api/approvals/pending?type=' + type)
      if (r.data.success) { if (type === 'external') this.pendingExternal = r.data.approvals; else this.pendingInternal = r.data.approvals }
    },
    async loadReviewedApprovals(type) {
      const r = await api.get('/api/approvals/reviewed?type=' + type)
      if (r.data.success) { if (type === 'external') this.reviewedExternal = r.data.approvals; else this.reviewedInternal = r.data.approvals }
    },
    
    openReviewDialog(row) {
      this.currentReview = row; this.reviewComment = ''; this.reviewRisk = '低'
      this.level1Checks = []; this.level2Checks = []; this.level3Checks = []
      if (row.status === 'pending_level1') this.reviewLevel = 1
      else if (row.status === 'pending_level2') this.reviewLevel = 2
      else this.reviewLevel = 3
      this.reviewDialogVisible = true
    },
    
    async submitLevel1(r) {
      if (r === 'rejected' && !this.reviewComment) { ElMessage.warning('驳回必须填备注'); return }
      await api.put(`/api/approvals/${this.currentReview.id}/review-level1`, { result: r, comment: this.reviewComment })
      ElMessage.success(r === 'approved' ? '通过' : '已驳回'); this.reviewDialogVisible = false; this.loadPendingApprovals(this.reviewTab)
    },
    async submitLevel2(r) {
      if (r === 'rejected' && !this.reviewComment) { ElMessage.warning('驳回必须填备注'); return }
      await api.put(`/api/approvals/${this.currentReview.id}/review-level2`, { result: r, comment: this.reviewComment, risk: this.reviewRisk })
      ElMessage.success(r === 'rejected' ? '已驳回' : '通过'); this.reviewDialogVisible = false; this.loadPendingApprovals(this.reviewTab)
    },
    openLevel3Dialog() { this.level3Info = { amount: '', riskItems: '', projectRisk: '' }; this.level3DialogVisible = true },
    async confirmLevel2Forward() {
      this.level3DialogVisible = false
      await api.put(`/api/approvals/${this.currentReview.id}/review-level2`, {
        result: 'forward', comment: this.reviewComment, risk: this.reviewRisk,
        amount: this.level3Info.amount, risk_items: this.level3Info.riskItems, project_risk: this.level3Info.projectRisk
      })
      ElMessage.success('已转审总经理'); this.reviewDialogVisible = false; this.loadPendingApprovals(this.reviewTab)
    },
    async submitLevel3(r) {
      if (r === 'rejected' && !this.reviewComment) { ElMessage.warning('驳回必须填备注'); return }
      await api.put(`/api/approvals/${this.currentReview.id}/review-level3`, { result: r, comment: this.reviewComment })
      ElMessage.success(r === 'rejected' ? '已驳回' : '通过'); this.reviewDialogVisible = false; this.loadPendingApprovals(this.reviewTab)
    },
    
    handleLogout() {
      ElMessageBox.confirm('确定退出？', '提示', { type: 'warning' }).then(() => { localStorage.clear(); this.$router.push('/login') }).catch(() => {})
    }
  }
}
</script>

<style scoped>
.dashboard { min-height: 100vh; background: #f0f2f5; }
.header { background: white; padding: 0 20px; height: 60px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.header h2 { color: #333; font-size: 20px; }
.user-info { display: flex; align-items: center; gap: 15px; }
.user-name { cursor: pointer; font-size: 16px; display: flex; align-items: center; gap: 5px; }
.main-container { display: flex; height: calc(100vh - 60px); }
.sidebar { width: 200px; background: white; display: flex; flex-direction: column; }
.sidebar-menu { flex: 1; border-right: none; }
.logout-btn { padding: 20px; }
.content { flex: 1; padding: 20px; overflow-y: auto; }
.section { background: white; padding: 30px; border-radius: 8px; }
.section h3 { margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #409EFF; }
.section h4 { margin: 20px 0 10px; color: #666; }
.form-tip { color: #999; font-size: 12px; margin-left: 5px; }
</style>