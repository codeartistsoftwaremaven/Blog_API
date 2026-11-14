# 第十五章补充位置

项目位置：`D:\Maestro\Blog_API`。

## 修改原有文件

| 文件 | 补充内容 |
| --- | --- |
| `app/main.py` | 应用工厂、全部路由注册、日志初始化、数据库启动检查、Redis 初始化/关闭/降级、请求 ID、健康检查、可配置 CORS/Host |
| `app/core/config.py` | 版本、JWT 配置、缓存 TTL、阅读计数阈值、登录限流参数、Redis 超时、允许的域名和来源；根目录 .env 读取 |
| `app/core/security.py` | 统一使用 Settings 密钥；JWT 包含 sub/iat/exp/jti，解码校验必需字段；保留 Argon2 密码工具 |
| `app/core/exceptions.py` | 在已有四处理器基础上，为兜底 500 响应保留请求 ID，并消除新版框架状态码常量的弃用警告 |
| `app/db/base.py` | 只保留公共基类/时间戳和约束命名，移走混入的业务模型 |
| `app/db/session.py` | 异步会话、异常回滚、SQLite 外键启用 |
| `app/models/user.py` | 用户模型、三级角色枚举与关系 |
| `app/models/article.py` | 分类、标签、文章、article_tags 联合主键及关系 |
| `app/models/comment.py` | 评论、自关联回复与级联删除 |
| `app/api/v1/auth.py` | 注册、登录、注销路由骨架 |
| `app/api/v1/users.py` | 用户资料、资料修改、用户列表路由骨架 |
| `app/api/v1/articles.py` | 文章列表、slug 详情、创建、修改、删除路由骨架 |
| `app/api/v1/categories.py` | 分类和标签路由骨架 |
| `app/api/v1/comments.py` | 评论列表、创建/回复、删除路由骨架 |
| `app/deps.py` | 数据库与可空 Redis 依赖 |
| `.env.example` | 完整配置模板 |
| `requirements.txt` | 直接依赖和兼容范围 |
| `Dockerfile` | 镜像构建、非 root 运行和启动时迁移 |
| `pytest.ini` | 测试路径和异步测试配置 |

原有 `app/core/logging.py` 保留，现已由应用启动流程调用。

## 新增文件

- `app/models/__init__.py`：集中导入所有模型，供 Alembic 发现六表。
- `app/` 及各层必要的 `__init__.py`：明确包和分层入口。
- `app/schemas/common.py`：统一错误响应模型。
- `app/utils/redis_cache.py`：可降级 JSON 缓存读写工具。
- `app/utils/pagination.py`：带边界校验的分页参数。
- `alembic.ini`、`alembic/env.py`、`alembic/script.py.mako`：迁移环境。
- `alembic/versions/0001_init_schema.py`：六表首次迁移及回退。
- `.env`：首次生成随机密钥的本地配置；已有 .env 会保留。
- `.gitignore`、`.dockerignore`：排除密钥、数据库、虚拟环境和备份。
- `docker-compose.yml`：应用、Redis、数据库持久化与健康检查。
- `requirements.lock.txt`：本次测试通过的依赖版本。
- `tests/conftest.py`、`tests/test_foundation.py`、`tests/test_migrations.py`：基础测试。
- `README.md`：启动、验收、六表关系和后续范围说明。

## 范围

此处完成第十五章的架构与初始化。业务路由明确返回 501；完整业务输入输出模型、Repository/Service 实现、注册登录、RBAC、文章/评论 CRUD、阅读计数回写、登录限流和注销黑名单由后续章节继续实现。favorites 收藏表是选做挑战，本次没有增加。

## 原文件备份

本次被替换的非空源文件会在 `.chapter15-backups/` 下按时间建立备份。虚拟环境、SQLite 数据库和备份文件均不提交到版本库。

## 验证结果

- Python 3.12.14 下 6 项 pytest 测试全部通过。
- 覆盖数据库迁移/回退/再次迁移、模型与数据库结构一致性、联合主键防重复、评论及文章级联删除。
- 覆盖无 Redis 启动与降级、模拟 Redis 正常及断连、文档与路由、请求 ID、四类异常、JWT 和 Argon2、缓存失败回退。
- Compose 配置通过 YAML 结构检查；本机未运行 Docker 构建，也未启动真实 Redis 服务。
