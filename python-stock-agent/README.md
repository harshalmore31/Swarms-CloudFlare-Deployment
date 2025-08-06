# Python Stock Agent 🐍📈

A Python-based stock analysis agent built with Cloudflare Workers that provides real-time market analysis using AI agents from the Swarms platform.

## Features

- **Python Workers Implementation**: Built using Cloudflare's Python Workers runtime
- **Real-time Market Data**: Fetches live stock data from Yahoo Finance API (no API key required)
- **AI-Powered Analysis**: Uses Swarms AI agents for technical and fundamental analysis
- **Scheduled Execution**: Runs automatically every 3 hours via Cron Triggers
- **Email Reports**: Optional email notifications with analysis results
- **Web Dashboard**: Interactive HTML interface for manual triggers and status monitoring
- **Error Handling**: Comprehensive error handling and logging

## Architecture

- **Entry Point**: `src/entry.py` - Main Python Worker file
- **Handlers**: 
  - `on_fetch()` - HTTP request handler
  - `on_scheduled()` - Cron trigger handler
- **Core Functions**:
  - `handle_stock_analysis()` - Main analysis orchestrator
  - `fetch_market_data()` - Yahoo Finance API integration
  - `fetch_market_news()` - Financial Modeling Prep API integration
  - `send_email_report()` - Mailgun email integration

## Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Configure Environment Variables**:
   ```bash
   # Required
   wrangler secret put SWARMS_API_KEY

   # Optional (for news)
   wrangler secret put FMP_API_KEY

   # Optional (for email reports)
   wrangler secret put MAILGUN_API_KEY
   wrangler secret put MAILGUN_DOMAIN
   wrangler secret put RECIPIENT_EMAIL
   ```

3. **Development**:
   ```bash
   npm run dev
   ```

4. **Test Scheduled Events**:
   ```bash
   npm run test
   # Then visit: http://localhost:8787/__scheduled?cron=0+*+*+*+*
   ```

5. **Deploy**:
   ```bash
   npm run deploy
   ```

## API Endpoints

- **`GET /`** - Web dashboard interface
- **`GET /trigger`** - Manual analysis trigger
- **`GET /status`** - Service status check
- **Scheduled** - Automatic execution every 3 hours

## Environment Variables

### Required
- `SWARMS_API_KEY` - API key for Swarms AI platform

### Optional
- `FMP_API_KEY` - Financial Modeling Prep API key (for market news)
- `MAILGUN_API_KEY` - Mailgun API key (for email reports)
- `MAILGUN_DOMAIN` - Mailgun domain (for email reports)
- `RECIPIENT_EMAIL` - Email address for reports

## Analyzed Stocks

- **SPY** - SPDR S&P 500 ETF Trust
- **QQQ** - Invesco QQQ Trust
- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **TSLA** - Tesla Inc.
- **NVDA** - NVIDIA Corporation

## AI Analysis

The system uses two specialized AI agents:

1. **Technical Analyst**:
   - RSI, MACD, Moving Averages analysis
   - Support/resistance levels identification
   - Trading signals and price targets

2. **Fundamental Analyst**:
   - Market conditions evaluation
   - Economic indicators assessment
   - Risk analysis and investment recommendations

## Python Workers Features Used

- **Foreign Function Interface (FFI)**: Access to JavaScript APIs
- **Bindings**: Environment variables and secrets
- **Scheduled Events**: Cron trigger support
- **HTTP Handlers**: Request/Response processing
- **Logging**: Native Python logging support

## Comparison with JavaScript Version

| Feature | JavaScript | Python |
|---------|------------|--------|
| Runtime | V8 JavaScript | Pyodide Python |
| API Access | Native fetch() | workers.fetch() |
| Error Handling | try/catch | try/except |
| Logging | console.log | logging module |
| JSON Processing | Native | json module |
| Async/Await | Native | asyncio |

## Development Notes

- Python Workers are currently in beta
- Requires `python_workers` compatibility flag
- Uses Pyodide runtime for Python execution
- Full access to Cloudflare Workers APIs via FFI

## Monitoring

Check the Cloudflare Workers dashboard for:
- Execution logs
- Performance metrics
- Error tracking
- Cron trigger history

## License

MIT License - see original stock-agent for reference implementation.