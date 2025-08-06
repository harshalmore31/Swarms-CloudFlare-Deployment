# Stock Analysis Agent 📈

A JavaScript-based stock analysis agent built with Cloudflare Workers that provides real-time market analysis using AI agents from the Swarms platform.

## Features

- **Cloudflare Workers**: Serverless execution on Cloudflare's global edge network
- **Real-time Market Data**: Fetches live stock data from Yahoo Finance API (no API key required)
- **AI-Powered Analysis**: Uses Swarms AI agents for technical and fundamental analysis
- **Scheduled Execution**: Runs automatically every 3 hours via Cron Triggers
- **Email Reports**: Optional email notifications with analysis results using Mailgun
- **Web Dashboard**: Interactive HTML interface for manual triggers and status monitoring
- **Global Edge Deployment**: Runs in 330+ cities worldwide with sub-100ms latency

## Architecture

Built using Cloudflare Workers with:

- **Entry Point**: `src/index.js` - Main Worker script
- **Handlers**: 
  - `fetch()` - HTTP request handler for web interface
  - `scheduled()` - Cron trigger handler for automated analysis
- **Core Functions**:
  - `handleStockAnalysis()` - Main analysis orchestrator
  - `fetchMarketData()` - Yahoo Finance API integration
  - `fetchMarketNews()` - Financial Modeling Prep API integration
  - `sendEmailReport()` - Mailgun email integration

## Quick Start

### 1. Setup

```bash
# Clone and navigate to stock-agent
git clone <repository-url>
cd stock-agent

# Install dependencies
npm install
```

### 2. Environment Configuration

Create a `.dev.vars` file:

```env
# Required: Swarms API key
SWARMS_API_KEY=your-swarms-api-key-here

# Optional: Market news (free tier available)
FMP_API_KEY=your-fmp-api-key

# Optional: Email notifications
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-domain.com
RECIPIENT_EMAIL=your-email@example.com
```

### 3. Development

```bash
# Start local development server
npm run dev

# Visit http://localhost:8787 to test the interface
```

### 4. Test Scheduled Events

```bash
# Test cron triggers locally
npm run test

# Or manually trigger via curl
curl "http://localhost:8787/__scheduled?cron=0+*+*+*+*"
```

### 5. Deploy

```bash
# Deploy to Cloudflare Workers
npm run deploy

# Your agent will be live at: https://stock-agent.your-subdomain.workers.dev
```

## Configuration

### Cron Schedule

Edit `wrangler.jsonc` to customize the schedule:

```jsonc
{
  "triggers": {
    "crons": [
      "0 */3 * * *"  // Every 3 hours (default)
      // "0 9 * * 1-5"  // 9 AM weekdays only
      // "0 */6 * * *"   // Every 6 hours
    ]
  }
}
```

### Analyzed Stocks

Modify the symbols array in `src/index.js`:

```javascript
const symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA'];
// Add more symbols as needed
```

## API Endpoints

- **`GET /`** - Interactive web dashboard
- **`GET /trigger`** - Manual analysis trigger (returns JSON)
- **`GET /status`** - Service status check (returns JSON)
- **Scheduled** - Automatic execution every 3 hours

## Swarms AI Integration

The agent uses two specialized AI agents:

### 1. Technical Analyst
- Calculates RSI, MACD, Moving Averages
- Identifies support and resistance levels  
- Provides trading signals and price targets
- Model: `gpt-4o-mini` (cost-optimized)

### 2. Fundamental Analyst  
- Analyzes market conditions and sentiment
- Evaluates news and economic indicators
- Provides investment recommendations
- Model: `gpt-4o-mini` (cost-optimized)

### Agent Configuration

```javascript
const swarmConfig = {
  name: "Real-Time Stock Analysis",
  agents: [
    {
      agent_name: "Technical Analyst",
      system_prompt: "Professional technical analysis...",
      model_name: "gpt-4o-mini",
      max_tokens: 1500,
      temperature: 0.2
    }
    // Additional agents...
  ],
  swarm_type: "ConcurrentWorkflow",
  max_loops: 1
};
```

## External API Integrations

### Yahoo Finance API (Free)
- **Purpose**: Real-time stock data
- **Endpoint**: `https://query1.finance.yahoo.com/v8/finance/chart/{symbol}`
- **Rate Limits**: None documented, use responsibly
- **Data**: OHLCV, market state, 52-week highs/lows

### Financial Modeling Prep API (Optional)
- **Purpose**: Market news and additional data  
- **Free Tier**: 250 requests/day
- **Pricing**: $14/month for 1,000 requests/day
- **Setup**: Sign up at [financialmodelingprep.com](https://financialmodelingprep.com/developer/docs)

### Mailgun API (Optional)
- **Purpose**: Email report delivery
- **Free Tier**: 5,000 emails/month
- **Setup**: Configure domain and API key at [mailgun.com](https://www.mailgun.com/)

## Cloudflare Workers Features

### Platform Benefits
- **Global Edge Network**: Runs in 330+ cities worldwide
- **Sub-100ms Latency**: Requests served from nearest location
- **Automatic Scaling**: Handles traffic spikes automatically
- **Built-in Security**: DDoS protection and WAF included

### Runtime Features
- **Cron Triggers**: Reliable scheduled execution
- **Secrets Management**: Secure API key storage
- **Environment Variables**: Multi-environment support
- **Real-time Logs**: Debug and monitor execution
- **Analytics**: Request metrics and performance data

### Pricing
- **Free Tier**: 100,000 requests/day
- **Paid Plan**: $5/month for 10M requests + usage-based pricing
- **CPU Time**: 10ms free per request, $0.02 per additional GB-second

## Error Handling & Resilience

The agent includes comprehensive error handling:

- **API Timeouts**: 8-second timeout for stock data, 10-second for news
- **Graceful Degradation**: Continues analysis even if news API fails
- **Rate Limit Compliance**: Respects external API limits
- **Retry Logic**: Handles transient failures automatically
- **Logging**: Detailed console logs for debugging

## Performance Optimization

- **Parallel Processing**: Fetches multiple stock symbols concurrently
- **Timeout Management**: Prevents hanging requests
- **Error Recovery**: Continues with partial data if some APIs fail
- **Efficient Caching**: Browser caching for static assets

## Monitoring & Observability

### Cloudflare Dashboard
- Navigate to **Workers & Pages** → Select your worker
- Monitor: Requests, Errors, CPU usage, Response times
- View: Real-time logs, Cron trigger history

### Debug Mode
```bash
# Tail live logs during development
wrangler tail

# View logs with debug level
wrangler dev --log-level debug
```

## Security Best Practices

- **API Keys**: Stored as Cloudflare Workers secrets
- **HTTPS Only**: All external API calls use HTTPS
- **Input Validation**: Validates all external API responses
- **Error Sanitization**: Prevents sensitive data leakage in errors
- **Rate Limiting**: Respects external API rate limits

## Troubleshooting

### Common Issues

1. **"SWARMS_API_KEY is required"**
   ```bash
   wrangler secret put SWARMS_API_KEY
   # Enter your API key when prompted
   ```

2. **Cron triggers not working**
   - Check cron syntax at [crontab.guru](https://crontab.guru/)
   - Verify deployment with `wrangler deploy`
   - Check Cloudflare dashboard for trigger history

3. **Email reports not sending**
   - Verify Mailgun domain is configured
   - Check all email environment variables are set
   - Review Mailgun dashboard for delivery status

4. **Market data fetch failures**
   - Yahoo Finance API is free but may rate limit
   - Check Worker logs for specific error messages
   - Consider reducing number of symbols if timeout issues occur

### Getting Help

- Check [Cloudflare Workers documentation](https://developers.cloudflare.com/workers/)
- Review [Swarms API documentation](https://docs.swarms.world/)
- Open issues in the project repository

## Development Workflow

1. **Local Development**: Use `npm run dev` with `.dev.vars` file
2. **Testing**: Test scheduled events with `npm run test`
3. **Staging**: Deploy to staging environment with `wrangler deploy --env staging`
4. **Production**: Deploy with `wrangler deploy`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes  
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - See LICENSE file for details