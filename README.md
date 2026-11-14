# Blog API — 第十五章基础工程

这是第十五章的架构与初始化实现，业务接口目前明确返回 HTTP 501，尚未实现注册登录、角色权限、文章 CRUD、阅读计数回写、注销黑名单和登录限流。相关配置和基础工具已预留。

## Windows 本地启动

需要 Python 3.12（请勿使用系统中旧的 Python 2）。在项目目录执行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
# 仅首次且没有 .env 时复制；SECRET_KEY 应换为随机字符串。
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000/health 和 http://127.0.0.1:8000/docs。
也可使用 `.\.venv\Scripts\fastapi.exe dev app/main.py` 启动。

如果项目已经有本次配置好的 `.venv`、`.env` 和数据库，可以直接运行启动命令。`requirements.txt` 声明依赖范围，`requirements.lock.txt` 保存本次验证过的具体版本。

没有本地 Redis 也能启动：启动日志提示降级，`/health` 的 `redis` 为 false；Redis 正常时为 true。数据库不可连接则启动失败。缓存读取失败返回未命中，业务服务实现时必须查询数据库。

`DEBUG=true` 用于本地查看 SQL 和调试日志；需要验证统一 500 响应时使用 `DEBUG=false`，调试模式会展示框架错误详情。

## 目录和职责

- `app/main.py`：应用工厂、资源生命周期、中间件和健康检查。
- `app/core/`：Settings、JWT/Argon2、异常和日志。
- `app/db/`：公共基类和异步会话；业务模型统一放在 `app/models/`。
- `app/api/v1/`：路由骨架；`schemas/`、`repositories/`、`services/` 为后续业务分层入口。
- `app/utils/`：分页参数和可降级 JSON 缓存工具。
- `alembic/`：从 Settings 读取 URL，导入所有模型；首次迁移创建六张业务表。

## 六表设计

`users` 通过 `author_id` 与 `articles`、`comments` 建立一对多关系；用户角色枚举为 reader/author/admin。`categories` 与 `articles` 一对多，分类删除后文章分类置空。`articles` 用唯一 slug 对外标识，status 区分 draft/published，views 保存持久化阅读数。`tags` 通过 `article_tags` 与文章多对多，关联表以 article_id/tag_id 为联合主键。`comments.parent_id` 自关联形成回复树，删除文章会级联清理评论与关联表；删除父评论会清理回复。

SQLite 运行连接显式打开外键约束。删除有文章或评论的用户会被外键阻止。后续评论服务还需验证回复与父评论属于同一文章。

## 验证与迁移

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic check
```

测试覆盖 Redis 降级/正常连接、OpenAPI、异常格式与响应头、JWT/密码、六表迁移与级联删除、缓存降级。测试数据库使用临时目录。

首次迁移后数据库还有 Alembic 自己的 `alembic_version` 表，属于正常现象。模型变化后执行 `alembic revision --autogenerate -m "描述"`，审查脚本后再执行 `alembic upgrade head`。

## Docker

```powershell
docker compose up --build
```

启动时自动迁移；SQLite 数据位于命名卷，Redis 只在内部网络开放。`.env` 和数据库不会复制进镜像；部署前设置自己的密钥、域名和 CORS 来源。请勿提交 `.env`。

本地启动命令应从项目根目录执行，默认 SQLite 文件是当前目录下的 blog.db。
