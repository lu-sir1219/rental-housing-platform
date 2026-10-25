# BM-公寓管理+户型管理+预约管理+租客管理+个人中心

> **版本**: v1.0 | **日期**: 2026-08-11 | **作者**: BM 运营商端设计文档
>
> 本文档为「租房智能体」平台 BM（公寓运营商/房东）端的完整技术设计文档，覆盖 5 个核心业务模块。

---

## 一、模块概述

### 1.1 公寓管理
公寓管理是 BM 运营的基础模块，负责公寓信息（名称、地址、坐标、网站、微信、物业类型、配套设施等）的增删改查。技术层面以 `institutes` 表为核心，关联 `unit_types`（户型）作为子资源。BM 运营商通过此模块完成房源的上架、编辑、下架操作，数据通过 PostgreSQL + pgvector 存储，坐标信息支持地图可视化。

**设计目的**：提供 BM 自助管理公寓资产的能力，替代传统线下 EXCEL 管理，实现房源数据的结构化、可检索、可展示。

**依赖模块**：户型管理（每套公寓下挂多个户型）、OpenStreetMap 前端地图展示（Leaflet）+ 后端多源地理编码（高德/Google/ORS 自动回退反填地址）、文件上传（公寓/户型图片）。

**适用场景**：BM 运营商新增合作公寓楼、修改公寓基础信息、查看公寓库存全貌、批量导入公寓数据。

### 1.2 户型管理
户型管理是公寓的子模块，管理每套公寓下的具体户型（Studio、1B1B、2B1B 等），包括户型名称、月租金、面积、楼层范围、房间数量、总套数/可租套数（库存）、租赁要求等。

**设计目的**：实现户型级别的精细化库存管理，支持租客按户型筛选房源，为租客管理模块提供库存数据基础。

**依赖模块**：公寓管理（institute_id 外键关联）、租客管理（创建/删除租客触发库存联动）。

**适用场景**：BM 为公寓添加新户型、调整租金、更新库存数量、设置租赁要求。

### 1.3 预约管理
预约管理是租客与 BM 之间的"看房预约"消息系统。租客在房源详情页右上角点击"📅 预约看房"按钮，填写手机号码和可选的看房留言，提交后系统创建一条 `VisitMessage`（看房预约消息）并向 BM 发送站内通知。BM 端可按公寓筛选、查看、标记已读这些预约消息。

> **注意**：此为"预约看房"（联系方式投递/线索收集），与"立即预定"（6 步预订下单流程，见户型卡片上的"立即预定"按钮）是两套**完全独立**的系统。预约看房**不需要登录**，仅投递电话号码供 BM 自行联系；预定则需登录并走完整的合同签署 + 付款流程。

**设计目的**：为租客提供低门槛的看房咨询入口（无需注册/登录即可提交联系方式），为 BM 提供统一的预约消息看板，减少人工跟进成本。

**依赖模块**：公寓管理（预约消息按公寓筛选）、站内通知（新预约自动通知 BM）。

**适用场景**：租客浏览房源后留下联系方式等待 BM 回电、BM 每日查看新增看房预约消息、标记已处理后标记已读。

### 1.4 租客管理
租客管理是 BM 运营的核心 CRM 模块，管理已入住/即将入住的租客信息（姓拼音、名拼音、中文全名、电话、邮箱、学校、所租公寓、所租户型、房间号、入住/退租日期、居住状态）。

**设计目的**：为 BM 提供租客档案的统一管理入口，支持快速检索（按姓名/电话/学校）、库存联动（入住扣库存、退租还库存）、租期跟踪。

**依赖模块**：公寓管理（所租公寓）、户型管理（所租户型 + 库存联动）。

**适用场景**：BM 录入新租客、更新租客信息、退租处理、按学校/公寓筛选租客。

### 1.5 个人中心
个人中心是 BM 运营商的账户管理页面，支持查看和编辑个人信息（用户名、手机号、微信、邮箱、二维码）。

**设计目的**：提供 BM 自助维护账户信息的能力，微信二维码用于租客联系房东。

**依赖模块**：用户认证系统（`/auth/me`）、文件上传（二维码图片）。

**适用场景**：BM 更新联系方式、上传/更换微信二维码、查看账户基本信息。

---

## 二、功能需求说明

### 2.1 公寓管理

| 功能 | 操作 | 输入 | 输出 | 业务规则 |
|------|------|------|------|----------|
| 创建公寓 | POST `/api/v1/institutes` | name, country, city, district, street, postal_code, address(自动拼接), building_type, amenities(JSON), latitude, longitude, contact_phone, contact_email, website_url, logo_url, description | InstituteRead | name 必填；支持结构化地址（country/city/district/street）自动拼接完整 address；坐标可选但前端强制定位 |
| 公寓列表 | GET `/api/v1/me/institutes` | page, page_size, keyword, city, building_type | {items[], total, page, page_size} | 按当前 BM 用户过滤（`bm_id = current_user.id`）；支持关键词搜索 name/address；支持按城市、建筑类型筛选 |
| 公寓详情 | GET `/api/v1/institutes/{id}` | id (path) | InstituteRead（含 unit_types 列表） | 预加载 unit_types 关系，返回完整子资源 |
| 编辑公寓 | PATCH `/api/v1/institutes/{id}` | 任意部分字段 | InstituteRead | 仅公寓所有者可编辑；坐标变更时重新反填地址 |
| 删除公寓 | DELETE `/api/v1/institutes/{id}` | id (path) | {ok: true} | 将 `status` 设为 `suspended`；级联将其下户型打上 `deleted_at` 时间戳 |

**删除策略**：公寓采用三态枚举 `status`（`pending`/`active`/`suspended`），删除即设为 `suspended`。户型采用 `deleted_at` 时间戳（NULL 表示未删除）。公寓删除时级联将其下所有户型打上 `deleted_at`。列表查询默认过滤 `status != 'suspended'`（公寓）和 `deleted_at IS NULL`（户型）。

### 2.2 户型管理

| 功能 | 操作 | 输入 | 输出 | 业务规则 |
|------|------|------|------|----------|
| 创建户型 | POST `/api/v1/institutes/{institute_id}/unit-types` | name, base_rent, area_sqm, bedrooms, bathrooms, hall_count, total_count, available_count, property_type, description, rental_requirements, amenities, images[] | UnitTypeRead | name 必填；total_count / available_count 默认值 1；`has_vacancy` 由 available_count > 0 自动计算 |
| 户型列表（按公寓） | GET `/api/v1/institutes/{institute_id}/unit-types` | page, page_size | {items[], total, page, page_size} | 过滤 `deleted_at IS NULL`；预加载 images 关系 |
| 户型列表（全部） | GET `/api/v1/unit-types` | page, page_size, keyword, min_rent, max_rent, property_type, institute_id | {items[], total, page, page_size} | 支持多条件组合筛选 |
| 户型详情 | GET `/api/v1/unit-types/{id}` | id (path) | UnitTypeRead（含 institute 摘要） | 预加载 institute 关系 |
| 编辑户型 | PATCH `/api/v1/unit-types/{id}` | 任意部分字段 | UnitTypeRead | 使用 `getattr` 防御性访问字段防止 `MissingGreenlet`；更新后重新 eager load 返回 |
| 删除户型 | DELETE `/api/v1/unit-types/{id}` | id (path) | {ok: true} | **软删除**（设置 `deleted_at` 时间戳） |
| 复制户型 | POST `/api/v1/unit-types/{id}/copy` | target_institute_id (可选) | UnitTypeRead | 创建一个内容相同的新户型（不含 images），默认同公寓 |

**库存机制（双层）**：
- **数据库层**：`total_count`（总套数）、`available_count`（可租套数）、`has_vacancy`（是否有空房，计算字段）
- **业务规则层**：
  - 创建租客 → `available_count - 1`
  - 删除租客 → `available_count + 1`
  - 租客换户型 → 归还旧户型 + 扣除新户型
    - 租客预约看房 → 不与库存联动（预约看房仅投递联系方式，不涉及户型预订）

### 2.3 预约管理

| 功能 | 操作 | 输入 | 输出 | 业务规则 |
|------|------|------|------|----------|
| 提交预约看房 | POST `/api/v1/apartment/submitVisitApply` | apartmentId, guestPhone (必填), guestMessage (选填) | {ok: true, message: "预约信息已发送给公寓管理员"} | **无需登录**；手机号必填且需为数字；自动向公寓创建者发送站内通知 |
| BM 查看预约消息 | GET `/api/v1/apartment/admin/getVisitMessageList` | apartmentId (Query, 必填) | [VisitMessageRead] | 只能查看自己管理的公寓的预约消息；按时间倒序 |
| 标记已读 | PUT `/api/v1/apartment/admin/markVisitMsgRead` | messageId (Query, 必填) | {ok: true} | 只能操作自己管理的公寓下的消息 |

**VisitMessage 数据模型**：
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer (PK) | 消息 ID |
| `apartment_id` | Integer (FK → institutes.id) | 预约的公寓 |
| `guest_phone` | String(32) | 租客手机号码 |
| `guest_message` | String(500) | 看房留言（选填） |
| `is_read` | Boolean (default=False) | BM 是否已读 |
| `created_at` | DateTime | 提交时间 |

**核心流程**：
```
租客浏览房源详情页 → 点击右上角"📅 预约看房"按钮
  → 弹窗填写手机号（必填）+ 看房留言（选填）
  → 提交 POST /apartment/submitVisitApply
  → 后端创建 VisitMessage 记录
  → 后端创建 Notification（通知 BM："手机号 138xxxx 提交了看房申请"）
  → 前端提示"预约信息已发送给公寓管理员"
```

**BM 端处理**：
```
BM 登录 → 进入预约消息页（/workspace/visit-messages）
  → 选择公寓
  → 查看该公寓下的预约消息列表（手机号 + 留言 + 时间 + 已读/未读状态）
  → 点击"标记已读"确认处理完毕
```

**预约看房 vs 立即预定（区分）**：

| 维度 | 📅 预约看房 | 🛒 立即预定 |
|------|------------|------------|
| 入口 | 房源详情页右上角按钮 | 户型卡片上的"立即预定"按钮 |
| 是否需要登录 | **否** | **是**（requiresAuth） |
| 填写内容 | 手机号 + 可选留言 | 6 步向导：入住日期→租期→个人信息→紧急联系人→确认→合同签署 |
| 数据模型 | `VisitMessage`（仅电话和留言） | `Booking`（含金额、合同、政策同意、身份信息） |
| BM 操作 | 查看消息、标记已读 | 批准/拒绝 Booking |
| 目的 | 线索收集/联系方式投递 | 正式下单/签约 |

### 2.4 租客管理

| 功能 | 操作 | 输入 | 输出 | 业务规则 |
|------|------|------|------|----------|
| 创建租客 | POST `/api/v1/tenants` | surname_pinyin, given_name_pinyin, chinese_name(可选), phone, email, school_name, current_unit_type_id, room_number, move_in_date, move_out_date, housing_status, label | TenantRead | 创建后自动 `available_count - 1`；预加载 unit_type.institute 链 |
| 租客列表 | GET `/api/v1/tenants` | page, page_size, keyword | {items[], total, page, page_size, total_pages} | 关键词搜索 surname_pinyin / given_name_pinyin / phone / school_name |
| 租客详情 | GET `/api/v1/tenants/{id}` | id (path) | TenantRead（含 unit_type_name + institute_name） | 预加载 unit_type.institute 链 |
| 编辑租客 | PATCH `/api/v1/tenants/{id}` | 任意部分字段 | TenantRead | 户型变更时**自动库存转移**（归还旧 + 扣除新） |
| 删除租客 | DELETE `/api/v1/tenants/{id}` | id (path) | {ok: true} | 执行**物理删除**；自动归还户型库存 |

**库存联动规则**：
| 操作 | 库存变化 |
|------|----------|
| 创建租客 | 目标户型 `available_count - 1` |
| 删除租客 | 目标户型 `available_count + 1` |
| 编辑租客（换户型） | 旧户型 `+1`，新户型 `-1` |
| 编辑租客（不换户型） | 不触发库存变化 |

### 2.5 个人中心

| 功能 | 操作 | 输入 | 输出 | 业务规则 |
|------|------|------|------|----------|
| 获取当前用户 | GET `/auth/me` | — | UserRead（含 id, username, phone, email, wechat, qr_code_url, role） | 基于 JWT token 认证 |
| 更新个人信息 | PATCH `/auth/me` | username, phone, email, wechat 等 | UserRead | 至少提供一个字段 |
| 上传二维码 | POST `/api/v1/uploads` | file (image) | {url: "/api/v1/uploads/xxx"} | 文件类型限制图片；存储路径 `uploads/qrcodes/` |
| 获取 BM 列表 | GET `/api/v1/bms` | page, page_size | {items[], total} | 公开接口，用于租客查看房东信息 |

---

## 三、整体设计思路

### 3.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     Vue 3 前端 (SPA)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │   Element Plus UI 组件                                │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐              │  │
│  │  │GlobalSide│ │ Router   │ │ Views    │              │  │
│  │  │ bar.vue  │ │ index.ts │ │ *.vue    │              │  │
│  │  └──────────┘ └──────────┘ └──────────┘              │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │ HTTP (axios)                      │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│               FastAPI 后端 (Python 3.13)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (routes/)                                  │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │  │
│  │  │institute│ │unit_type│ │visit_ms│ │tenants  │   │  │
│  │  │s.py     │ │s.py     │ │gs.py    │ │.py      │   │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Service Layer (services/)                            │  │
│  │  ┌──────────────┐ ┌──────────────┐                    │  │
│  │  │institute_svc │ │unit_type_svc │                    │  │
│  │  └──────────────┘ └──────────────┘                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Data Layer (models/ + SQLAlchemy Async)              │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │  │
│  │  │Institute│ │UnitType│ │VisitMsg│ │Tenant  │        │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│           数据存储层                                         │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ PostgreSQL 16    │  │ Redis 7          │                 │
│  │ + pgvector       │  │ (Celery 队列)     │                 │
│  └──────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心设计亮点

1. **Institute → UnitType 两层架构**：公寓（Institute）与户型（UnitType）是 1:N 关系，前端通过级联下拉实现「选公寓 → 选户型」的交互模式。Institute 承担地理属性（地址、坐标），UnitType 承担库存属性（总套数、可租套数）。

2. **库存双层管理**：数据库层直接存储 `total_count` / `available_count` 避免每次查询实时计算；业务层在租客 CRUD 操作时通过 `_adjust_inventory` 函数同步更新，保证数据一致性。

3. **软删除级联**：公寓采用三态 `status` 枚举（pending/active/suspended），户型采用 `deleted_at` 时间戳。删除公寓（设为 suspended）时自动级联将其下户型打上 `deleted_at` 时间戳，保留数据可追溯性。

4. **库存联动事务**：租客创建/编辑/删除操作在同一个数据库事务中完成租客数据变更 + 库存调整，`await session.flush()` 后再调整库存，最后 `await session.commit()` 统一提交，保证原子性。

5. **预约看房免登录设计**：租客无需注册/登录即可在房源详情页提交预约看房（手机号+留言），降低线索获取门槛。提交后自动向 BM 发送站内通知，VisitMessage + Notification 在同一事务中创建。

6. **前端地图展示**：公寓坐标通过 OpenStreetMap（Leaflet）在前端渲染，轻量无 API Key 依赖。后端地理编码采用多源回退策略（中国→高德，海外→Google→ORS→Haversine 兜底）。

7. **前端响应式设计**：表格列宽收紧适配 1200px 容器，避免横向滚动；使用 Element Plus 的 `el-table`、`el-dialog`、`el-form` 统一 UI 风格。

---

## 四、业务流程图

### 4.1 公寓管理流程

```
BM 登录 → 进入公寓管理页(/buildings)
  │
  ├── 新建公寓
  │     ├── 填写 name、结构化地址（country/city/district/street）、building_type、amenities 等
  │     ├── 选择坐标（地图点击或手动输入经纬度）
  │     ├── 上传封面图和图片集
  │     └── 提交 → POST /api/v1/institutes → 数据库 insert
  │
  ├── 编辑公寓
  │     ├── 点击"编辑" → 打开编辑对话框
  │     ├── 修改字段（地址变更触发重新地理编码）
  │     └── 保存 → PATCH /api/v1/institutes/{id} → 数据库 update
  │
  ├── 查看公寓
  │     ├── 点击公寓卡片 → 进入详情页(/building/{id})
  │     └── 展示公寓基本信息 + 户型列表 + 图片
  │
  └── 删除公寓
        ├── 点击"删除" → 确认对话框
        └── 确认 → DELETE /api/v1/institutes/{id} → status=suspended（级联户型 deleted_at）
```

### 4.2 户型管理流程

```
BM 登录 → 进入户型管理(/unit-type/manage) 或 从公寓详情进入
  │
  ├── 新增户型
  │     ├── 选择所属公寓（级联下拉）
  │     ├── 填写 name、base_rent、area_sqm、bedrooms、bathrooms
  │     ├── 填写 total_count（总套数）、available_count（可租套数）
  │     ├── 填写 rental_requirements（租赁要求）
  │     ├── 上传户型图片
  │     └── 提交 → POST /api/v1/institutes/{id}/unit-types
  │
  ├── 编辑户型
  │     ├── 点击户型卡片的"编辑"
  │     ├── 修改租金、库存、描述等
  │     └── 保存 → PATCH /api/v1/unit-types/{id}
  │
  ├── 复制户型
  │     ├── 点击"复制" → 自动创建副本（不含 images）
  │     └── POST /api/v1/unit-types/{id}/copy
  │
  └── 删除户型
        ├── 点击"删除" → 确认对话框
        └── 确认 → DELETE /api/v1/unit-types/{id} → deleted_at=now()
```

### 4.3 预约管理流程

```
租客端（预约看房 — 无需登录）：
  浏览房源详情页(/building/{id})
  → 点击右上角"📅 预约看房"按钮
  → 弹窗填写：手机号码（必填）+ 看房留言（选填）
  → 提交 POST /apartment/submitVisitApply
  → 系统创建 VisitMessage + 向 BM 发送站内通知
  → 提示"预约信息已发送给公寓管理员"

BM 端（查看预约消息）：
  ┌── 进入预约消息页(/workspace/visit-messages)
  │     ├── 下拉选择公寓
  │     └── 表格展示：提交时间 + 手机号码 + 留言 + 已读/未读状态
  │
  └── 处理消息
        ├── 点击"标记已读" → PUT /admin/markVisitMsgRead
        └── BM 自行拨打电话联系租客

附：租客端（立即预定 — 需登录，与预约看房无关）
  房源详情页户型卡片 → 点击"立即预定"
  → 6步向导：入住日期→租期→个人信息→紧急联系人→确认→合同签署
  → 创建 Booking(状态: pending)
  → BM 在 /bookings/landlord 审批
```

### 4.4 租客管理流程

```
BM 登录 → 进入租客管理(/tenants)
  │
  ├── 新增租客
  │     ├── 填写姓名（surname_pinyin + given_name_pinyin + chinese_name）
  │     ├── 填写电话、邮箱、学校
  │     ├── 选择公寓 → 自动加载该公寓下的户型（级联下拉）
  │     ├── 选择户型（触发库存检查）
  │     ├── 填写房间号、入住/退租日期、居住状态
  │     └── 提交 → POST /api/v1/tenants → insert + available_count - 1
  │
  ├── 编辑租客
  │     ├── 点击"编辑" → 打开编辑对话框
  │     ├── 修改字段 → 如变更户型：旧户型库存+1 + 新户型库存-1
  │     └── 保存 → PATCH /api/v1/tenants/{id}
  │
  ├── 搜索租客
  │     ├── 输入关键词 → GET /api/v1/tenants?keyword=xxx
  │     └── 匹配 surname_pinyin / given_name_pinyin / phone / school_name
  │
  └── 删除租客（退租）
        ├── 点击"删除" → 确认对话框
        └── 确认 → DELETE /api/v1/tenants/{id} → delete + available_count + 1
```

### 4.5 个人中心流程

```
BM 登录 → 点击头像/个人中心(/landlord/profile)
  │
  ├── 查看个人信息（从 /auth/me 获取）
  │
  ├── 编辑信息
  │     ├── 修改 username/phone/email/wechat
  │     └── 保存 → PATCH /auth/me
  │
  └── 上传微信二维码
        ├── 选择图片文件
        ├── 上传 → POST /api/v1/uploads
        └── 保存 URL → PATCH /auth/me（qr_code_url 字段）
```

---

## 五、数据结构设计

### 5.1 ER 关系图

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│   User   │       │ Institute│       │  Tenant  │
│ (users)  │       │(institute│       │(tenants) │
├──────────┤       │    s)    │       ├──────────┤
│ id (PK)  │       ├──────────┤       │ id (PK)  │
│ username │       │ id (PK)  │       │ user_id  │
│ phone    │       │ bm_id(FK)│──┐    │ current_ │
│ email    │       │ name     │  │    │ unit_type│
│ wechat   │       │ address  │  │    │ _id (FK) │
│ qr_code  │       │ city     │  │    │ surname_ │
│ role     │       │ lat/lng  │  │    │ pinyin   │
└──────────┘       │ is_delete│  │    │ phone    │
       │            │ d        │  │    │ school   │
       │            └──────────┘  │    │ room_no  │
       │                  │       │    │ housing_ │
       │                  │ 1:N   │    │ status   │
       │                  │       │    │ move_in  │
       │                  ▼       │    │ move_out │
       │            ┌──────────┐  │    └──────────┘
       │            │ UnitType │  │          │
       │            │(unit_typ │  │          │FK
       │            │   es)    │  │          │
       │            ├──────────┤  │          │
       │            │ id (PK)  │  │          │
       │            │ institute│──┘          │
       │            │ _id (FK) │             │
       │            │ name     │             │
       │            │ monthly_ │             │
       │            │ rent     │             │
       │            │ area_sqm │             │
       │            │ total_co │             │
       │            │ unt      │             │
       │            │ available│             │
       │            │ _count   │             │
       │            │ has_vaca │             │
       │            │ ncy      │             │
       │            │ is_delete│             │
       │            │ d        │             │
       │            └──────────┘             │
       │                  │                  │
       │                  │ 1:N              │
       │                  ▼                  │
       │            ┌──────────────┐         │
       └────────────│ VisitMessage │         │
                    │(apartment_   │         │
                    │visit_message │         │
                    │     s)       │         │
                    ├──────────────┤         │
                    │ id (PK)      │         │
                    │ apartment_id │─────────┘
                    │   (FK)       │→ institutes
                    │ guest_phone  │
                    │ guest_message│
                    │ is_read      │(bool)
                    │ created_at   │
                    └──────────────┘
```

### 5.2 核心表字段说明

#### 5.2.1 institutes 表（公寓）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | Integer | PK, auto | 主键 |
| `business_id` | String(24) | UNIQUE, index | 业务 ID |
| `uuid` | String(36) | UNIQUE | UUID 全局唯一标识 |
| `bm_id` | Integer | FK → users.id | 房东用户 ID |
| `name` | String(200) | NOT NULL | 公寓名称 |
| `name_cn` | String(200) | — | 中文名称 |
| `abbreviation` | String(50) | — | 简称 |
| `address` | String(300) | — | 完整地址（由结构化字段自动拼接） |
| `country` | String(10) | — | 国家 |
| `city` | String(100) | — | 城市 |
| `district` | String(100) | — | 区/区域 |
| `street` | String(200) | — | 街道+门牌号 |
| `postal_code` | String(20) | — | 邮编 |
| `latitude` | Numeric(9,6) | — | 纬度 |
| `longitude` | Numeric(9,6) | — | 经度 |
| `building_type` | String(50) | — | 建筑类型（apartment/condo/house/dormitory） |
| `total_floors` | Integer | — | 总楼层 |
| `year_built` | Integer | — | 建成年份 |
| `total_units` | Integer | — | 总户数 |
| `has_elevator` | Boolean | default=False | 是否有电梯 |
| `amenities` | JSON | — | 配套设施（如 ["gym","pool","laundry"]） |
| `female_only` | Boolean | default=False | 是否女生独栋 |
| `couples_allowed` | Boolean | default=False | 是否支持情侣入住 |
| `contact_phone` | String(32) | — | 联系电话 |
| `contact_email` | String(255) | — | 联系邮箱 |
| `website_url` | String(500) | — | 公寓官网 |
| `bm_wechat` | String(100) | — | BM 微信号 |
| `bm_wechat_qr` | String(500) | — | BM 微信二维码 URL |
| `logo_url` | String(500) | — | Logo 图片 URL |
| `description` | Text | — | 公寓描述 |
| `npc` | String(100) | — | 新加坡 NPC 辖区简称 |
| `status` | Enum | default=pending | 状态（pending/active/suspended） |
| `created_at` | DateTime | default=now | 创建时间 |
| `updated_at` | DateTime | onupdate=now | 更新时间 |

> **图片存储**：公寓图片通过 `BuildingImage` 独立子表管理（`institute_id` FK），不在 institutes 主表中存储。

#### 5.2.2 unit_types 表（户型）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | Integer | PK, auto | 主键 |
| `business_id` | String(24) | UNIQUE, index | 业务 ID |
| `uuid` | String(36) | UNIQUE | UUID 全局唯一标识 |
| `institute_id` | Integer | FK → institutes.id, ON DELETE CASCADE | 所属公寓 |
| `name` | String(100) | NOT NULL | 户型名称 |
| `property_type` | String(50) | — | 户型分类（studio/ensuite/1bed/2bed/3bed/4bed/5bed+/shared） |
| `bedrooms` | Integer | default=0 | 卧室数 |
| `bathrooms` | Integer | default=0 | 卫生间数 |
| `hall_count` | Integer | default=0 | 客厅数 |
| `area_sqm` | Float | — | 面积（平方米） |
| `base_rent` | Float | NOT NULL | 月租金 |
| `deposit_amount` | Float | — | 押金金额 |
| `deposit_type` | Enum | — | 押金类型（one_month/one_three/two_month/three_month/half_month/free/custom） |
| `currency` | String(10) | default=CNY | 货币（CNY/SGD/GBP 等） |
| `lease_start` | String(50) | — | 租期开始（自由文本，AI 可读） |
| `lease_end` | String(50) | — | 租期结束（自由文本） |
| `lease_start_date` | Date | — | 租期开始日期（结构化，DB 可查） |
| `lease_end_date` | Date | — | 租期结束日期（结构化） |
| `min_stay_months` | Integer | default=3 | 最短租期（月） |
| `special_offer` | Text | — | 专属优惠 |
| `floor_pricing` | JSONB | — | 楼层差异化加价 |
| `total_count` | Integer | default=1 | 该户型总套数 |
| `available_count` | Integer | default=1 | 可租套数 |
| `has_vacancy` | Boolean | default=True | 是否有空房（available_count > 0） |
| `amenities` | ARRAY(String) | — | 户型专属设施（如 ["ac","wifi","furniture"]） |
| `description` | Text | — | 户型描述 |
| `rental_requirements` | Text | — | 租赁要求 |
| `available_from` | Date | — | 可入住日期 |
| `status` | Enum | default=available | 状态（available/rented/maintenance） |
| `deleted_at` | DateTime | — | 软删除时间戳（NULL=未删除） |
| `created_at` | DateTime | default=now | 创建时间 |
| `updated_at` | DateTime | onupdate=now | 更新时间 |

> **图片存储**：户型图片通过 `UnitTypeImage` 独立子表管理（`unit_type_id` FK），不在 unit_types 主表中存储。

#### 5.2.3 apartment_visit_messages 表（预约看房消息）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | Integer | PK, auto | 主键 |
| `apartment_id` | Integer | FK → institutes.id | 预约的公寓 |
| `guest_phone` | String(32) | NOT NULL | 租客手机号码 |
| `guest_message` | String(500) | — | 看房留言（选填） |
| `is_read` | Boolean | default=False | BM 是否已读 |
| `created_at` | DateTime | default=now | 提交时间 |

#### 5.2.4 tenants 表（租客）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | Integer | PK, auto | 主键 |
| `user_id` | Integer | FK → users.id | 关联平台用户（可选） |
| `surname_pinyin` | String(100) | NOT NULL | 姓（拼音） |
| `given_name_pinyin` | String(100) | NOT NULL | 名（拼音） |
| `chinese_name` | String(100) | — | 中文全名（选填） |
| `phone` | String(20) | — | 电话号码 |
| `email` | String(200) | — | 邮箱 |
| `school_name` | String(200) | — | 学校名称 |
| `current_unit_type_id` | Integer | FK → unit_types.id | 当前所租户型 |
| `room_number` | String(50) | — | 房间号 |
| `housing_status` | Enum | — | 居住状态（living/moved_out/reserved） |
| `move_in_date` | Date | — | 入住日期 |
| `move_out_date` | Date | — | 退租日期 |
| `label` | String(100) | — | 标签（如"优质租客"） |
| `created_at` | DateTime | default=now | 创建时间 |
| `updated_at` | DateTime | onupdate=now | 更新时间 |

#### 5.2.5 users 表（用户 — 仅 BM 相关字段）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | Integer | PK, auto | 主键 |
| `username` | String(100) | NOT NULL | 用户名 |
| `phone` | String(20) | — | 手机号 |
| `email` | String(200) | — | 邮箱 |
| `wechat` | String(100) | — | 微信号 |
| `qr_code_url` | String(500) | — | 微信二维码图片 URL |
| `role` | Enum | NOT NULL | 角色（landlord/tenant/admin/bd_manager/maintenance_worker） |
| `hashed_password` | String | NOT NULL | 密码哈希 |
| `is_active` | Boolean | default=True | 活跃状态 |

---

## 六、接口设计

### 6.1 公寓管理 API

| 方法 | 路径 | 说明 | 请求参数 | 返回 |
|------|------|------|----------|------|
| POST | `/api/v1/institutes` | 创建公寓 | Body: InstituteCreate | `InstituteRead` (201) |
| GET | `/api/v1/me/institutes` | 我的公寓列表 | Query: page, page_size, keyword, city, building_type | `{items: InstituteRead[], total, page, page_size, total_pages}` (200) |
| GET | `/api/v1/institutes/{id}` | 公寓详情 | Path: id | `InstituteRead` (200) |
| PATCH | `/api/v1/institutes/{id}` | 编辑公寓 | Path: id, Body: InstituteUpdate | `InstituteRead` (200) |
| DELETE | `/api/v1/institutes/{id}` | 删除公寓 | Path: id | `{ok: true}` (200) |
| POST | `/api/v1/institutes/import` | 批量导入 | Body: JSON 数组 | `{created: N, errors: [...]}` (201) |
| GET | `/api/v1/institutes` | 公开公寓列表 | Query: page, page_size, keyword, city | `{items[], total}` (200) |

**InstituteCreate 核心字段**：
```json
{
  "name": "string (必填)",
  "country": "新加坡 (结构化地址)",
  "city": "Singapore",
  "district": "Queenstown",
  "street": "123 Main St",
  "postal_code": "123456",
  "address": "(自动拼接，也可手动传入兼容旧接口)",
  "building_type": "apartment | condo | house | dormitory",
  "latitude": 1.3521,
  "longitude": 103.8198,
  "contact_phone": "+65-12345678",
  "contact_email": "contact@example.com",
  "amenities": ["gym", "pool"],
  "description": "公寓描述",
  "website_url": "https://example.com",
  "logo_url": "/api/v1/uploads/xxx",
  "image_urls": ["/api/v1/uploads/xxx"]
}
```

**InstituteRead 核心字段**：
```json
{
  "id": 1,
  "business_id": "INST-20260811-0001",
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "bm_id": 1,
  "name": "Sunshine Apartments",
  "name_cn": "阳光公寓",
  "address": "123 Main St，Queenstown，Singapore，新加坡",
  "country": "新加坡",
  "city": "Singapore",
  "district": "Queenstown",
  "street": "123 Main St",
  "building_type": "apartment",
  "latitude": 1.3521,
  "longitude": 103.8198,
  "amenities": ["gym", "pool"],
  "status": "active",
  "unit_types": [{...}],
  "images": [{...}],
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```

**异常情况**：
| 场景 | HTTP 状态码 | 响应 |
|------|-------------|------|
| name 缺失 | 422 | `{"detail": [{"loc": ["body", "name"], "msg": "field required"}]}` |
| 公寓不存在 | 404 | `{"detail": "公寓不存在"}` |
| 非所有者编辑 | 403 | `{"detail": "无权操作"}` |

### 6.2 户型管理 API

| 方法 | 路径 | 说明 | 请求参数 | 返回 |
|------|------|------|----------|------|
| POST | `/api/v1/institutes/{institute_id}/unit-types` | 创建户型 | Path: institute_id, Body: UnitTypeCreate | `UnitTypeRead` (201) |
| GET | `/api/v1/institutes/{institute_id}/unit-types` | 公寓户型列表 | Path: institute_id, Query: page, page_size | `{items: UnitTypeRead[], total, page, page_size}` (200) |
| GET | `/api/v1/unit-types` | 全部户型列表 | Query: page, page_size, keyword, min_rent, max_rent, property_type, institute_id | `{items: UnitTypeRead[], total, page, page_size}` (200) |
| GET | `/api/v1/unit-types/{id}` | 户型详情 | Path: id | `UnitTypeRead` (200) |
| PATCH | `/api/v1/unit-types/{id}` | 编辑户型 | Path: id, Body: UnitTypeUpdate | `UnitTypeRead` (200) |
| DELETE | `/api/v1/unit-types/{id}` | 删除户型 | Path: id | `{ok: true}` (200) |
| POST | `/api/v1/unit-types/{id}/copy` | 复制户型 | Path: id, Body: {target_institute_id?} | `UnitTypeRead` (201) |

**UnitTypeCreate 核心字段**：
```json
{
  "name": "Studio (必填)",
  "base_rent": 2500.00,
  "currency": "SGD",
  "area_sqm": 30.5,
  "bedrooms": 0,
  "bathrooms": 1,
  "hall_count": 1,
  "property_type": "studio",
  "total_count": 10,
  "available_count": 5,
  "min_stay_months": 3,
  "deposit_amount": 2500.00,
  "deposit_type": "one_month",
  "description": "...",
  "rental_requirements": "押金1个月，收入3000+/月",
  "amenities": ["ac", "wifi", "furniture"],
  "floor_pricing": {"3-5F": 2500, "6-10F": 2700},
  "special_offer": "首月优惠200",
  "image_urls": ["/api/v1/uploads/xxx"]
}
```

**UnitTypeRead 核心字段**：
```json
{
  "id": 1,
  "business_id": "UT-20260811-0001",
  "uuid": "660e8400-e29b-41d4-a716-446655440001",
  "institute_id": 1,
  "institute_name": "Sunshine Apartments",
  "name": "Studio",
  "property_type": "studio",
  "bedrooms": 0,
  "bathrooms": 1,
  "hall_count": 1,
  "base_rent": 2500.00,
  "currency": "SGD",
  "deposit_amount": 2500.00,
  "deposit_type": "one_month",
  "area_sqm": 30.5,
  "total_count": 10,
  "available_count": 5,
  "has_vacancy": true,
  "min_stay_months": 3,
  "description": "...",
  "rental_requirements": "押金1个月...",
  "amenities": ["ac", "wifi", "furniture"],
  "floor_pricing": {"3-5F": 2500},
  "status": "available",
  "deleted_at": null,
  "images": [{...}],
  "created_at": "...",
  "updated_at": "..."
}
```

**异常情况**：
| 场景 | HTTP 状态码 | 响应 |
|------|-------------|------|
| name 缺失 | 422 | `{"detail": [{"loc": ["body", "name"], "msg": "field required"}]}` |
| 户型不存在 | 404 | `{"detail": "户型不存在"}` |
| 公寓不存在 | 404 | `{"detail": "公寓不存在"}` |
| MissingGreenlet（懒加载） | 500 | 后端日志记录，前端显示"加载失败" |

### 6.3 预约管理 API

| 方法 | 路径 | 说明 | 请求参数 | 返回 |
|------|------|------|----------|------|
| POST | `/api/v1/apartment/submitVisitApply` | 租客提交预约看房 | Body: {apartmentId, guestPhone, guestMessage?} | `{ok: true, message: "预约信息已发送给公寓管理员"}` (201) |
| GET | `/api/v1/apartment/admin/getVisitMessageList` | BM 查看预约消息 | Query: apartmentId (必填) | `[VisitMessageRead]` (200) |
| PUT | `/api/v1/apartment/admin/markVisitMsgRead` | BM 标记已读 | Query: messageId (必填) | `{ok: true}` (200) |

**SubmitVisitApply 请求体**：
```json
{
  "apartmentId": 1,
  "guestPhone": "13800138000 (必填, 仅数字)",
  "guestMessage": "期望周末看房，请提前联系 (选填, 最多500字)"
}
```

**VisitMessageRead 响应**：
```json
{
  "id": 1,
  "apartment_id": 1,
  "guest_phone": "13800138000",
  "guest_message": "期望周末看房",
  "is_read": false,
  "created_at": "2026-08-11T10:30:00"
}
```

**核心业务逻辑**：
1. 租客提交预约看房 → 验证 `apartmentId` 对应的公寓存在 → 验证 `guestPhone` 非空且为数字 → 创建 `VisitMessage` 记录 → 向公寓创建者发送站内通知 → 返回成功
2. BM 查看预约消息 → 验证当前用户是公寓所有者或管理员 → 按公寓 ID 查询所有预约消息（按时间倒序）
3. BM 标记已读 → 验证消息存在且属于当前用户的公寓 → 设置 `is_read = True`

**异常情况**：
| 场景 | HTTP 状态码 | 响应 |
|------|-------------|------|
| 公寓不存在 | 400 | `{"detail": "公寓不存在"}` |
| 手机号为空或含非数字 | 400 | `{"detail": "请输入正确的手机号码"}` |
| BM 查看他人公寓的消息 | 403 | `{"detail": "无权查看该公寓的预约消息"}` |
| 标记不存在的消息 | 404 | `{"detail": "消息不存在"}` |

### 6.4 租客管理 API

| 方法 | 路径 | 说明 | 请求参数 | 返回 |
|------|------|------|----------|------|
| POST | `/api/v1/tenants` | 创建租客 | Body: TenantCreate | `TenantRead` (201) |
| GET | `/api/v1/tenants` | 租客列表 | Query: page, page_size, keyword | `{items: TenantRead[], total, page, page_size, total_pages}` (200) |
| GET | `/api/v1/tenants/{id}` | 租客详情 | Path: id | `TenantRead` (200) |
| PATCH | `/api/v1/tenants/{id}` | 编辑租客 | Path: id, Body: TenantUpdate | `TenantRead` (200) |
| DELETE | `/api/v1/tenants/{id}` | 删除租客 | Path: id | `{ok: true, detail: "房客已删除"}` (200) |

**TenantCreate 核心字段**：
```json
{
  "surname_pinyin": "ZHANG (必填)",
  "given_name_pinyin": "SAN (必填)",
  "chinese_name": "张三 (选填)",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "school_name": "National University of Singapore",
  "current_unit_type_id": 1,
  "room_number": "301",
  "housing_status": "living",
  "move_in_date": "2026-09-01",
  "move_out_date": "2027-08-31",
  "label": "优质租客"
}
```

**TenantRead 核心字段**：
```json
{
  "id": 1,
  "surname_pinyin": "ZHANG",
  "given_name_pinyin": "SAN",
  "chinese_name": "张三",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "school_name": "National University of Singapore",
  "current_unit_type_id": 1,
  "unit_type_name": "Studio",
  "institute_name": "Sunshine Apartments",
  "room_number": "301",
  "housing_status": "living",
  "move_in_date": "2026-09-01",
  "move_out_date": "2027-08-31",
  "label": "优质租客",
  "created_at": "...",
  "updated_at": "..."
}
```

**异常情况**：
| 场景 | HTTP 状态码 | 响应 |
|------|-------------|------|
| 必填字段缺失 | 422 | `{"detail": [{"loc": ["body", "surname_pinyin"], "msg": "field required"}]}` |
| 户型不存在 | 422 | 库存调整失败（`unit_type_id` 无效则跳过库存操作） |
| 租客不存在 | 404 | `{"detail": "房客不存在"}` |

### 6.5 个人中心 API

| 方法 | 路径 | 说明 | 请求参数 | 返回 |
|------|------|------|----------|------|
| GET | `/auth/me` | 获取当前用户信息 | — (JWT Header) | `UserRead` (200) |
| PATCH | `/auth/me` | 更新个人信息 | Body: UserUpdate | `UserRead` (200) |
| GET | `/api/v1/me` | 获取当前用户信息（旧端点） | — | `UserRead` (200) |
| PUT | `/api/v1/me` | 更新个人信息（旧端点） | Body: UserUpdate | `UserRead` (200) |
| POST | `/api/v1/uploads` | 上传文件 | FormData: file | `{url: "/api/v1/uploads/xxx"}` (200) |
| GET | `/api/v1/bms` | BM 列表 | Query: page, page_size | `{items: UserRead[], total}` (200) |

**UserUpdate 核心字段**：
```json
{
  "username": "new_username",
  "phone": "13900139000",
  "email": "new@example.com",
  "wechat": "new_wechat_id",
  "qr_code_url": "/api/v1/uploads/qrcodes/xxx.png"
}
```

---

## 七、核心代码逻辑说明

### 7.1 库存联动机制（`_adjust_inventory`）

**文件位置**：`backend/app/api/v1/routes/tenants.py:17-24`

```python
async def _adjust_inventory(session: AsyncSession, unit_type_id: int | None, delta: int):
    """调整户型可租数量（delta 为正表示归还，为负表示占用）"""
    if unit_type_id is None:
        return
    ut = await session.get(UnitType, unit_type_id)
    if ut:
        ut.available_count = max(0, (ut.available_count or 0) + delta)
        ut.has_vacancy = ut.available_count > 0
```

**逻辑要点**：
- `delta = -1`：创建租客时占用一套
- `delta = +1`：删除租客或换出户型时归还一套
- `available_count` 使用 `max(0, ...)` 防止负数
- `has_vacancy` 自动同步更新为 `available_count > 0`
- 函数设计为独立辅助函数，避免重复代码

**调用时机**：
| 操作 | 调用 | delta |
|------|------|-------|
| 创建租客 | `_adjust_inventory(session, data.current_unit_type_id, -1)` | -1 |
| 删除租客 | `_adjust_inventory(session, t.current_unit_type_id, +1)` | +1 |
| 编辑租客（换户型） | `_adjust_inventory(session, old_unit_type_id, +1)` + `_adjust_inventory(session, new_unit_type_id, -1)` | 旧+1 新-1 |

### 7.2 软删除级联

**公寓删除**（`backend/app/api/v1/routes/institutes.py`）：
```python
@router.delete("/{institute_id}")
async def delete_institute(institute_id: int, session: AsyncSession = Depends(get_db_session)):
    institute = await session.get(Institute, institute_id)
    if not institute:
        raise HTTPException(404, "公寓不存在")
    institute.status = InstituteStatus.suspended  # 公寓设为 suspended
    # 级联软删除其下所有户型（打上 deleted_at 时间戳）
    from datetime import datetime, timezone
    unit_types = await session.execute(
        select(UnitType).where(UnitType.institute_id == institute_id, UnitType.deleted_at.is_(None))
    )
    for ut in unit_types.scalars():
        ut.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return {"ok": true}
```

**关键设计**：
- 公寓：三态 `status` 枚举（pending/active/suspended），删除=设为 suspended
- 户型：`deleted_at` 时间戳，NULL 表示未删除，非 NULL 表示已删除
- 公寓和户型均不物理删除，保留数据用于审计和恢复
- 列表查询默认过滤 `status != 'suspended'`（公寓）和 `deleted_at IS NULL`（户型）
- 级联操作在同一事务中完成

### 7.3 预约看房消息提交 + 通知

**文件位置**：`backend/app/api/v1/routes/visit_messages.py:32-63`

预约看房的核心逻辑在 `submit_visit_apply` 函数中：

```python
@router.post("/submitVisitApply", status_code=201)
async def submit_visit_apply(data: SubmitVisitApply, session: AsyncSession = Depends(get_db_session)):
    # 1. 验证公寓存在
    apt = await session.get(Institute, data.apartment_id)
    if not apt:
        raise HTTPException(400, "公寓不存在")

    # 2. 验证手机号（非空且为数字）
    phone = data.guest_phone.strip()
    if not phone or not phone.isdigit():
        raise HTTPException(400, "请输入正确的手机号码")

    # 3. 创建 VisitMessage 记录
    msg = VisitMessage(
        apartment_id=data.apartment_id,
        guest_phone=phone,
        guest_message=data.guest_message.strip() or None,
    )
    session.add(msg)
    await session.flush()

    # 4. 向公寓创建者发送站内通知
    notif = Notification(
        user_id=apt.created_by,
        type=NotificationType.system,
        title="新的预约看房申请",
        content=f"手机号 {phone} 提交了看房申请...",
        entity_type="visit_message",
        entity_id=str(msg.id),
        property_id=data.apartment_id,
    )
    session.add(notif)
    await session.commit()
    return {"ok": True, "message": "预约信息已发送给公寓管理员"}
```

**逻辑要点**：
- **无需身份认证**：该接口为公开端点，租客无需登录即可提交
- 先 `flush` VisitMessage 获取 `msg.id`，再将 `entity_id` 写入通知
- 通知与消息在同一事务中提交，保证一致性
- BM 端通过 `getVisitMessageList` 按 `apartment_id` 查询，权限校验只允许查看自己管理的公寓

### 7.4 前端级联下拉（选公寓 → 选户型）

**文件位置**：`frontend/src/views/TenantManagement.vue`

**实现方式**：
1. 租客创建表单中有两个 `el-select`：公寓选择器 + 户型选择器
2. 公寓选择器的 `@change` 事件触发 `fetchUnitTypes(instituteId)`
3. 户型选择器动态加载该公寓下的户型列表
4. `fetchBuildings()` 兼容 API 返回格式：`Array.isArray(r.data) ? r.data : r.data.items`

```typescript
// 简化的级联逻辑
const onInstituteChange = async (instituteId: number) => {
  unitTypes.value = []
  form.current_unit_type_id = null
  const r = await unitTypeService.listByInstitute(instituteId)
  unitTypes.value = Array.isArray(r.data) ? r.data : r.data.items
}
```

### 7.5 前端 API 兼容处理

**文件位置**：`frontend/src/views/TenantManagement.vue`

由于后端不同端点返回格式不一致（有的直接返回数组，有的返回 `{items, total}`），前端统一做兼容处理：

```typescript
// fetchBuildings 兼容处理
const fetchBuildings = async () => {
  const r = await buildingService.getMyBuildings()
  buildings.value = Array.isArray(r.data) ? r.data : r.data.items
}
```

### 7.6 二维码上传路径处理

**文件位置**：`frontend/src/views/LandlordProfile.vue`

- 上传时存储完整相对路径：`/api/v1/uploads/qrcodes/xxx.png`
- 加载时检查是否已包含 `/api/v1/uploads/` 前缀，防重复拼接：

```typescript
const getQrCodeUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('/api/v1/uploads/')) return url
  return `/api/v1/uploads/${url}`
}
```

---

## 八、异常与容错设计

### 8.1 常见异常场景

| 模块 | 异常场景 | 发生原因 | 处理方式 |
|------|----------|----------|----------|
| 公寓管理 | 地址地理编码失败 | 后端地理编码服务（高德/Google/ORS 多源回退）不可用或地址无效 | 创建/编辑不阻塞，仅提示"地理编码失败" |
| 公寓管理 | 删除有关联租客的公寓 | 公寓下有活跃租客 | status 设为 suspended，户型同步打 deleted_at 时间戳，租客数据不变 |
| 户型管理 | `MissingGreenlet` 错误 | 异步会话中访问懒加载关系 | `_to_read` 中用 `try/except` 包裹；关键查询使用 `selectinload` 预加载 |
| 户型管理 | Schema 字段不匹配 | Pydantic 默认值覆盖真实值 | `_to_read` 显式传递所有字段；`UnitTypeUpdate` 用 `getattr` 防御性访问 |
| 预约管理 | 看他人公寓的预约消息 | BM 试图查看非自己管理的公寓 | 后端校验 `apt.created_by != current_user.id`，返回 403 |
| 租客管理 | 库存负数 | 并发创建租客或数据不一致 | `max(0, available_count + delta)` 防止负数 |
| 租客管理 | 户型不存在 | `current_unit_type_id` 指向已删除户型 | `_adjust_inventory` 中 `unit_type_id is None` 时直接返回 |
| 个人中心 | 文件上传失败 | 文件过大或格式不支持 | 前端限制文件类型和大小；后端返回具体错误信息 |
| 全局 | 用户令牌过期 | JWT token 超时 | 前端 Axios 拦截器捕获 401 → 清除 token → 重定向登录页 |
| 全局 | ResizeObserver 警告 | Element Plus 组件内部 | `App.vue` 全局错误捕获过滤 `ResizeObserver loop` 警告 |

### 8.2 容错方案

1. **懒加载防御**：
   - 所有涉及跨表查询的路由使用 `selectinload` 预加载关系链（如 `Tenant.unit_type → UnitType.institute`）
   - `_to_read` 转换函数中用 `try/except` 包裹懒加载访问，防止 `MissingGreenlet`

2. **库存操作幂等性**：
   - `_adjust_inventory` 可被多次调用，每次仅做 `delta` 增量
   - 删除租客时即使 `current_unit_type_id` 已为空，也不抛异常

3. **软删除过滤一致性**：
   - 公寓列表查询默认加 `WHERE status != 'suspended'`
   - 户型列表查询默认加 `WHERE deleted_at IS NULL`
   - 详情查询不自动过滤（管理员可能需要查看已删除记录）

4. **前端错误提示**：
   - 所有 API 调用使用统一的 `ElMessage.error()` 提示
   - 表单校验失败时字段下方显示红色错误信息（Element Plus 原生支持）

### 8.3 日志规范

- 后端使用 Python `logging` 模块，关键操作记录 INFO 日志（创建/删除/状态变更）
- 异常记录 ERROR 日志，包含 traceback
- Celery 任务日志通过 `celery -A app.celery_app worker --loglevel=info` 输出
- 前端仅做 `console.error` 调试输出，不记录用户操作日志

---

## 九、测试用例

### 9.1 公寓管理

| 编号 | 分类 | 测试场景 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|----------|----------|----------|----------|
| INST-01 | 正常 | 创建公寓 | BM 已登录 | POST /institutes，name="Test Apt" | 201，返回 InstituteRead，status=active |
| INST-02 | 正常 | 编辑公寓名称 | 公寓已存在 | PATCH /institutes/{id}，name="New Name" | 200，name 已更新 |
| INST-03 | 正常 | 删除公寓 | 公寓已存在，下有 3 个户型 | DELETE /institutes/{id} | 200，公寓 status=suspended，3个户型 deleted_at 非空 |
| INST-04 | 正常 | 分页查询 | 数据库有 25 个公寓 | GET /me/institutes?page=2&page_size=10 | 200，返回 items[10]、total=25 |
| INST-05 | 正常 | 按城市筛选 | 有新加坡和伦敦公寓 | GET /me/institutes?city=Singapore | 200，仅返回新加坡公寓 |
| INST-06 | 边界 | 创建公寓 name 为空 | BM 已登录 | POST /institutes，name="" | 422，Pydantic 校验失败 |
| INST-07 | 边界 | 编辑不存在的公寓 | — | PATCH /institutes/99999 | 404，"公寓不存在" |
| INST-08 | 异常 | 非所有者编辑 | BM-A 创建公寓，BM-B 编辑 | BM-B PATCH /institutes/{id} | 403，"无权操作" |

### 9.2 户型管理

| 编号 | 分类 | 测试场景 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|----------|----------|----------|----------|
| UT-01 | 正常 | 创建户型 | 公寓已存在 | POST /institutes/{id}/unit-types，name="Studio" | 201，total_count=1，available_count=1，has_vacancy=true |
| UT-02 | 正常 | 编辑户型租金 | 户型已存在 | PATCH /unit-types/{id}，base_rent=3000 | 200，租金已更新 |
| UT-03 | 正常 | 复制户型 | 户型已存在 | POST /unit-types/{id}/copy | 201，新户型 name 相同但 id 不同，images 为空 |
| UT-04 | 正常 | 删除户型 | 户型已存在 | DELETE /unit-types/{id} | 200，deleted_at 时间戳非空 |
| UT-05 | 正常 | 按租金范围筛选 | 有 2000/3000/4000 的户型 | GET /unit-types?min_rent=2500&max_rent=3500 | 200，仅返回 3000 的户型 |
| UT-06 | 边界 | 创建户型 total_count=0 | 公寓已存在 | POST ... total_count=0, available_count=0 | 201，has_vacancy=false |
| UT-07 | 边界 | 编辑不存在的户型 | — | PATCH /unit-types/99999 | 404 |
| UT-08 | 异常 | name 缺失 | 公寓已存在 | POST ... 不含 name | 422 |

### 9.3 预约管理

| 编号 | 分类 | 测试场景 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|----------|----------|----------|----------|
| VM-01 | 正常 | 租客提交预约看房 | 公寓存在 | POST /apartment/submitVisitApply，完整手机号 | 201，创建 VisitMessage + 通知 |
| VM-02 | 正常 | 租客提交含留言的预约 | 公寓存在 | POST ... guestMessage="周末看房" | 201，留言正确保存 |
| VM-03 | 正常 | BM 查看预约消息 | BM 已登录，有预约消息 | GET /admin/getVisitMessageList?apartmentId=1 | 200，返回消息列表按时间倒序 |
| VM-04 | 正常 | BM 标记已读 | BM 已登录，有未读消息 | PUT /admin/markVisitMsgRead?messageId=1 | 200，is_read=true |
| VM-05 | 正常 | 免登录提交 | 无 token | POST /apartment/submitVisitApply | 201（无需认证） |
| VM-06 | 边界 | 手机号为空 | 公寓存在 | POST ... guestPhone="" | 400，"请输入正确的手机号码" |
| VM-07 | 边界 | 手机号含字母 | 公寓存在 | POST ... guestPhone="138abc" | 400 |
| VM-08 | 边界 | 留言超长 | 公寓存在 | POST ... guestMessage=(501字符) | 422（Pydantic max_length=500） |
| VM-09 | 异常 | 公寓不存在 | — | POST ... apartmentId=99999 | 400，"公寓不存在" |
| VM-10 | 异常 | 查看他人公寓的消息 | BM-B 查看 BM-A 的公寓消息 | GET /admin/getVisitMessageList?apartmentId=(BM-A的公寓) | 403，"无权查看" |

### 9.4 租客管理

| 编号 | 分类 | 测试场景 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|----------|----------|----------|----------|
| TN-01 | 正常 | 创建租客 | 户型 available_count=5 | POST /tenants，完整信息 | 201，户型 available_count 变为 4 |
| TN-02 | 正常 | 删除租客（退租） | 租客存在，户型 available_count=4 | DELETE /tenants/{id} | 200，户型 available_count 变为 5 |
| TN-03 | 正常 | 租客换户型 | 租客在户型A，available_count: A=4, B=5 | PATCH ... current_unit_type_id=B | 200，A→5, B→4 |
| TN-04 | 正常 | 搜索租客（按拼音） | 有 ZHANG SAN | GET /tenants?keyword=ZHANG | 200，返回 ZHANG SAN |
| TN-05 | 正常 | 搜索租客（按学校） | 有 NUS 学生 | GET /tenants?keyword=NUS | 200，返回 NUS 学生 |
| TN-06 | 边界 | 创建租客时不选户型 | — | POST ... current_unit_type_id=null | 201，跳过库存调整 |
| TN-07 | 边界 | 库存减到 0 后再创建 | 户型 available_count=0 | POST /tenants，current_unit_type_id=该户型 | 201，available_count 保持为 0（max(0, -1+0)） |
| TN-08 | 异常 | 编辑不存在的租客 | — | PATCH /tenants/99999 | 404 |

### 9.5 个人中心

| 编号 | 分类 | 测试场景 | 前置条件 | 操作步骤 | 预期结果 |
|------|------|----------|----------|----------|----------|
| PF-01 | 正常 | 获取当前用户信息 | BM 已登录 | GET /auth/me | 200，返回 UserRead |
| PF-02 | 正常 | 更新手机号 | BM 已登录 | PATCH /auth/me，phone="13900139000" | 200，phone 已更新 |
| PF-03 | 正常 | 上传二维码 | BM 已登录 | POST /uploads，图片文件 | 200，返回文件 URL |
| PF-04 | 边界 | 更新为空 body | BM 已登录 | PATCH /auth/me，{} | 422（至少一个字段） |
| PF-05 | 异常 | 未登录获取信息 | 无 token | GET /auth/me | 401 |
| PF-06 | 异常 | 上传非图片文件 | BM 已登录 | POST /uploads，.exe 文件 | 400 / 422 |

---

## 十、模块难点 & 解决方案

### 10.1 地图地址回填（el-dialog + Leaflet 响应式断裂）

**问题描述**：在 `CreateProperty.vue` 的 el-dialog 中使用 Leaflet 地图组件，地图回调中修改 `reactive()` 对象的值，Vue DOM 未触发更新。

**已尝试方案**：
- `watch` 桥接：监听地图状态变化 → 写入响应式变量
- `v-if` 开关：先销毁再重建 dialog 内的地图组件
- `:key` 重渲染：改变 key 值强制重建组件

**当前状态**：**暂未解决**，已添加完整报错提示，用户可手动输入经纬度。

**建议后续方向**：
- 将地图逻辑抽离为独立组件，通过 `defineExpose` / `emit` 通信
- 使用 `nextTick` + `markRaw` 防止 Leaflet 对象被 Vue 代理
- 考虑将 `el-dialog` 替换为 `el-drawer` 避免 z-index 层级问题

### 10.2 PDF 模板坐标标注 → 填充引擎

**问题描述**：合同模板管理系统已完成 PDF 模板上传 + 坐标标注（前端拖动框选矩形标注字段位置），但 PDF 覆盖引擎（在指定坐标写文本/渲染字段值）尚未实现。

**已完成部分**：
- 数据库 `contract_templates` 表（含 `field_positions` JSONB）
- 后端 CRUD API（上传/下载/坐标保存/删除）
- 前端 `ContractTemplateManager.vue`（PDF 预览 + 矩形框选 + 坐标保存）

**待实现**：
- PDF 填充引擎：PyPDF2 / reportlab 在指定坐标叠加文本
- 合同生成时从 `contract_templates` 加载模板 → 填充租客/户型/租金信息
- 中文字体嵌入（模板使用标准租房合同中文模板）

### 10.3 库存双层机制的并发安全

**问题描述**：创建租客时 `available_count - 1` 是读-改-写操作，高并发下可能出现竞态条件。

**当前实现**：
- 操作在同一个数据库事务中完成
- 使用 `asyncpg` 驱动，每个请求独立事务

**潜在风险**：
- 两个 BM 同时为同一户型创建租客，可能都读到 `available_count=1`，最终 `available_count` 变为 0 但实际创建了 2 个租客

**建议增强**：
- 使用 `SELECT ... FOR UPDATE` 行锁
- 或使用 PostgreSQL 原子更新：`UPDATE unit_types SET available_count = available_count - 1 WHERE id = ? AND available_count > 0`
- 上游创建租客前检查 `available_count > 0`（防御性校验）

### 10.4 前端路由定义重复

**问题描述**：部分路由有多个定义指向同一组件：
- `/property/manage` 和 `/unit-type/manage` → `ManageProperties.vue`
- `/property/create` 和 `/unit-type/create` → `CreateProperty.vue`
- `/buildings/:id/unit-types` → `UnitTypeList.vue`（从公寓查看户型，但侧边栏不显示）

**影响**：
- 菜单重构后旧路由保留但不在侧边栏显示，造成代码冗余
- 编辑页面通过 query 参数区分是编辑公寓还是编辑户型（如 `?type=property`），增加了组件复杂度

**建议**：
- 确定主路由（建议统一到 `/buildings` 和 `/unit-type` 两套路由）
- 旧路由添加永久重定向（301），待搜索引擎/外部链接迁移后删除

---

## 十一、待优化点 & 后续迭代

### 11.1 代码清理

| 优先级 | 项目 | 说明 |
|--------|------|------|
| 高 | 路由统一 | 清理 `/property/manage`→`/unit-type/manage` 等重复路由，添加 301 重定向 |
| 高 | 前端 API 兼容代码 | `Array.isArray(r.data) ? r.data : r.data.items` 统一后端返回格式后移除 |
| 中 | Schema 字段补全 | `UnitTypeRead` 确认所有字段已覆盖，移除冗余的 `try/except` 防御代码 |
| 中 | AdminWorkspace 清理 | 移除已隐藏的 5 个 Tab（房源管理/审核/财务/消息/门店设置）的代码 |
| 低 | console.error 清理 | 生产环境移除调试用 `console.error` |

### 11.2 功能增强

| 优先级 | 功能 | 说明 |
|--------|------|------|
| 高 | PDF 合同填充引擎 | 根据模板坐标覆盖信息生成可签署 PDF |
| 高 | 库存并发安全 | 添加行锁或原子更新防竞态 |
| 中 | 地图地址回填修复 | 解决 el-dialog 内 Leaflet 响应式问题 |
| 中 | 批量操作 | 租客批量导入/导出 EXCEL、公寓批量导入优化 |
| 中 | 租客历史记录 | 租客的预约历史、合同历史、维修工单历史 |
| 低 | 公寓/户型操作审计日志 | 记录谁在什么时间做了什么操作 |
| 低 | 数据看板 | 公寓入住率、户型空置率、月度收入统计 |
| 低 | 消息通知 | BM 收到新预约/租客退租提醒（可接入邮件/微信） |

### 11.3 性能优化

| 项目 | 说明 |
|------|------|
| 户型列表预加载 | 公寓详情页一次性预加载所有户型，避免 N+1 查询 |
| Redis 缓存 | 热门公寓/户型数据缓存到 Redis（已部署 Redis 7，待接入） |
| 图片懒加载 | 公寓/户型图片列表使用 `loading="lazy"` |
| 前端打包优化 | `vite build` 按路由 code-split，减小首屏 JS 体积 |

---

## 十二、模块验收标准

### 12.1 功能验收

| 模块 | 验收项 | 达标条件 |
|------|--------|----------|
| 公寓管理 | CRUD | 创建/查看/编辑/删除公寓全部正常；删除后公寓 `status=suspended`、户型 `deleted_at` 非空 |
| 公寓管理 | 搜索筛选 | 按关键词搜索返回匹配公寓；按城市筛选项正确 |
| 公寓管理 | 批量导入 | 至少 10 条数据批量导入成功；含错误数据时返回 errors[] |
| 户型管理 | CRUD | 创建/查看/编辑/删除/复制户型全部正常；库存字段正确保存 |
| 户型管理 | 库存显示 | 户型卡片正确显示"已租/总共"（如 "3/10"） |
| 户型管理 | 筛选 | 按租金范围、物业类型、公寓筛选正确 |
| 预约管理 | 提交 | 租客无需登录即可提交预约看房（手机号+留言） |
| 预约管理 | 列表 | BM 选择公寓后正确显示该公寓的预约消息列表，按时间倒序 |
| 预约管理 | 标记已读 | 点击"标记已读"后消息状态变为已读 |
| 预约管理 | 通知 | 租客提交后 BM 收到站内通知 |
| 预约管理 | 权限 | 非公寓所有者无法查看该公寓的预约消息 |
| 租客管理 | CRUD | 创建/查看/编辑/删除租客全部正常 |
| 租客管理 | 库存联动 | 创建→扣库存；删除→还库存；换户型→转移库存 |
| 租客管理 | 搜索 | 按姓名拼音/电话/学校搜索正确 |
| 个人中心 | 信息编辑 | 修改用户名/电话/微信/邮箱全部正常；刷新后保留 |

### 12.2 数据验收

| 验收项 | 达标条件 |
|--------|----------|
| 数据库一致性 | 创建租客后 `available_count` 正确减少；删除后正确增加 |
| has_vacancy 一致性 | `available_count > 0` ↔ `has_vacancy = True` 始终一致 |
| 软删除一致性 | 删除公寓（suspended）后，其下户型全部 `deleted_at IS NOT NULL` |
| 外键完整性 | 删除户型不会导致 Tenant 的 `current_unit_type_id` 悬空（FK 约束） |

### 12.3 异常验收

| 验收项 | 达标条件 |
|--------|----------|
| 网络异常 | 请求超时/网络断开时前端显示错误提示，不崩溃 |
| 并发操作 | 两个 BM 同时编辑同一公寓，后提交者不覆盖先提交者（乐观锁或提示冲突） |
| 未登录访问 | 未登录访问 BM 路由 → 重定向登录页 |
| 非 BM 用户访问 | 租客角色访问 BM 路由 → 重定向首页 |

### 12.4 兼容验收

| 验收项 | 达标条件 |
|--------|----------|
| 浏览器兼容 | Chrome 90+、Edge 90+、Safari 14+ 功能正常 |
| 响应式布局 | 1200px 宽度表格列宽自适应，无横向滚动条溢出 |
| 移动端 | 不低于 768px 宽度下 BM 菜单正常展示（不强制移动端优化） |

---

> **文档结束** — 本文档涵盖 5 个 BM 模块的完整设计，包括数据模型、API 接口、业务逻辑、测试用例、难点分析和验收标准。后续迭代请更新本文档对应章节。
