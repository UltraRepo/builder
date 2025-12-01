# UltraRepo MCP Marketplace - Enhanced Commercial Plan
## With Token Tracking & Usage-Based Billing

**Domain**: mcp.ultrarepo.com  
**Timeline**: 12 weeks (8 weeks base + 4 weeks commercial features)

---

## 🔗 Technology Resources

### Core Infrastructure
- **Official MCP Registry**: https://github.com/modelcontextprotocol/registry
- **MCP Specification**: https://modelcontextprotocol.io
- **Docker**: https://www.docker.com
- **Docker Compose**: https://docs.docker.com/compose/
- **PostgreSQL**: https://www.postgresql.org
- **Redis**: https://redis.io

### Usage Metering & Billing
- **Lago** (Usage-based billing): https://github.com/getlago/lago | https://www.getlago.com
- **OpenMeter** (Alternative): https://github.com/openmeter/openmeter | https://openmeter.io
- **Stripe Billing**: https://stripe.com/billing
- **Stripe Connect** (Publisher payouts): https://stripe.com/connect

### API Gateway & Token Tracking
- **Kong Gateway**: https://github.com/Kong/kong | https://konghq.com
- **Kong AI Gateway**: https://konghq.com/products/kong-ai-gateway
- **Apache APISIX** (Alternative): https://github.com/apache/apisix
- **Tyk** (Alternative): https://github.com/TykTechnologies/tyk

### Monitoring & Analytics
- **TimescaleDB**: https://github.com/timescale/timescaledb | https://www.timescale.com
- **Grafana**: https://github.com/grafana/grafana | https://grafana.com
- **Prometheus**: https://github.com/prometheus/prometheus | https://prometheus.io
- **Loki** (Logging): https://github.com/grafana/loki

### Web Development
- **React**: https://react.dev
- **Vite**: https://vitejs.dev
- **Next.js** (Alternative): https://nextjs.org
- **Tailwind CSS**: https://tailwindcss.com
- **shadcn/ui**: https://ui.shadcn.com

### Backend
- **FastAPI**: https://fastapi.tiangolo.com
- **Go**: https://go.dev
- **Python**: https://www.python.org

### Additional Tools
- **Nginx**: https://nginx.org
- **Let's Encrypt** (SSL): https://letsencrypt.org
- **Certbot**: https://certbot.eff.org

---

## 🎯 Overview

Extended marketplace supporting **three revenue models**:
1. **Free/Open Source** - Community MCPs (no cost)
2. **Paid License** - One-time purchase ($29-$99)
3. **Usage-Based** - Token metering + pay-per-use ($0.001/1K tokens)

---

## 🏗️ Enhanced Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  mcp.ultrarepo.com (Linux)                    │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  Registry  │  │    Lago    │  │   Stripe   │             │
│  │    (Go)    │  │  Metering  │  │  Payments  │             │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘             │
│         │                │                 │                  │
│  ┌──────▼────────────────▼─────────────────▼────┐            │
│  │         API Gateway (Kong AI Gateway)        │            │
│  │  - Token counting for all MCP traffic        │            │
│  │  - Request/response interception             │            │
│  │  - Cost calculation per consumer              │            │
│  │  - Usage event streaming to Lago              │            │
│  └─────────────────────────┬────────────────────┘            │
│                             │                                 │
│  ┌──────────────────────────▼───────────────────────┐        │
│  │         Commercial Services (FastAPI)            │        │
│  │  - Payment processing                            │        │
│  │  - License management                            │        │
│  │  - Publisher dashboards                          │        │
│  │  - Consumer usage analytics                      │        │
│  └─────────────────────────┬────────────────────────┘        │
│                             │                                 │
│  ┌──────────────┬───────────▼──────────┬────────────┐        │
│  │  PostgreSQL  │     TimescaleDB      │   Redis    │        │
│  │  (Registry)  │  (Usage Metrics)     │  (Cache)   │        │
│  └──────────────┴──────────────────────┴────────────┘        │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 Technology Stack Additions

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Usage Metering** | Lago (open source) | Event ingestion, billing aggregation |
| **AI Gateway** | Kong AI Gateway + Plugin | Token counting for MCP traffic |
| **Time-Series DB** | TimescaleDB | Store usage metrics efficiently |
| **Analytics** | Grafana + Prometheus | Real-time dashboards |
| **Queue** | Redis Streams | Event buffer for Lago |

---

## 🔢 Token Tracking Architecture

### **1. Kong AI Gateway - Traffic Interception**

Kong sits between UltraRepo Client and MCP servers, counting every token:

```lua
-- kong/plugins/mcp-token-counter/handler.lua
local TokenCounterHandler = {
  VERSION = "1.0.0",
  PRIORITY = 1000,
}

function TokenCounterHandler:access(conf)
  -- Record request metadata
  kong.ctx.shared.start_time = ngx.now()
  kong.ctx.shared.consumer_id = kong.client.get_consumer().id
  kong.ctx.shared.mcp_server_id = kong.router.get_service().id
end

function TokenCounterHandler:body_filter(conf)
  local ctx = kong.ctx.shared
  local response_body = kong.response.get_raw_body()
  
  -- Extract token count from MCP response
  local tokens_used = extract_token_count(response_body)
  
  -- Send usage event to Lago
  send_to_lago({
    consumer_id = ctx.consumer_id,
    mcp_server_id = ctx.mcp_server_id,
    tokens_input = tokens_used.input,
    tokens_output = tokens_used.output,
    total_tokens = tokens_used.total,
    latency_ms = (ngx.now() - ctx.start_time) * 1000,
    timestamp = os.time()
  })
end

return TokenCounterHandler
```

### **2. Lago Integration - Usage Events**

```python
# services/commercial/lago_client.py
from lago_python_client import Client
from lag0_python_client.models import Event

lago_client = Client(api_key=os.getenv('LAGO_API_KEY'))

def send_usage_event(
    consumer_id: str,
    package_id: str,
    tokens_used: int,
    timestamp: int
):
    """Send token usage to Lago for billing"""
    event = Event(
        transaction_id=f"mcp_{consumer_id}_{timestamp}",
        external_customer_id=consumer_id,
        code="mcp_tokens",  # Billable metric name
        properties={
            "package_id": package_id,
            "tokens_input": tokens_used["input"],
            "tokens_output": tokens_used["output"],
            "total_tokens": tokens_used["total"]
        }
    )
    
    lago_client.events.create(event)
```

### **3. Pricing Plans in Lago**

```python
# Configure pricing in Lago dashboard or via API
from lago_python_client.models import Plan, Charge

# Create usage-based plan
plan = Plan(
    name="MCP Usage Plan",
    code="mcp_usage",
    interval="monthly",
    charges=[
        Charge(
            billable_metric_code="mcp_tokens",
            charge_model="graduated",  # Tiered pricing
            properties={
                "graduated_ranges": [
                    {
                        "from_value": 0,
                        "to_value": 100000,
                        "per_unit_amount": "0.002"  # $0.002 per 1K tokens
                    },
                    {
                        "from_value": 100001,
                        "to_value": 1000000,
                        "per_unit_amount": "0.0015"  # Volume discount
                    },
                    {
                        "from_value": 1000001,
                        "to_value": None,
                        "per_unit_amount": "0.001"  # Best rate
                    }
                ]
            }
        )
    ]
)

lago_client.plans.create(plan)
```

---

## 🗄️ Enhanced Database Schema

```sql
-- Package pricing models
CREATE TABLE package_pricing (
    package_id UUID REFERENCES mcp_packages(id),
    pricing_type VARCHAR(50) NOT NULL,  -- 'free', 'license', 'usage', 'hybrid'
    
    -- License pricing
    license_price DECIMAL(10,2),
    
    -- Usage-based pricing
    cost_per_1k_tokens DECIMAL(8,5),
    minimum_monthly_spend DECIMAL(10,2),
    
    -- Lago integration
    lago_plan_code VARCHAR(255),
    lago_metric_code VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (package_id)
);

-- Consumer subscriptions (for usage billing)
CREATE TABLE consumer_subscriptions (
    id UUID PRIMARY KEY,
    consumer_id UUID REFERENCES users(id),
    package_id UUID REFERENCES mcp_packages(id),
    stripe_subscription_id VARCHAR(255),
    lago_external_subscription_id VARCHAR(255),
    status VARCHAR(50),  -- 'active', 'paused', 'cancelled'
    started_at TIMESTAMP DEFAULT NOW(),
    cancelled_at TIMESTAMP
);

-- Usage metrics (TimescaleDB hypertable)
CREATE TABLE usage_metrics (
    time TIMESTAMPTZ NOT NULL,
    consumer_id UUID NOT NULL,
    package_id UUID NOT NULL,
    mcp_server_id VARCHAR(255),
    
    tokens_input INT NOT NULL,
    tokens_output INT NOT NULL,
    total_tokens INT NOT NULL,
    
    latency_ms FLOAT,
    request_id VARCHAR(255),
    
    -- Cost calculation
    cost_usd DECIMAL(10,6),
    
    PRIMARY KEY (time, consumer_id, package_id)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('usage_metrics', 'time');

-- Continuous aggregates for fast queries
CREATE MATERIALIZED VIEW usage_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS day,
    consumer_id,
    package_id,
    SUM(total_tokens) AS tokens_total,
    SUM(cost_usd) AS cost_total,
    COUNT(*) AS request_count
FROM usage_metrics
GROUP BY day, consumer_id, package_id;
```

---

## 📊 Publisher & Consumer Dashboards

### **Publisher Dashboard APIs**

```python
# services/commercial/publisher_api.py

@app.get("/publisher/{publisher_id}/analytics")
async def get_publisher_analytics(
    publisher_id: str,
    start_date: date,
    end_date: date,
    db: Session
):
    """Publisher can see their package usage and revenue"""
    
    # Get all packages by this publisher
    packages = db.query(PaidPackage).filter_by(
        publisher_id=publisher_id
    ).all()
    
    # Aggregate usage across all packages
    usage = db.execute("""
        SELECT 
            package_id,
            DATE_TRUNC('day', time) as date,
            SUM(total_tokens) as tokens_used,
            SUM(cost_usd) as revenue,
            COUNT(DISTINCT consumer_id) as unique_users
        FROM usage_metrics
        WHERE package_id IN :package_ids
        AND time BETWEEN :start_date AND :end_date
        GROUP BY package_id, date
        ORDER BY date DESC
    """, {
        "package_ids": tuple(p.package_id for p in packages),
        "start_date": start_date,
        "end_date": end_date
    }).fetchall()
    
    return {
        "period": {"start": start_date, "end": end_date},
        "total_revenue": sum(row.revenue for row in usage),
        "total_tokens": sum(row.tokens_used for row in usage),
        "unique_consumers": len(set(row.unique_users for row in usage)),
        "daily_breakdown": [
            {
                "date": row.date,
                "tokens": row.tokens_used,
                "revenue": row.revenue,
                "users": row.unique_users
            }
            for row in usage
        ]
    }
```

### **Consumer Dashboard APIs**

```python
@app.get("/consumer/{consumer_id}/usage")
async def get_consumer_usage(
    consumer_id: str,
    month: str,  # YYYY-MM
    db: Session
):
    """Consumer can see their token usage and costs"""
    
    usage = db.execute("""
        SELECT 
            package_id,
            p.name as package_name,
            SUM(total_tokens) as tokens_used,
            SUM(cost_usd) as cost,
            COUNT(*) as request_count
        FROM usage_metrics um
        JOIN mcp_packages p ON um.package_id = p.id
        WHERE consumer_id = :consumer_id
        AND DATE_TRUNC('month', time) = :month
        GROUP BY package_id, p.name
    """, {
        "consumer_id": consumer_id,
        "month": month + "-01"
    }).fetchall()
    
    # Get current Lago invoice (if exists)
    lago_invoice = lago_client.invoices.find_all(
        external_customer_id=consumer_id,
        status="draft"
    )
    
    return {
        "month": month,
        "packages": [
            {
                "package_id": row.package_id,
                "package_name": row.package_name,
                "tokens_used": row.tokens_used,
                "estimated_cost": row.cost,
                "requests": row.request_count
            }
            for row in usage
        ],
        "total_cost": sum(row.cost for row in usage),
        "total_tokens": sum(row.tokens_used for row in usage),
        "lago_invoice": lago_invoice[0] if lago_invoice else None
    }
```

---

## 💸 Billing Flow

### **Monthly Billing with Lago + Stripe**

```
Day 1-30: 
  ├─ Kong intercepts MCP traffic
  ├─ Sends token usage to Lago
  └─ Lago aggregates usage per consumer

Day 31 (Month End):
  ├─ Lago generates invoices
  ├─ Calls Stripe to charge consumers
  ├─ Consumer receives invoice email
  └─ Charges consumer's payment method

Day 1-5 (Next Month):
  ├─ Calculate publisher earnings
  ├─ Deduct marketplace fee (30%)
  └─ Transfer to publisher (Stripe Connect)
```

---

## 📈 Real-Time Monitoring

### **Grafana Dashboards**

```yaml
# grafana/dashboards/mcp-usage.json
{
  "dashboard": {
    "title": "MCP Marketplace - Live Usage",
    "panels": [
      {
        "title": "Tokens per Second",
        "targets": [{
          "expr": "rate(mcp_tokens_total[1m])",
          "datasource": "Prometheus"
        }]
      },
      {
        "title": "Top Consumers by Usage",
        "targets": [{
          "rawQuery": "SELECT consumer_id, SUM(total_tokens) FROM usage_metrics WHERE time > NOW() - INTERVAL '1 hour' GROUP BY consumer_id ORDER BY 2 DESC LIMIT 10"
        }]
      },
      {
        "title": "Revenue Today",
        "targets": [{
          "rawQuery": "SELECT SUM(cost_usd) FROM usage_metrics WHERE time::date = CURRENT_DATE"
        }]
      }
    ]
  }
}
```

---

## 🔐 Fair Usage & Abuse Prevention

```python
# Kong rate limiting based on token budget
@app.before_request
async def check_token_budget():
    consumer_id = get_consumer_id()
    package_id = get_package_id()
    
    # Check monthly token limit
    usage_this_month = db.execute("""
        SELECT SUM(total_tokens) 
        FROM usage_metrics
        WHERE consumer_id = :consumer_id
        AND package_id = :package_id
        AND time >= DATE_TRUNC('month', NOW())
    """, {"consumer_id": consumer_id, "package_id": package_id}).scalar()
    
    # Get package limit
    package = db.query(PackagePricing).get(package_id)
    
    if usage_this_month >= package.monthly_token_limit:
        raise HTTPException(429, "Monthly token limit exceeded")
```

---

## 📦 Docker Compose Update

```yaml
version: '3.8'
services:
  # Existing services...
  
  # Kong AI Gateway
  kong:
    image: kong/kong-gateway:3.5
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_DATABASE: kong
      KONG_PLUGINS: bundled,mcp-token-counter
    volumes:
      - ./kong/plugins:/usr/local/share/lua/5.1/kong/plugins
    ports:
      - "8000:8000"  # Proxy
      - "8001:8001"  # Admin API
    depends_on:
      - postgres

  # Lago (Usage Metering)
  lago_api:
    image: getlago/api:latest
    environment:
      DATABASE_URL: postgresql://lago:password@postgres:5432/lago
      REDIS_URL: redis://redis:6379
      LAGO_API_URL: https://mcp.ultrarepo.com/lago
      SECRET_KEY_BASE: ${LAGO_SECRET}
    depends_on:
      - postgres
      - redis

  lago_worker:
    image: getlago/api:latest
    command: bundle exec sidekiq
    environment:
      DATABASE_URL: postgresql://lago:password@postgres:5432/lago
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  # TimescaleDB (time-series metrics)
  timescale:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_DB: metrics
      POSTGRES_USER: timescale
      POSTGRES_PASSWORD: password
    volumes:
      - timescale_data:/var/lib/postgresql/data

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    volumes:
      - ./grafana:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana

volumes:
  timescale_data:
  grafana_data:
```

---

## 🗓️ Implementation Timeline

### **Weeks 1-8**: Base Marketplace (as planned)

### **Weeks 9-10**: Kong & Token Tracking
- [ ] Deploy Kong AI Gateway container
- [ ] Create MCP token counter plugin
- [ ] Configure Kong upstream to MCP servers
- [ ] Test token counting accuracy
- [ ] Deploy TimescaleDB for metrics

### **Weeks 11-12**: Lago & Commercial Features
- [ ] Deploy Lago containers (API + Worker)
- [ ] Configure Lago plans and metrics
- [ ] Integrate Kong → Lago event pipeline
- [ ] Build publisher dashboard
- [ ] Build consumer usage dashboard
- [ ] Set up Grafana monitoring
- [ ] Configure Stripe Connect for publishers
- [ ] Test end-to-end billing flow

---

## 💰 Cost Estimates (Enhanced)

**Monthly Infrastructure** (Production):
- Linux VPS (8GB RAM, 4 vCPU): **$48/month**
- TimescaleDB managed: **$50/month** (or self-hosted: $0)
- Lago self-hosted: **$0** (open source)
- Stripe fees: **2.9% + $0.30 per transaction**
- Total: **~$98-148/month**

**Revenue Potential**:
- 100 paying consumers × $50/month = **$5,000/month**
- Marketplace fee (30%) = **$1,500/month**
- Publisher payout (70%) = **$3,500/month**

---

## 🎯 Key Advantages

✅ **Open Source Metering**: Lago = no vendor lock-in  
✅ **Real-Time Tracking**: Know costs instantly  
✅ **Fair Pricing**: Pay only for what you use  
✅ **Publisher Transparency**: Full analytics access  
✅ **Consumer Control**: Set budgets & alerts  
✅ **Scalable**: Lago handles 15K events/sec  

