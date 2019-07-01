<template>
<div class="app-container">
  <section>
    <el-col :span="12" style="padding-bottom: 0px;">
        <el-button type="primary" @click="addChildren">添加下级部门</el-button>
        <el-button type="info" @click="updateCurrent">修改选中部门</el-button>
        <el-button type="warning" @click="deleteCurrent">删除选中部门</el-button>
      <el-form style="margin:10px;">
        <el-form-item class="edit-form">
          <el-input v-model="filterText" placeholder="搜索" />
        </el-form-item>
        <el-form-item class="edit-form">
          <el-tree
            ref="deptTree"
            class="filter-tree"
            highlight-current
            :data="deptTree"
            :props="defaultProps"
            :default-expand-all="true"
            node-key="id"
            :expand-on-click-node="true"
            :filter-node-method="filterNode"
            @node-click="handleNodeClick"
          />
        </el-form-item>
      </el-form>

    </el-col>
    <el-col :span="12">
      
      <el-form ref="temp" class="small-space" :model="selectedNode" label-position="left" label-width="90px" style="margin: 15px;">
        <el-form-item label="部门名称" prop="deptName">
          <el-input v-model="selectedNode.name" :disabled="true" />
        </el-form-item>
        <el-form-item label="部门邮箱" prop="deptEmail">
          <el-input v-model="selectedNode.email" :disabled="true" />
        </el-form-item>
        <el-form-item label="部门负责人" prop="deptManager">
          <el-input v-model="selectedNode.manager.name" :disabled="true" />
        </el-form-item>
        <el-form-item label="部门属性" prop="deptFunction">
          <el-input v-model="selectedNode.function" :disabled="true" />
        </el-form-item>
      </el-form>
    </el-col>
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form ref="temp" class="small-space" :model="temp" :rules="temp_rules" label-position="left" label-width="90px" style="width: 350px; margin-left:30px;">
        <template v-if="temp.parentID !== ''">
          <el-form-item label="上级部门ID" prop="parentID">
            <el-input v-model="temp.parentID" :disabled="true" />
          </el-form-item>
          <el-form-item label="上级部门" prop="parentName">
            <el-input v-model="temp.parentName" :disabled="true" />
          </el-form-item>
        </template>
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="temp.name" />
        </el-form-item>
        <el-form-item label="部门负责人" prop="manager">
          <el-autocomplete v-model="temp.userName" class="inline-input" value-key="realname" :fetch-suggestions="queryUserSearch" placeholder="查找用户" @select="handleUserSelect" />
        </el-form-item>
        <el-form-item label="部门邮箱" prop="email">
          <el-input v-model="temp.email" />
        </el-form-item>
        <el-form-item label="部门属性" prop="function">
          <el-input v-model="temp.function" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button v-if="dialogStatus=='create'" type="primary" @click="doCreate">确 定</el-button>
        <el-button v-else type="primary" @click="doUpdate">确 定</el-button>
      </div>
    </el-dialog>
  </section>
</div>
</template>

<script>
import {
  createResource,
  updateResource,
  getResourceListPage,
  deleteResource,
  getDeptNodes
} from '../../api/hrsystem'

export default {
  data() {
    return {
      dialogFormVisible: false,
      dialogStatus: 'create',
      textMap: {
        update: '编辑',
        create: '创建'
      },
      deptTree: [],
      filterText: '',
      selectedNode: {
        id: '',
        name: '',
        email: '',
        function: '',
        manager: {},
        userName: '',
        hasChildren: false
      },
      temp: {
        parentID: '',
        parentName: '',
        name: '',
        email: '',
        manager: '',
        userName: '',
        function: ''
      },
      users: [],
      temp_rules: {
        name: [{
          required: true,
          message: '部门名称不能为空！',
          trigger: 'blur'
        }]
      },
      defaultProps: {
        children: 'children',
        label: 'name'
      }
    }
  },
  watch: {
    filterText(val) {
      this.$refs.deptTree.filter(val)
    }
  },
  mounted() {
    this.initDeptNodes()
  },
  methods: {
    initDeptNodes() {
      getDeptNodes().then(res => {
        this.deptTree = res
      }).catch(err => {
        console.log('getDeptNodes failed, error', err.toString())
        this.$notify({
          title: '初始化失败',
          message: '获取部门信息时报错',
          type: 'error',
          duration: 2000
        })
      })
      if (this.users.length === 0) {
        const userParam = {
          limit: 500 // 如果用户个数超过500需要进行调整
        }
        getResourceListPage('hrsystem', 'user', userParam).then(res => {
          this.users = res.objects
        }).catch(err => {
          console.log(err.toString())
          this.users = []
        })
      }
    },
    // 当前选中节点信息更新
    handleNodeClick(data) {
      this.selectedNode.id = data.id
      this.selectedNode.name = data.name
      this.selectedNode.manager = data.manager
      if (data.children && data.children.length > 0) {
        this.selectedNode.hasChildren = true
      }
      this.selectedNode.email = data.email
      this.selectedNode.function = data.function
    },
    filterNode(value, data) {
      if (!value) {
        return true
      }
      return data.name.indexOf(value) !== -1
    },
    queryUserSearch(queryString, cb) {
      const users = this.users
      const results = queryString ? users.filter(this.createUserFilter(queryString)) : users
      // 调用 callback 返回建议列表的数据
      cb(results)
    },
    createUserFilter(queryString) {
      return (user) => {
        return (user.realname.indexOf(queryString) !== -1)
      }
    },
    handleUserSelect(item) {
      this.temp.manager = item.id
      this.temp.userName = item.realname
    },
    checkSelected() {
      if (this.selectedNode.id === '') {
        this.$notify({
          title: '提醒',
          message: '请先选中部门后再执行操作',
          type: 'info',
          duration: 2000
        })
      }
    },
    addChildren() {
      // console.log("currentNodeKey=", this.selectedNode.id, this.selectedNode.name);
      this.checkSelected()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.temp.parentID = this.selectedNode.id
      this.temp.parentName = this.selectedNode.name
      this.temp.manager = ''
      this.temp.name = ''
      this.temp.email = ''
      this.temp.function = ''
    },
    updateCurrent() {
      this.checkSelected()
      this.dialogStatus = 'update'
      this.temp.parentID = ''
      this.temp.parentName = ''
      this.dialogFormVisible = true
      this.temp.name = this.selectedNode.name
      this.temp.email = this.selectedNode.email
      this.temp.function = this.selectedNode.function
      this.temp.manager = this.selectedNode.manager.id
      this.temp.userName = this.selectedNode.manager.name
    },
    deleteCurrent() {
      this.checkSelected()
      const param = {
        pk: this.selectedNode.id
      }
      deleteResource('hrsystem', 'dept', param).then(res => {
        this.initDeptNodes()
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
      }).catch(err => {
        console.log('deleteResource failed, error=', err.toString())
        this.$notify({
          title: '失败',
          message: '删除失败',
          type: 'error',
          duration: 2000
        })
      })
    },
    doCreate() {
      const param = {
        parent: this.temp.parentID,
        name: this.temp.name,
        email: this.temp.email,
        manager: this.temp.manager,
        'function': this.temp.function
      }
      createResource('hrsystem', 'dept', param).then(res => {
        this.$notify({
          title: '成功',
          message: '添加成功',
          type: 'success',
          duration: 2000
        })
        this.initDeptNodes()
        this.dialogFormVisible = false
      }).catch(err => {
        console.log('createResource failed, error=', err.toString())
        this.$notify({
          title: '失败',
          message: '添加失败, ' + err.toString(),
          type: 'error',
          duration: 2000
        })
      })
    },
    doUpdate() {
      const param = {
        id: this.selectedNode.id,
        name: this.temp.name,
        email: this.temp.email,
        manager: this.temp.manager,
        'function': this.temp.function
      }
      updateResource('hrsystem', 'dept', param).then(res => {
        this.$notify({
          title: '成功',
          message: '修改成功',
          type: 'success',
          duration: 2000
        })
        this.initDeptNodes()
        this.dialogFormVisible = false
      }).catch(err => {
        console.log('updateResource failed, error=', err.toString())
        this.$notify({
          title: '失败',
          message: '修改失败, ' + err.toString(),
          type: 'error',
          duration: 2000
        })
      })
    }
  }
}
</script>

<style>

</style>
