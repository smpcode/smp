
<template>
  <div class="app-container">
    <section>
      <div class="filter-container">
        <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
          <el-form :inline="true" :model="filters">
            <el-form-item>
              <el-input
                v-model="filters.name"
                placeholder="角色名称"
                @keyup.enter.native="handleFilter"
              ></el-input>
            </el-form-item>

            <el-form-item>
              <el-input v-model="filters.role" placeholder="角色" @keyup.enter.native="handleFilter"></el-input>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                style="margin-left: 10px"
                @click="handleFilter"
                icon="search"
              >查询</el-button>
              <el-button
                class="filter-item"
                style="margin-left: 10px;"
                @click="handleCreate"
                type="primary"
                icon="edit"
              >添加</el-button>
              <!--
                <el-button class="filter-item" type="primary" icon="document" @click="handleDownload">导出</el-button>
              -->
            </el-form-item>
          </el-form>
        </el-col>
      </div>
      <!--表格-->
      <el-table :data="objects" highlight-current-row border fit element-loading-text="加载中" v-loading="listLoading">
        <el-table-column prop="id" label="#" width="90">
          <template slot-scope="scope">
            <span>{{scope.row.id}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="角色名称" width="200">
          <template slot-scope="scope">
            <span>{{scope.row.name}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="250">
          <template slot-scope="scope">
              <el-popover trigger="hover" placement="top">
              <p>编码: {{ scope.row.role }}</p>
              <p>介绍: {{ scope.row.desc }}</p>
              <div slot="reference" class="name-wrapper">
                <el-tag size="medium">{{ scope.row.role }}</el-tag>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="400" fixed="right">
          <template slot-scope="scope">
            <el-button type="info" size="mini" @click="handleRolePermissions(scope.row)">权限</el-button>
            <el-button type="info" size="small" @click="handleRoleMembers(scope.row)">成员</el-button>
            <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">更新</el-button>
            <el-button type="danger" size="mini" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!--分页显示-->
      <div v-show="!listLoading" class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page.sync="listQuery.page"
          :page-sizes="[10,20,30,50,100]"
          :page-size="listQuery.limit"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          style="float:right;"
        ></el-pagination>
      </div>
      <!--新增/编辑对话框-->
      <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
        <el-form
          class="small-space"
          :model="temp"
          :rules="temp_rules"
          ref="temp"
          label-position="left"
          label-width="85px"
          style="width: 400px; margin-left:50px;"
        >
          <el-form-item label="角色名称" prop="name">
            <el-input v-model="temp.name"></el-input>
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-input v-model="temp.role"></el-input>
          </el-form-item>
          <el-form-item label="角色描述" prop="desc">
            <el-input v-model="temp.desc"></el-input>
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
  getResourceListPage,
  createResource,
  updateResource,
  deleteResource
} from "../../api/archapi";

export default {
  data() {
    return {
      filters: {
        role: "",
        name: ""
      },
      listQuery: {
        page: 1,
        limit: 20,
        sort: "+id"
      },
      temp: {
        id: undefined,
        name: "",
        role: "",
        desc: ""
      },
      temp_rules: {
        role: [
          {
            required: true,
            message: "角色不能为空！",
            trigger: "blur"
          }
        ],
        name: [
          {
            required: true,
            message: "角色名称不能为空！",
            trigger: "blur"
          }
        ],
        desc: [
          {
            required: true,
            message: "描述不能为空！",
            trigger: "blur"
          }
        ]
      },
      listLoading: true,
      objects: [],
      total: null,
      dialogFormVisible: false,
      dialogStatus: false, // 用于控制创建或者更新
      textMap: {
        update: "编辑",
        create: "创建"
      }
    };
  },
  mounted() {
    this.getList();
  },
  methods: {
    getList() {
      this.listLoading = true;
      let param = {
        name__like: "%" + this.filters.name + "%",
        role__like: "%" + this.filters.role + "%",
        limit: this.listQuery.limit,
        page: this.listQuery.page,
        ordering: this.listQuery.sort
      };
      getResourceListPage("hrsystem", "role", param)
        .then(res => {
          this.objects = res.data.objects;
          this.total = res.data.meta.total;
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
      let param = {
        role: this.temp.role,
        name: this.temp.name,
        desc: this.temp.desc
      };
      createResource("hrsystem", "role", param)
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
      let param = {
        id: this.temp.id,
        role: this.temp.role,
        name: this.temp.name,
        desc: this.temp.desc
      };
      updateResource("hrsystem", "role", param)
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
      this.temp.role = row.role;
      this.temp.name = row.name;
      this.temp.desc = row.desc;
    },
    handleDelete(row) {
      console.log("handleDelete:", row.id, row.role);
      let param = {
        pk: row.id
      };
      deleteResource("hrsystem", "role", param)
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
      this.temp.name = "";
      this.temp.role = "";
      this.temp.desc = "";
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
    // 角色的用户列表
    handleRoleMembers(row) {
      this.$router.push({
        path: "/admin/role/users",
        query: {
          role_id: row.id,
          role_name: row.name
        }
      });
    },
    // 角色的权限列表
    handleRolePermissions(row) {
      let role = row.id;
      this.$store
        .dispatch("set_role_routes", {
          role
        })
        .then(() => {
          this.$router.push({
            path: "/admin/role/permissions",
            query: {
              role_id: role,
              role_name: row.name
            }
          });
        });
    }
  }
};
</script>
