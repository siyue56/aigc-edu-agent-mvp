# 高校学习智能体AIGC应用 - 部署指南 (Phase 1 MVP)

本文档提供将项目部署到公网云服务器（例如 IP: `81.71.2.37`）的完整操作指南，包含环境变量清单、CI/CD 自动化部署配置、生产域名 HTTPS 证书申请等必要步骤。

## 1. 目标服务器准备 (IP: `81.71.2.37`)

### 1.1 环境依赖安装
通过 SSH 连接到服务器 `81.71.2.37`：
```bash
ssh root@81.71.2.37
```

安装基础运行环境（以 Ubuntu/Debian 为例）：
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装 Git、Curl 和 Nginx（用于反向代理与 HTTPS）
sudo apt install -y git curl nginx

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 1.2 开放安全组 / 防火墙端口
请确保您的云服务器控制台（如阿里云、腾讯云等）安全组中放行了以下端口：
* **80** (HTTP) - 用于 Web 访问和 Let's Encrypt 证书申请
* **443** (HTTPS) - 用于加密 Web 访问
* **8000** (可选) - 仅在不经过 Nginx 直接访问后端 API 时开放
* **22** (SSH) - 远程连接

---

## 2. 部署流程与环境变量配置

### 2.1 克隆代码与目录初始化
```bash
# 建议在 /opt 或 /var/www 目录下存放项目
cd /opt
git clone https://github.com/siyue56/aigc-edu-agent-mvp.git
cd aigc-edu-agent-mvp
```

### 2.2 环境变量清单与密钥注入
本项目采用 Docker Secrets 注入敏感信息。需要在部署前创建相关密钥文件：

```bash
# 创建 secrets 目录
mkdir -p secrets

# 1. JWT 加密密钥 (必须配置，建议使用随机强密码)
# 例如生成一个 32 位的随机字符串：
openssl rand -hex 32 > secrets/jwt_secret.txt

# 2. 如果未来接入 OpenAI，可以在此处配置模型 API Key
echo "sk-your-openai-api-key" > secrets/openai_api_key.txt
```

**核心环境变量清单（在 `docker-compose.yml` 中定义）：**
| 变量名 | 默认值 / 参考值 | 说明 |
| :--- | :--- | :--- |
| `POSTGRES_USER` | `postgres` | 数据库超级用户名称 |
| `POSTGRES_PASSWORD` | `postgrespassword` | 数据库密码（建议生产环境修改） |
| `POSTGRES_DB` | `aigc_db` | 核心业务数据库名 |
| `SECRET_KEY` | `/run/secrets/jwt_secret` | 后端读取 JWT 密钥的文件挂载路径 |

### 2.3 启动服务
```bash
# 赋权并执行一键部署脚本
chmod +x deploy.sh
./deploy.sh
```
部署完成后，可以通过 `http://81.71.2.37` 访问前端页面，`http://81.71.2.37:8000/docs` 访问后端 API 文档。

---

## 3. 生产域名 HTTPS 证书申请步骤

为了保障数据安全和微信小程序合法请求，生产环境必须配置 HTTPS。我们将使用 Nginx + Certbot 自动签发 Let's Encrypt 免费证书。

### 3.1 域名解析
前往您的域名服务商控制台，添加一条 `A` 记录，将您的域名（例如 `agent.example.com`）指向公网 IP `81.71.2.37`。

### 3.2 配置 Nginx 反向代理
在服务器 `/etc/nginx/sites-available/` 下创建配置文件 `aigc-agent`：

```nginx
server {
    listen 80;
    server_name agent.example.com; # 替换为您的域名

    # 代理前端 Web (Docker 映射端口 80 -> 本地实际端口可以改为 3000 避免冲突)
    # 假设我们在 docker-compose.yml 中将 web 端口改为了 3000:80
    location / {
        proxy_pass http://127.0.0.1:80; 
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 代理后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/aigc-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3.3 申请与配置 HTTPS 证书
```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 一键申请证书并自动配置 Nginx
sudo certbot --nginx -d agent.example.com

# 测试证书自动续期
sudo certbot renew --dry-run
```

---

## 4. CI/CD 配置示例

### 选项 A：GitLab Runner 配置示例 (按需)
在项目根目录创建 `.gitlab-ci.yml`：
```yaml
stages:
  - deploy

deploy_production:
  stage: deploy
  script:
    - ssh root@81.71.2.37 "cd /opt/aigc-edu-agent-mvp && git pull origin main && ./deploy.sh"
  only:
    - main
```

### 选项 B：GitHub Actions 配置示例 (推荐，因为项目已推送到 GitHub)
在项目目录 `.github/workflows/deploy.yml` 中添加：
```yaml
name: Deploy to Cloud Server

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Server via SSH
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: 81.71.2.37
          username: root
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /opt/aigc-edu-agent-mvp
            git pull origin main
            ./deploy.sh
```
*注意：需要在 GitHub 仓库的 `Settings -> Secrets and variables -> Actions` 中配置 `SERVER_SSH_KEY`（服务器的私钥）。*
