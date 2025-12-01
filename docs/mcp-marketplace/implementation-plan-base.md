# UltraRepo MCP Marketplace - Implementation Plan
## Based on modelcontextprotocol/registry

**Domain**: mcp.ultrarepo.com  
**Base**: https://github.com/modelcontextprotocol/registry (Official MCP Registry - Go)  
**Timeline**: 8 weeks to production

---

## 🎯 Project Overview

Building a self-hosted MCP marketplace for UltraRepo by extending the official `modelcontextprotocol/registry` with:
- YAML transformation layer (KiloCode/UltraRepo compatibility)
- Web UI for browsing and discovery
- GitHub integration for package submissions
- Linux deployment on mcp.ultrarepo.com

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              mcp.ultrarepo.com (Linux Server)            │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Web UI      │  │ YAML Adapter │  │  MCP Registry│  │
│  │ (React SPA)  │  │  (FastAPI)   │  │     (Go)     │  │
│  │  Port 3000   │  │  Port 8001   │  │  Port 8080   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
│         └──────────────────┼──────────────────┘          │
│                            │                             │
│  ┌─────────────────────────▼──────────────────────┐     │
│  │           Nginx Reverse Proxy                  │     │
│  │  - SSL/TLS (Let's Encrypt)                     │     │
│  │  - Static file serving                         │     │
│  │  - Route /api/* to adapters                    │     │
│  └────────────────────────────────────────────────┘     │
│                                                           │
│  ┌──────────────┬────────────────┬──────────────┐       │
│  │  PostgreSQL  │   Redis Cache  │    GitHub    │       │
│  │  (Registry)  │   (Adapter)    │   (Source)   │       │
│  └──────────────┴────────────────┴──────────────┘       │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Component Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Core Registry** | Go (existing) | Official MCP server registry |
| **YAML Adapter** | Python/FastAPI | Transform JSON → YAML for UltraRepo |
| **Web UI** | React + Vite | Browse packages, search, view details |
| **Reverse Proxy** | Nginx | SSL, routing, static files |
| **Database** | PostgreSQL | Registry data (existing) |
| **Cache** | Redis | YAML caching, rate limiting |
| **Deployment** | Docker Compose | Container orchestration |

---

## 🔌 API Architecture

### Existing Registry Endpoints (Keep)
```
GET  /servers                  # List all MCP servers (JSON)
GET  /servers/{id}             # Get specific server (JSON)
POST /servers                  # Register new server
GET  /health                   # Health check
```

### New YAML Adapter Endpoints (Add)
```
GET  /api/v1/marketplace/mcps     # KiloCode-compatible YAML
GET  /api/v1/marketplace/modes    # Custom modes (YAML)
GET  /api/v1/search               # Enhanced search
GET  /api/v1/stats                # Statistics
```

### Web UI Routes (New)
```
/                                 # Homepage with package grid
/package/{id}                     # Package detail page
/search?q=...                     # Search results
/submit                           # Package submission guide
```

---

## 🛠️ YAML Adapter Service

**Purpose**: Transform the official registry's JSON API to YAML format for UltraRepo compatibility.

```python
# services/yaml-adapter/main.py
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import httpx
import yaml
from redis import Redis

app = FastAPI()
redis_client = Redis(host='redis', port=6379, decode_responses=True)

@app.get("/api/v1/marketplace/mcps", response_class=PlainTextResponse)
async def get_mcps_yaml():
    # Check cache
    cached = redis_client.get("mcps_yaml")
    if cached:
        return cached
    
    # Fetch from Go registry
    async with httpx.AsyncClient() as client:
        response = await client.get("http://registry:8080/servers")
        servers = response.json()
    
    # Transform to KiloCode format
    marketplace = {
        "items": [
            {
                "id": s["id"],
                "name": s["name"],
                "description": s["description"],
                "author": s.get("author"),
                "authorUrl": s.get("author_url"),
                "url": s["repository_url"],
                "tags": s.get("tags", []),
                "content": s.get("installation_config"),
                "parameters": s.get("parameters", [])
            }
            for s in servers
        ]
    }
    
    # Convert to YAML
    yaml_output = yaml.dump(marketplace, default_flow_style=False)
    
    # Cache for 5 minutes
    redis_client.setex("mcps_yaml", 300, yaml_output)
    
    return yaml_output
```

---

## 🎨 Web UI Features

### Homepage
- **Package Grid**: Cards with name, description, author, tags
- **Search Bar**: Full-text search
- **Category Filters**: Filter by tags
- **Featured Section**: Highlighted packages
- **Stats**: Total packages, downloads

### Package Detail Page
- **Metadata**: Name, author, description, repository link
- **Installation**: Copy-paste config with syntax highlighting
- **Prerequisites**: Required dependencies
- **Usage Examples**: Code snippets
- **Related Packages**: Recommendations

### Tech Stack
```json
{
  "framework": "React 18 + Vite",
  "ui": "Tailwind CSS + shadcn/ui",
  "routing": "React Router",
  "api": "TanStack Query",
  "syntax": "Prism.js for code highlighting"
}
```

---

## 📋 Deployment Configuration

### Docker Compose (Production)

```yaml
version: '3.8'

services:
  # Official MCP Registry (Go)
  registry:
    image: ghcr.io/modelcontextprotocol/registry:latest
    container_name: mcp-registry
    environment:
      - DATABASE_URL=postgresql://mcp:password@postgres:5432/registry
      - PORT=8080
    depends_on:
      - postgres
    restart: unless-stopped

  # YAML Adapter (Python/FastAPI)
  adapter:
    build: ./services/yaml-adapter
    container_name: mcp-adapter
    environment:
      - REGISTRY_URL=http://registry:8080
      - REDIS_URL=redis://redis:6379
    ports:
      - "8001:8001"
    depends_on:
      - registry
      - redis
    restart: unless-stopped

  # Web UI (React)
  web:
    build: ./web-ui
    container_name: mcp-web
    environment:
      - VITE_API_URL=https://mcp.ultrarepo.com
    volumes:
      - ./web-ui/dist:/usr/share/nginx/html:ro
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: mcp-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./web-ui/dist:/var/www/html:ro
    depends_on:
      - registry
      - adapter
      - web
    restart: unless-stopped

  # PostgreSQL (Registry Database)
  postgres:
    image: postgres:16-alpine
    container_name: mcp-postgres
    environment:
      - POSTGRES_DB=registry
      - POSTGRES_USER=mcp
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis (Caching)
  redis:
    image: redis:7-alpine
    container_name: mcp-redis
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Nginx Configuration

```nginx
# /nginx/nginx.conf
server {
    listen 80;
    server_name mcp.ultrarepo.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mcp.ultrarepo.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # Web UI (static files)
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    # YAML Adapter API
    location /api/v1/ {
        proxy_pass http://adapter:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Official Registry API (passthrough)
    location /servers {
        proxy_pass http://registry:8080;
        proxy_set_header Host $host;
    }
}
```

---

## 🚀 8-Week Implementation Plan

### Week 1-2: Foundation
- [x] Fork/clone modelcontextprotocol/registry
- [x] Deploy registry with Docker on test server
- [x] Set up PostgreSQL database
- [x] Verify basic registry functionality
- [x] Configure domain (mcp.ultrarepo.com)
- [x] Set up SSL with Let's Encrypt

### Week 3-4: YAML Adapter
- [x] Create FastAPI adapter service
- [x] Implement JSON → YAML transformation
- [x] Add Redis caching layer
- [x] Build /api/v1/marketplace/mcps endpoint
- [x] Test with UltraRepo client
- [x] Deploy adapter container

### Week 5-6: Web UI
- [x] Set up React + Vite project
- [x] Install Tailwind CSS + shadcn/ui
- [x] Build homepage with package grid
- [x] Create package detail pages
- [x] Implement search functionality
- [x] Add category filtering
- [x] Deploy static build

### Week 7: Integration & Testing
- [x] Configure Nginx reverse proxy
- [x] Set up Docker Compose orchestration
- [x] End-to-end testing
- [x] Performance optimization
- [x] Security hardening
- [x] Documentation

### Week 8: Launch
- [x] Production deployment
- [x] DNS configuration
- [x] Monitoring setup (Prometheus/Grafana)
- [x] Backup configuration
- [x] Launch announcement
- [x] Initial package seeding

---

## 🔐 Security Considerations

1. **SSL/TLS**: Let's Encrypt auto-renewal
2. **Rate Limiting**: Redis-based (100 req/min per IP)
3. **CORS**: Restrict to ultrarepo.com domains
4. **Input Validation**: Pydantic models in adapter
5. **Container Security**: Non-root users, read-only filesystems
6. **Database**: Strong passwords, no public exposure

---

## 📊 Success Metrics

- **Uptime**: 99.9% availability
- **Response Time**: <100ms for cached YAML
- **Package Count**: 20+ at launch, 50+ in 3 months
- **UltraRepo Integration**: Seamless client compatibility
- **Community**: 100+ unique users in first month

---

## 💰 Infrastructure Costs

**Linux VPS** (DigitalOcean/Linode):
- 4GB RAM, 2 vCPU, 80GB SSD: **$24/month**
- Domain: **$12/year**
- SSL: **Free** (Let's Encrypt)

**Total**: ~$26/month

---

## 🎯 Key Advantages

✅ **Leverage Official Code**: Start with production-ready registry  
✅ **Fast Time to Market**: 8 weeks vs 16 weeks from scratch  
✅ **MCP Compatibility**: Official protocol support  
✅ **Community Backed**: Updates from Anthropic/GitHub/Microsoft  
✅ **Low Maintenance**: Minimal custom code to maintain  

---

## 📚 Repository Structure

```
ultrarepo-mcp-marketplace/
├── registry/                    # Git submodule: official registry
├── services/
│   └── yaml-adapter/           # FastAPI YAML transformation
│       ├── app/
│       ├── Dockerfile
│       └── requirements.txt
├── web-ui/                     # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── nginx/
│   ├── nginx.conf
│   └── ssl/
├── docker-compose.yml
└── README.md
```
