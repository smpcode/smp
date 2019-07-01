<template>
  <div class="app-container">
    <div class="filter-container">
      <el-col :span="24" class="toolbar">
        <el-form :inline="true" :model="filters">
          <el-form-item>
            <el-input
              v-model="filters.account"
              placeholder="账户"
              @keyup.enter.native="handleFilter"
            />
          </el-form-item>

          <el-form-item>
            <el-input
              v-model="filters.realname"
              placeholder="姓名"
              @keyup.enter.native="handleFilter"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              style="margin-left: 10px"
              icon="search"
              @click="handleFilter"
            >查询</el-button>
            <el-button
              class="filter-item"
              style="margin-left: 10px;"
              type="primary"
              icon="edit"
              @click="handleCreate"
            >添加</el-button>
            <!--
                <el-button class="filter-item" type="primary" icon="document" @click="handleDownload">导出</el-button>
            -->
          </el-form-item>
        </el-form>
      </el-col>
    </div>

    <!--表格-->
    <el-table
      v-loading="listLoading"
      :data="objects"
      highlight-current-row
      border
      fit
      element-loading-text="加载中"
    >
      <el-table-column prop="id" label="#" width="90">
        <template scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="account" label="账户" width="250">
        <template scope="scope">
          <span>{{ scope.row.account }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="realname" label="姓名" width="200">
        <template scope="scope">
          <el-popover trigger="hover" placement="top">
            <p>姓名: {{ scope.row.realname }}</p>
            <p>邮箱: {{ scope.row.email }}</p>
            <p>手机: {{ scope.row.mobil }}</p>
            <div slot="reference" class="name-wrapper">
              <el-tag size="medium">{{ scope.row.realname }}</el-tag>
            </div>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column prop="deptName" label="部门" width="250">
        <template scope="scope">
          <span>{{ scope.row.dept.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="300" fixed="right">
        <template scope="scope">
          <el-button type="info" size="mini" @click="showUserRoles(scope.row)">角色</el-button>
          <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button type="danger" size="mini" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />

    <!--新增/编辑用户对话框-->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="temp"
        class="small-space"
        :model="temp"
        :rules="temp_rules"
        label-position="left"
        label-width="85px"
        style="width: 400px; margin-left:50px;"
      >
        <el-form-item label="账户" prop="account">
          <el-input v-model="temp.account"/>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="temp.email"/>
        </el-form-item>
        <el-form-item label="手机" prop="mobile">
          <el-input v-model="temp.mobile"/>
        </el-form-item>
        <el-form-item label="部门" prop="deptName">
          <el-autocomplete
            v-model="temp.deptName"
            class="inline-input"
            value-key="name"
            :fetch-suggestions="queryDeptSearch"
            placeholder="查找部门"
            @select="handleDeptSelect"
          />
        </el-form-item>
        <el-form-item label="真实姓名" prop="realname">
          <el-input v-model="temp.realname"/>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="temp.password" type="password"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button v-if="dialogStatus=='create'" type="primary" @click="doCreate">确 定</el-button>
        <el-button v-else type="primary" @click="doUpdate">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog title="查看角色" :visible.sync="roleDialogFormVisible">
      <el-table
        v-loading="listRolesLoading"
        :data="userRoles"
        highlight-current-row
        style="width: 90%;"
      >
        <el-table-column prop="role" label="角色" min-width="250">
          <template scope="scope">
            <span>{{ scope.row.role.role }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色名称" min-width="250">
          <template scope="scope">
            <span>{{ scope.row.role.desc }}</span>
          </template>
        </el-table-column>
      </el-table>
      <div slot="footer" class="dialog-footer">
        <el-button @click="roleDialogFormVisible = false">关 闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  getResourceListPage,
  createResource,
  updateResource,
  deleteResource
} from "../../api/hrsystem";
import CryptoJS from "crypto-js";
import Pagination from "@/components/Pagination";

export default {
  components: { Pagination },
  data() {
    return {
      filters: {
        account: "",
        realname: ""
      },
      sortOptions: [
        {
          label: "按ID升序列",
          key: "+id"
        },
        {
          label: "按ID降序",
          key: "-id"
        }
      ],
      listQuery: {
        page: 1,
        limit: 20,
        sort: "+id"
      },
      temp: {
        id: undefined,
        account: "",
        realname: "",
        deptName: "",
        deptID: "",
        email: "",
        password: ""
      },
      temp_rules: {
        account: [
          {
            required: true,
            message: "账户不能为空！",
            trigger: "blur"
          }
        ],
        realname: [
          {
            required: true,
            message: "姓名不能为空！",
            trigger: "blur"
          }
        ],
        email: [
          {
            required: true,
            message: "邮箱不能为空！",
            trigger: "blur"
          },
          {
            type: "email",
            message: "邮箱格式不正确！",
            trigger: "blur"
          }
        ],
        password: [
          {
            trigger: "blur",
            validator: (rule, value, callback) => {
              if (this.dialogStatus === "create") {
                if (value === "") {
                  callback(new Error("密码不能为空"));
                }
              } else {
                callback();
              }
            }
          }
        ]
      },
      userRoles: [],
      listLoading: true,
      listRolesLoading: false,
      objects: [],
      depts: [],
      total: 0,
      dialogFormVisible: false,
      roleDialogFormVisible: false,
      dialogStatus: false, // 用于控制创建或者更新
      textMap: {
        update: "编辑",
        create: "创建"
      },
      props: {
        deptProps: {
          value: "name",
          label: "name"
        }
      }
    };
  },
  mounted() {
    this.getList();
  },
  methods: {
    getList() {
      this.listLoading = true;
      // 部门信息仅初始化一次即可
      if (this.depts.length === 0) {
        const deptParam = {
          limit: 100 // 如果部门个数超过100需要进行调整
        };
        getResourceListPage("hrsystem", "dept", deptParam)
          .then(res => {
            this.depts = res.objects;
          })
          .catch(err => {
            console.log(err.toString());
            this.depts = [];
          });
      }
      const param = {
        limit: this.listQuery.limit,
        page: this.listQuery.page,
        ordering: this.listQuery.sort
      };
      if (this.filters.account.length > 0) {
        param.account__like = "%" + this.filters.account + "%";
      }
      if (this.filters.realname.length > 0) {
        param.realname__like = "%" + this.filters.realname + "%";
      }
      getResourceListPage("hrsystem", "user", param)
        .then(res => {
          this.objects = res.objects;
          this.total = res.meta.total;
          this.listLoading = false;
        })
        .catch(err => {
          console.log(err.toString());
          this.objects = [];
          this.total = 0;
          this.listLoading = false;
        });
    },
    doCreate() {
      const param = {
        account: this.temp.account,
        realname: this.temp.realname,
        email: this.temp.email,
        mobile: this.temp.mobile,
        dept: this.temp.deptID,
        password: CryptoJS.HmacSHA256(
          this.temp.password,
          this.temp.account
        ).toString()
      };
      createResource("hrsystem", "user", param)
        .then(res => {
          this.$notify({
            title: "成功",
            message: "添加成功",
            type: "success",
            duration: 2000
          });
          this.getList();
          this.dialogFormVisible = false;
        })
        .catch(err => {
          console.log("createResource failed, error=", err.toString());
          this.$notify({
            title: "失败",
            message: "添加失败, " + err.toString(),
            type: "error",
            duration: 2000
          });
        });
    },
    doUpdate() {
      const param = {
        id: this.temp.id,
        account: this.temp.account,
        realname: this.temp.realname,
        dept: this.temp.deptID,
        mobile: this.temp.mobile,
        email: this.temp.email
      };
      const newPassword = this.temp.password || "";
      if (newPassword.length > 0) {
        param.password = CryptoJS.HmacSHA256(
          newPassword,
          this.temp.account
        ).toString();
      }
      updateResource("hrsystem", "user", param)
        .then(res => {
          this.$notify({
            title: "成功",
            message: "修改成功",
            type: "success",
            duration: 2000
          });
          // 刷新表格
          this.getList();
          this.dialogFormVisible = false;
        })
        .catch(err => {
          console.log("updateResource failed, error=", err.toString());
          this.$notify({
            title: "失败",
            message: "修改失败, " + err.toString(),
            type: "error",
            duration: 2000
          });
        });
    },
    handleFilter() {
      this.getList();
    },
    handleUpdate(row) {
      this.dialogStatus = "update";
      this.dialogFormVisible = true;
      this.temp.id = row.id;
      this.temp.account = row.account;
      this.temp.realname = row.realname;
      this.temp.email = row.email;
      this.temp.mobile = row.mobile;
      this.temp.deptName = row.dept.name;
      this.temp.deptID = row.dept.id;
    },
    handleDelete(row) {
      console.log("handleDelete:", row.id, row.account);
      const param = {
        pk: row.id
      };
      deleteResource("hrsystem", "user", param)
        .then(res => {
          // 页面上删除
          const index = this.objects.indexOf(row);
          this.objects.splice(index, 1);
          this.$notify({
            title: "成功",
            message: "删除成功",
            type: "success",
            duration: 2000
          });
        })
        .catch(err => {
          console.log("deleteResource failed, error=", err.toString());
          this.$notify({
            title: "失败",
            message: "删除失败",
            type: "error",
            duration: 2000
          });
        });
    },
    handleCreate() {
      this.dialogStatus = "create";
      this.dialogFormVisible = true;
      this.temp.id = "";
      this.temp.account = "";
      this.temp.realname = "";
      this.temp.email = "";
      this.temp.password = "";
      this.temp.deptName = "";
      this.temp.mobile = "";
      this.temp.deptID = "";
    },
    handleDownload() {},
    // 处理页码变更事件，参数为页码数
    handleSizeChange(size) {
      this.listQuery.limit = size;
      this.getList();
    },
    handleCurrentChange(currentPage) {
      this.listQuery.page = currentPage;
      this.getList();
    },
    queryDeptSearch(queryString, cb) {
      const depts = this.depts;
      const results = queryString
        ? depts.filter(this.createDeptFilter(queryString))
        : depts;
      // 调用 callback 返回建议列表的数据
      cb(results);
    },
    createDeptFilter(queryString) {
      return dept => {
        return dept.name.indexOf(queryString) !== -1;
      };
    },
    handleDeptSelect(item) {
      this.temp.deptID = item.id;
      this.temp.deptName = item.name;
    },
    showUserRoles(item) {
      this.roleDialogFormVisible = true;
      this.listRolesLoading = true;
      const param = {
        user__eq: item.id
      };
      getResourceListPage("hrsystem", "user_role", param)
        .then(res => {
          this.userRoles = res.objects;
          this.listRolesLoading = false;
        })
        .catch(err => {
          console.log(err.toString());
          this.userRoles = [];
        });
    }
  }
};
</script>
