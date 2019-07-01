<template>
  <div class="app-container">
    <section>
      <div class="filter-container">
        <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
          <el-form :inline="true" :model="filters">
            <el-form-item>
              <el-input v-model="filters.key" placeholder="字典编码" @keyup.enter.native="handleFilter"></el-input>
            </el-form-item>

            <el-form-item>
              <el-input
                v-model="filters.desc"
                placeholder="字典描述"
                @keyup.enter.native="handleFilter"
              ></el-input>
            </el-form-item>

            <el-form-item>
              <el-input
                v-model="filters.value"
                placeholder="字典值"
                @keyup.enter.native="handleFilter"
              ></el-input>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                style="margin-left: 10px"
                @click="handleFilter"
                icon="search"
              >查询</el-button>
              <el-button
                v-if="hasPermission('create')"
                class="filter-item"
                style="margin-left: 10px;"
                @click="handleCreate"
                type="primary"
                icon="edit"
              >添加</el-button>
            </el-form-item>
          </el-form>
        </el-col>
      </div>
      <!--表格-->
      <el-table :data="objects" highlight-current-row border fit element-loading-text="加载中" v-loading="listLoading">
        <el-table-column prop="id" label="#" width="100">
          <template scope="scope">
            <span>{{scope.row.id}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="key" label="字典编码" width="250">
          <template scope="scope">
            <span>{{scope.row.key}}</span>
          </template>
        </el-table-column>
        <el-table-column prop="desc" label="字典描述" min-width="250">
          <template scope="scope">
            <span>{{scope.row.desc}}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="200">
          <template scope="scope">
            <el-button
              v-if="hasPermission('update')"
              type="info"
              size="mini"
              @click="handleUpdate(scope.row)"
            >更新</el-button>
            <el-button
              v-if="hasPermission('delete')"
              type="danger"
              size="mini"
              @click="handleDelete(scope.row)"
            >删除</el-button>
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

      <!--新增/编辑用户对话框-->
      <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
        <el-form
          class="small-space"
          :model="temp"
          :rules="temp_rules"
          ref="temp"
          label-position="left"
          label-width="85px"
          style="width: 100%; margin-left:5px;"
        >
          <el-form-item label="字典编码" prop="key">
            <el-input v-model="temp.key"></el-input>
          </el-form-item>
          <el-form-item label="字典描述" prop="desc">
            <el-input v-model="temp.desc"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button @click="addKeyValue">添加键值对</el-button>
          </el-form-item>
          <el-table :data="temp.KV.objects" style="width: 100%;">
            <el-table-column prop="key" label="键" width="180">
              <template scope="scope">
                <el-input v-model="scope.row.key" size="small"></el-input>
              </template>
            </el-table-column>
            <el-table-column prop="value" label="值" width="220">
              <template scope="scope">
                <el-input v-model="scope.row.value" size="small"></el-input>
              </template>
            </el-table-column>
            <el-table-column prop="order" label="排序" width="80">
              <template scope="scope">
                <el-input v-model="scope.row.order" size="small"></el-input>
              </template>
            </el-table-column>
            <el-table-column prop="desc" label="注释" min-width="220">
              <template scope="scope">
                <el-input v-model="scope.row.desc" size="small"></el-input>
              </template>
            </el-table-column>
            <el-table-column label="操作" align="center" width="100">
              <template scope="scope">
                <el-button
                  type="danger"
                  size="mini"
                  @click="deleteKeyValue(scope.row)"
                >删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form>
        <div slot="footer" class="dialog-footer">
          <el-button @click="dialogFormVisible = false">取 消</el-button>
          <el-button v-if="dialogStatus=='create'" type="primary" @click="doCreate">提 交</el-button>
          <el-button v-else type="primary" @click="doUpdate">提 交</el-button>
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
        key: "",
        desc: "",
        value: ""
      },
      listQuery: {
        page: 1,
        limit: 20,
        sort: "+id"
      },
      temp: {
        id: undefined,
        key: "",
        desc: "",
        KV: {
          objects: []
        }
      },
      temp_rules: {
        key: [
          {
            required: true,
            message: "字典编码不能为空！",
            trigger: "blur"
          }
        ],
        desc: [
          {
            required: true,
            message: "字典描述不能为空！",
            trigger: "blur"
          }
        ]
      },
      listLoading: true,
      objects: [],
      depts: [],
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
        key__like: "%" + this.filters.key + "%",
        desc__like: "%" + this.filters.desc + "%",
        value__like: "%" + this.filters.value + "%",
        limit: this.listQuery.limit,
        page: this.listQuery.page,
        ordering: this.listQuery.sort
      };
      getResourceListPage("hrsystem", "kv", param)
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
        key: this.temp.key,
        value: JSON.stringify(this.temp.KV.objects),
        desc: this.temp.desc
      };
      createResource("hrsystem", "kv", param)
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
        key: this.temp.key,
        value: JSON.stringify(this.temp.KV.objects),
        desc: this.temp.desc
      };
      updateResource("hrsystem", "kv", param)
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
    deleteKeyValue(row) {
      let index = this.temp.KV.objects.indexOf(row);
      this.temp.KV.objects.splice(index, 1);
    },
    addKeyValue() {
      this.temp.KV.objects.push({
        key: "",
        value: "",
        order: "",
        desc: ""
      });
    },
    handleFilter() {
      this.getList();
    },
    handleUpdate(row) {
      this.dialogStatus = "update";
      this.dialogFormVisible = true;
      this.temp.id = row.id;
      this.temp.key = row.key;
      this.temp.desc = row.desc;
      this.temp.KV.objects = JSON.parse(row.value);
    },
    handleDelete(row) {
      let param = {
        pk: row.id
      };
      deleteResource("hrsystem", "kv", param)
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
      this.temp.key = "";
      this.temp.KV.objects = [];
      this.temp.desc = "";
    },
    // 处理页码变更事件，参数为页码数
    handleSizeChange(size) {
      this.listQuery.limit = size;
      this.getList();
    },
    handleCurrentChange(currentPage) {
      this.listQuery.page = currentPage;
      this.getList();
    }
  }
};
</script>
