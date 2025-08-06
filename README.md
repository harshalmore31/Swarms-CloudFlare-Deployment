# Swarms-CloudFlare-Deployment

Deploy intelligent AI agents powered by Swarms API on Cloudflare Workers edge network. Build production-ready cron agents that run automatically, fetch real-time data, perform AI analysis, and execute actions across 330+ cities worldwide.

## Overview

This repository demonstrates how to combine **Swarms API multi-agent intelligence** with **Cloudflare Workers edge computing** to create autonomous AI systems that:

- ⚡ **Execute automatically** on predefined schedules (cron jobs)
- 📊 **Fetch real-time data** from external APIs (Yahoo Finance, news feeds)
- 🤖 **Perform intelligent analysis** using specialized Swarms AI agents
- 📧 **Take automated actions** (email alerts, reports, notifications)
- 🌍 **Scale globally** on Cloudflare's edge network with sub-100ms latency

## Available Implementations

This repository provides **two complete implementations** of stock analysis agents:

### 📂 `stock-agent/` - JavaScript Implementation
The original implementation using **JavaScript/TypeScript** on Cloudflare Workers.

### 📂 `python-stock-agent/` - Python Implementation  
A **Python Workers** implementation using Cloudflare's beta Python runtime with Pyodide.

## Stock Analysis Agent Features

Both implementations demonstrate a complete system that:

1. Runs automated stock analysis every 3 hours using Cloudflare Workers cron
2. Fetches real-time market data from Yahoo Finance API (no API key needed)
3. Collects market news from Financial Modeling Prep API (optional)
4. Deploys multiple Swarms AI agents for technical and fundamental analysis
5. Sends comprehensive email reports via Mailgun
6. Provides a web interface for manual triggers and monitoring

## Implementation Comparison

| Feature | JavaScript (`stock-agent/`) | Python (`python-stock-agent/`) |
|---------|----------------------------|--------------------------------|
| **Runtime** | V8 JavaScript Engine | Pyodide Python Runtime |
| **Language** | JavaScript/TypeScript | Python 3.x |
| **Status** | Production Ready | Beta (Python Workers) |
| **Performance** | Optimized V8 execution | Good, with Python stdlib support |
| **Syntax** | `fetch()`, `JSON.stringify()` | `await fetch()`, `json.dumps()` |
| **Error Handling** | `try/catch` | `try/except` |
| **Libraries** | Built-in Web APIs | Python stdlib + select packages |
| **Development** | Mature tooling | Growing ecosystem |

### Architecture (Both Implementations)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Cloudflare      │    │  Data Sources   │    │   Swarms API    │
│ Workers Runtime │    │                 │    │                 │
│ "0 */3 * * *"   │───▶│ Yahoo Finance   │───▶│ Technical Agent │
│ JS | Python     │    │ News APIs       │    │ Fundamental     │
│ scheduled()     │    │ Market Data     │    │ Agent Analysis  │
│ Global Edge     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start Guide

Choose your preferred implementation:

### Option A: JavaScript Implementation

```bash
# Clone the repository
git clone https://github.com/The-Swarm-Corporation/Swarms-CloudFlare-Deployment.git
cd Swarms-CloudFlare-Deployment/stock-agent

# Install dependencies
npm install
```

### Option B: Python Implementation

```bash
# Clone the repository
git clone https://github.com/The-Swarm-Corporation/Swarms-CloudFlare-Deployment.git
cd Swarms-CloudFlare-Deployment/python-stock-agent

# Install dependencies (Wrangler CLI)
npm install
```

### 2. Environment Configuration

Create a `.dev.vars` file in the `stock-agent/` directory:

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

### 3. Cron Schedule Configuration

The cron schedule is configured in `wrangler.jsonc`:

```jsonc
{
  "triggers": {
    "crons": [
      "0 */3 * * *"  // Every 3 hours
    ]
  }
}
```

Common cron patterns:
- `"0 9 * * 1-5"` - 9 AM weekdays only
- `"0 */6 * * *"` - Every 6 hours  
- `"0 0 * * *"` - Daily at midnight

### 4. Local Development

```bash
# Start local development server
npm run dev

# Visit http://localhost:8787 to test
```

### 5. Deploy to Cloudflare Workers

```bash
# Deploy to production
npm run deploy

# Your agent will be live at: https://stock-agent.your-subdomain.workers.dev
```

## API Integration Details

### Swarms API Agents

The stock agent uses two specialized AI agents:

1. **Technical Analyst Agent**:
   - Calculates technical indicators (RSI, MACD, Moving Averages)
   - Identifies support/resistance levels
   - Provides trading signals and price targets

2. **Fundamental Analyst Agent**:
   - Analyzes market conditions and sentiment
   - Evaluates news and economic indicators
   - Provides investment recommendations

### Data Sources

- **Yahoo Finance API**: Free real-time stock data (no API key required)
- **Financial Modeling Prep**: Market news and additional data (free tier: 250 requests/day)
- **Mailgun**: Email delivery service (free tier: 5,000 emails/month)

## Features

### Web Interface
- Real-time status monitoring
- Manual analysis triggers
- Progress tracking with visual feedback
- Analysis results display

### Automated Execution
- Scheduled cron job execution
- Error handling and recovery
- Cost tracking and monitoring
- Email report generation

### Production Ready
- Comprehensive error handling
- Timeout protection
- Rate limiting compliance
- Security best practices

## Configuration Examples

### Custom Stock Symbols

Edit the symbols array in `src/index.js`:

```javascript
const symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'GOOGL'];
```

### Custom Swarms Agents

Modify the agent configuration:

```javascript
const swarmConfig = {
  agents: [
    {
      agent_name: "Risk Assessment Agent",
      system_prompt: "Analyze portfolio risk and provide recommendations...",
      model_name: "gpt-4o-mini",
      max_tokens: 2000,  
      temperature: 0.1
    }
  ]
};
```

## Cost Optimization

- **Cloudflare Workers**: Free tier includes 100,000 requests/day
- **Swarms API**: Monitor usage in dashboard, use gpt-4o-mini for cost efficiency
- **External APIs**: Leverage free tiers and implement intelligent caching

## Security Best Practices

- Store API keys as Cloudflare Workers secrets
- Implement request validation and rate limiting
- Audit AI decisions and maintain compliance logs
- Use HTTPS for all external API calls

## Monitoring & Observability

- Cloudflare Workers analytics dashboard
- Real-time performance metrics
- Error tracking and alerting
- Cost monitoring and optimization

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify environment variables are set correctly
2. **Cron Not Triggering**: Check cron syntax and Cloudflare Workers limits
3. **Email Not Sending**: Verify Mailgun configuration and domain setup
4. **Data Fetch Failures**: Check external API status and rate limits

### Debug Mode

Enable detailed logging by setting:
```javascript
console.log('Debug mode enabled');
```

## Additional Resources

- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Swarms API Documentation](https://docs.swarms.world/)
- [Cron Expression Generator](https://crontab.guru/)
- [Financial Modeling Prep API](https://financialmodelingprep.com/developer/docs)

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/The-Swarm-Corporation/AdvancedResearch/issues)
- **Discussions**: [GitHub Discussions](https://github.com/The-Swarm-Corporation/AdvancedResearch/discussions)
- **Discord**: [Join our community](https://discord.gg/EamjgSaEQf)

<p align="center">
  <strong>Built with <a href="https://github.com/kyegomez/swarms">Swarms</a> framework for production-grade agentic applications </strong>
</p>
