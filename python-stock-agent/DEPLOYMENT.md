# Deployment Guide - Python Stock Agent

## Pre-Deployment Setup

### 1. Prerequisites
- Node.js and npm installed
- Wrangler CLI (comes with npm install)
- Cloudflare account with Workers enabled
- API keys for integrations (see below)

### 2. API Keys Required

#### Required
- **Swarms AI API Key**: Get from [https://swarms.ai](https://swarms.ai)
  ```bash
  wrangler secret put SWARMS_API_KEY
  ```

#### Optional (but recommended)
- **Financial Modeling Prep API**: For market news
  ```bash
  wrangler secret put FMP_API_KEY
  ```

- **Mailgun**: For email reports
  ```bash
  wrangler secret put MAILGUN_API_KEY
  wrangler secret put MAILGUN_DOMAIN
  wrangler secret put RECIPIENT_EMAIL
  ```

## Development Workflow

### 1. Local Development
```bash
# Install dependencies
npm install

# Copy environment template
cp .dev.vars.example .dev.vars
# Edit .dev.vars with your API keys

# Start development server
npm run dev
```

### 2. Testing Endpoints
- **Dashboard**: http://localhost:8787
- **Status**: http://localhost:8787/status  
- **Manual Trigger**: http://localhost:8787/trigger
- **Cron Test**: http://localhost:8787/__scheduled?cron=0+*+*+*+*

### 3. Test Scheduled Events
```bash
npm run test
# Then visit the cron endpoint above
```

## Deployment Steps

### 1. Validate Configuration
```bash
# Check wrangler configuration
wrangler whoami
wrangler config list
```

### 2. Set Production Secrets
```bash
# Required
wrangler secret put SWARMS_API_KEY

# Optional
wrangler secret put FMP_API_KEY
wrangler secret put MAILGUN_API_KEY
wrangler secret put MAILGUN_DOMAIN  
wrangler secret put RECIPIENT_EMAIL
```

### 3. Deploy to Cloudflare
```bash
npm run deploy
```

### 4. Verify Deployment
- Check the deployment URL provided by Wrangler
- Test the dashboard interface
- Verify cron triggers in Cloudflare dashboard
- Monitor logs for any errors

## Post-Deployment Monitoring

### 1. Cloudflare Dashboard
- Navigate to Workers & Pages
- Select your `python-stock-agent`
- Check:
  - ✅ Real-time logs
  - ✅ Analytics/metrics
  - ✅ Cron trigger history
  - ✅ Resource usage

### 2. Test Production Endpoints
```bash
# Replace YOUR_WORKER_URL with actual URL
curl https://python-stock-agent.YOUR_ACCOUNT.workers.dev/status
curl -X GET https://python-stock-agent.YOUR_ACCOUNT.workers.dev/trigger
```

### 3. Monitor Scheduled Executions
- Cron triggers run every 3 hours: `0 */3 * * *`
- Check execution logs in Cloudflare dashboard
- Verify email reports if configured

## Troubleshooting

### Common Issues

1. **Python Workers Beta Flag Missing**
   - Ensure `"compatibility_flags": ["python_workers"]` in wrangler.jsonc
   - Use compatibility_date >= "2024-03-20"

2. **API Key Issues**
   ```bash
   # List all secrets
   wrangler secret list
   
   # Update a secret
   wrangler secret put SWARMS_API_KEY
   ```

3. **Import Errors in Python**
   - Python Workers use Pyodide runtime
   - Some Python packages may not be available
   - Use `from workers import Response, fetch` for Cloudflare APIs

4. **Timeout Issues**
   - Yahoo Finance API calls have 8-second timeout
   - News API calls have 10-second timeout
   - Consider reducing symbol list if needed

5. **Memory/CPU Limits**
   - Python Workers may use more resources than JS
   - Monitor usage in Cloudflare dashboard
   - Optimize code if approaching limits

### Debug Mode
```bash
# Enable debug logs
wrangler dev --log-level debug

# Tail production logs
wrangler tail
```

## Configuration Options

### Cron Schedule Modification
Edit `wrangler.jsonc`:
```json
{
  "triggers": {
    "crons": [
      "0 */6 * * *"  // Every 6 hours instead of 3
    ]
  }
}
```

### Symbol List Customization
Edit `src/entry.py`, line ~309:
```python
symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'GOOGL']  // Add GOOGL
```

### Email Template Customization
Modify the `send_email_report()` function in `src/entry.py` around line ~520.

## Security Considerations

1. **API Keys**: Always use Wrangler secrets, never hardcode
2. **Rate Limiting**: Yahoo Finance is free but may rate limit
3. **Error Handling**: Comprehensive error handling prevents crashes
4. **Input Validation**: Validate external API responses

## Performance Optimization

1. **Parallel Processing**: Market data fetched in parallel
2. **Timeout Handling**: Prevents hanging requests  
3. **Error Recovery**: Continues analysis even if some data fails
4. **Caching**: Consider adding KV storage for frequent data

## Scaling Considerations

- **Multiple Markets**: Add European/Asian market symbols
- **More Frequent Updates**: Reduce cron interval (be mindful of costs)
- **Advanced Analytics**: Add more AI agents or models
- **Data Storage**: Use D1 database for historical data
- **Notifications**: Add Slack/Discord integrations

## Cost Monitoring

- **Workers Requests**: ~1 request every 3 hours + manual triggers
- **CPU Time**: Python Workers may use more CPU than JS
- **AI API Costs**: Monitor Swarms API usage and billing
- **Email Costs**: Mailgun charges per email sent

Monitor costs in Cloudflare dashboard and Swarms platform.