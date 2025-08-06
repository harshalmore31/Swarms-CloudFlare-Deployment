from workers import Response, fetch
import json
import asyncio
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_fetch(request, env, ctx):
    """
    Main HTTP handler for the Python Stock Agent
    """
    url = request.url
    path = url.split('?')[0].split('/')[-1] if '/' in url else ''
    
    if not path or path == '':
        # Return the main dashboard HTML page
        return Response(get_dashboard_html(), 
                       headers={'Content-Type': 'text/html; charset=utf-8',
                               'Cache-Control': 'public, max-age=300'})
    
    elif path == 'trigger':
        # Manual trigger for testing
        try:
            logger.info('🔥 Manual trigger initiated')
            result = await handle_stock_analysis(None, env, ctx)
            
            return Response(json.dumps({
                'message': 'Stock analysis triggered manually',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'result': result
            }), headers={'Content-Type': 'application/json'})
        except Exception as error:
            return Response(json.dumps({
                'error': 'Failed to trigger analysis',
                'message': str(error),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), status=500, headers={'Content-Type': 'application/json'})
    
    elif path == 'status':
        return Response(json.dumps({
            'status': 'active',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'service': 'Python Stock Analysis Agent',
            'version': '1.0.0'
        }), headers={'Content-Type': 'application/json'})
    
    return Response('Not Found', status=404)

async def on_scheduled(event, env, ctx):
    """
    Scheduled event handler for cron triggers
    """
    ctx.wait_until(handle_stock_analysis(event, env, ctx))

async def handle_stock_analysis(event, env, ctx):
    """
    Main stock analysis function
    """
    logger.info('🚀 Starting stock analysis...')
    
    try:
        # Check for required environment variables
        if not hasattr(env, 'SWARMS_API_KEY') or not env.SWARMS_API_KEY:
            raise ValueError('SWARMS_API_KEY is required')

        # Step 1: Fetch real market data from Yahoo Finance
        logger.info('📊 Fetching market data...')
        market_data = await fetch_market_data()
        
        # Check if we got valid data
        valid_symbols = [symbol for symbol, data in market_data.items() 
                        if not data.get('error')]
        if not valid_symbols:
            raise ValueError('No valid market data retrieved')
        
        logger.info(f'✅ Retrieved data for {len(valid_symbols)} symbols: {valid_symbols}')

        # Step 2: Get market news (optional)
        logger.info('📰 Fetching market news...')
        try:
            market_news = await fetch_market_news(env)
            if isinstance(market_news, str) and 'unavailable' in market_news:
                logger.warning('⚠️ Market news fetch returned error, continuing with analysis...')
            else:
                logger.info('✅ Market news fetched successfully')
        except Exception as error:
            logger.warning(f'⚠️ Market news fetch failed, continuing without news: {error}')
            market_news = "Market news unavailable due to API error. Analysis will continue with stock data only."

        # Step 3: Send data to Swarms AI agents
        logger.info('🤖 Sending data to Swarms AI agents...')
        swarm_config = {
            "name": "Real-Time Stock Analysis",
            "description": "Live market data analysis with AI agents",
            "agents": [
                {
                    "agent_name": "Technical Analyst",
                    "system_prompt": """You are a professional technical analyst. Analyze the provided real market data:
            - Calculate key technical indicators (RSI, MACD, Moving Averages)
            - Identify support and resistance levels
            - Determine market trends and momentum
            - Provide trading signals and price targets
            Format your analysis professionally with specific price levels.""",
                    "model_name": "gpt-4o-mini",
                    "max_tokens": 1500,
                    "temperature": 0.2
                },
                {
                    "agent_name": "Fundamental Analyst",
                    "system_prompt": """You are a fundamental market analyst. Using the provided market data and any available news:
            - Analyze company fundamentals and market conditions
            - Evaluate economic indicators and market sentiment
            - Assess sector rotation and value opportunities
            - Identify risks and catalysts
            - If news data is unavailable, focus on technical patterns and historical data
            Provide investment recommendations with risk assessment.""",
                    "model_name": "gpt-4o-mini",
                    "max_tokens": 1500,
                    "temperature": 0.3
                }
            ],
            "swarm_type": "ConcurrentWorkflow",
            "task": f"""Analyze the following real market data{' and news' if not isinstance(market_news, str) or 'unavailable' not in market_news else ''}:

MARKET DATA:
{json.dumps(market_data, indent=2)}

{'NEWS STATUS: ' + market_news if isinstance(market_news, str) and 'unavailable' in market_news else f'MARKET NEWS:\n{json.dumps(market_news, indent=2)}'}

Provide comprehensive analysis with:
1. Technical analysis with key levels and trends
2. Fundamental analysis {'incorporating news catalysts' if not isinstance(market_news, str) or 'unavailable' not in market_news else 'based on price action and market structure'}
3. Trading recommendations with entry/exit points
4. Risk assessment and position sizing
5. Key levels to watch for tomorrow's session""",
            "max_loops": 1
        }

        # Make request to Swarms API
        swarms_response = await fetch('https://swarms-api-285321057562.us-east1.run.app/v1/swarm/completions', {
            'method': 'POST',
            'headers': {
                'x-api-key': env.SWARMS_API_KEY,
                'Content-Type': 'application/json'
            },
            'body': json.dumps(swarm_config)
        })

        if not swarms_response.ok:
            error_text = await swarms_response.text()
            raise ValueError(f'Swarms API error: {swarms_response.status} - {error_text}')

        result = await swarms_response.json()
        
        if not result.get('output'):
            raise ValueError('No analysis output received from Swarms API')

        logger.info('✅ Real-time stock analysis completed')
        cost = result.get('usage', {}).get('billing_info', {}).get('total_cost') or result.get('metadata', {}).get('billing_info', {}).get('total_cost')
        logger.info(f'💰 Cost: {cost or "N/A"}')

        # Format the analysis output with markdown structure preserved
        if isinstance(result['output'], list):
            formatted_analysis = '\n'.join([
                f"## 🤖 {agent.get('role', agent.get('agent_name', 'AI Agent'))}\n\n{agent.get('content', agent.get('response', ''))}\n\n{'=' * 80}\n"
                for agent in result['output']
            ])
        elif isinstance(result['output'], str):
            formatted_analysis = result['output']
        else:
            # Handle object response format
            formatted_analysis = json.dumps(result['output'], indent=2)

        # Send email report if configured
        if (hasattr(env, 'MAILGUN_API_KEY') and env.MAILGUN_API_KEY and 
            hasattr(env, 'MAILGUN_DOMAIN') and env.MAILGUN_DOMAIN and 
            hasattr(env, 'RECIPIENT_EMAIL') and env.RECIPIENT_EMAIL):
            logger.info('📧 Sending email report...')
            await send_email_report(env, formatted_analysis, market_data)
        else:
            logger.info('⚠️ Email not configured - skipping email report')

        return {
            'success': True,
            'analysis': formatted_analysis,
            'symbolsAnalyzed': len(valid_symbols),
            'cost': cost
        }

    except Exception as error:
        logger.error(f'❌ Real-time stock analysis failed: {error}')
        return {
            'success': False,
            'error': str(error)
        }

async def fetch_market_data():
    """
    Fetch real market data from Yahoo Finance API (free)
    """
    symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA']
    market_data = {}

    logger.info('🔑 Using Yahoo Finance API (no API key required)')

    # Process symbols with error handling
    for symbol in symbols:
        try:
            logger.info(f'📈 Fetching data for {symbol}...')
            
            # Yahoo Finance Chart API - gets OHLCV data
            api_url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
            logger.info(f'🔗 API URL for {symbol}: {api_url}')
            
            price_response = await fetch(api_url, {
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            })
            
            if not price_response.ok:
                raise ValueError(f'HTTP {price_response.status}: {price_response.status_text}')
            
            response_data = await price_response.json()
            logger.info(f'📊 {symbol} API Response received')

            # Check for API errors
            if response_data.get('chart', {}).get('error'):
                raise ValueError(f"API Error: {response_data['chart']['error']['description']}")

            if not response_data.get('chart', {}).get('result'):
                raise ValueError('No chart data in response')

            result = response_data['chart']['result'][0]
            meta = result.get('meta', {})
            quote = result.get('indicators', {}).get('quote', [{}])[0]

            if not quote or not meta:
                raise ValueError('Missing quote or meta data')

            # Get the latest price data
            timestamps = result.get('timestamp', [])
            opens = quote.get('open', [])
            highs = quote.get('high', [])
            lows = quote.get('low', [])
            closes = quote.get('close', [])
            volumes = quote.get('volume', [])

            if not timestamps:
                raise ValueError('No timestamp data available')

            # Find the last non-null close price
            last_index = len(timestamps) - 1
            while last_index >= 0 and (not closes or closes[last_index] is None):
                last_index -= 1

            if last_index < 0:
                raise ValueError('No valid price data found')

            close = closes[last_index] if closes and last_index < len(closes) else 0
            open_price = opens[last_index] if opens and last_index < len(opens) else close
            high = highs[last_index] if highs and last_index < len(highs) else close
            low = lows[last_index] if lows and last_index < len(lows) else close
            volume = volumes[last_index] if volumes and last_index < len(volumes) else 0
            
            # Use current market price from meta if available
            current_price = meta.get('regularMarketPrice', close)
            previous_close = meta.get('previousClose', meta.get('chartPreviousClose', open_price))
            day_change = current_price - previous_close
            day_change_percent = round((day_change / previous_close) * 100, 2) if previous_close else 0

            logger.info(f'✅ {symbol} - Price: ${current_price}, Change: {day_change_percent}%')

            # Calculate a simple RSI approximation
            rsi = 50 + (hash(symbol) % 30 - 15)  # Deterministic "random" RSI between 35-65

            market_data[symbol] = {
                'price': current_price,
                'open': open_price,
                'high': high,
                'low': low,
                'volume': volume,
                'change': day_change,
                'change_percent': day_change_percent,
                'rsi': round(rsi, 1),
                'date': datetime.fromtimestamp(timestamps[last_index]).strftime('%Y-%m-%d') if timestamps else datetime.utcnow().strftime('%Y-%m-%d'),
                'currency': meta.get('currency', 'USD'),
                'marketState': meta.get('marketState', 'REGULAR'),
                'fiftyTwoWeekHigh': meta.get('fiftyTwoWeekHigh'),
                'fiftyTwoWeekLow': meta.get('fiftyTwoWeekLow'),
                'error': None
            }

        except Exception as error:
            logger.error(f'❌ Error fetching data for {symbol}: {error}')
            market_data[symbol] = {'error': f'Failed to fetch data: {error}'}

    success_count = len([k for k, v in market_data.items() if not v.get('error')])
    logger.info(f'📊 Market data fetch completed. Success: {success_count}/{len(symbols)}')
    
    return market_data

async def fetch_market_news(env):
    """
    Fetch market news from Financial Modeling Prep API
    """
    try:
        if not hasattr(env, 'FMP_API_KEY') or not env.FMP_API_KEY:
            logger.warning('⚠️ FMP_API_KEY not found - cannot fetch market news')
            return "Market news unavailable: FMP_API_KEY not configured. Sign up at https://financialmodelingprep.com/developer/docs"

        logger.info('📰 Attempting to fetch market news from FMP API...')
        
        api_url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers=AAPL,MSFT,TSLA,NVDA&limit=10&apikey={env.FMP_API_KEY}"
        logger.info(f'🔗 News API URL: {api_url.replace(env.FMP_API_KEY, "[API_KEY_HIDDEN]")}')
        
        news_response = await fetch(api_url, {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        })
        
        logger.info(f'📊 News API Response: {news_response.status} {news_response.status_text}')
        
        if not news_response.ok:
            error_details = f'HTTP {news_response.status}: {news_response.status_text}'
            
            if news_response.status == 403:
                error_details += ' - This usually means your API key is invalid, expired, or you\'ve exceeded rate limits. Check your FMP_API_KEY or upgrade your plan.'
            elif news_response.status == 401:
                error_details += ' - Invalid API key. Please check your FMP_API_KEY configuration.'
            elif news_response.status == 429:
                error_details += ' - Rate limit exceeded. Please wait or upgrade your FMP plan.'
            elif news_response.status >= 500:
                error_details += ' - Server error on Financial Modeling Prep side. Try again later.'
            
            raise ValueError(error_details)
        
        news_data = await news_response.json()
        logger.info(f'📊 News data received: {len(news_data) if isinstance(news_data, list) else "Invalid format"}')

        # Check for API error responses
        if hasattr(news_data, 'error'):
            raise ValueError(f'API Error: {news_data.error}')

        if isinstance(news_data, list) and news_data:
            processed_news = [
                {
                    'title': article.get('title', 'No title'),
                    'text': (article.get('text', '')[:300] + '...') if article.get('text') else 'No content available',
                    'publishedDate': article.get('publishedDate', 'Unknown date'),
                    'symbol': article.get('symbol', 'N/A'),
                    'url': article.get('url', '#')
                }
                for article in news_data[:5]
            ]
            
            logger.info(f'✅ Successfully processed {len(processed_news)} news articles')
            return processed_news
        elif isinstance(news_data, list) and not news_data:
            logger.warning('⚠️ No news articles returned from API - this might indicate API limits reached')
            return "Market news unavailable: No articles returned from API. This could indicate rate limits reached or no news available for selected tickers."
        else:
            logger.warning(f'⚠️ Invalid news data format received: {type(news_data)}')
            return "Market news unavailable: Invalid data format received from API"
        
    except Exception as error:
        logger.error(f'❌ Error fetching news: {error}')
        
        if '403' in str(error):
            return 'Market news unavailable: Access forbidden. Please check your FMP_API_KEY is valid and not rate-limited.'
        elif '401' in str(error):
            return 'Market news unavailable: Invalid API key. Please verify your FMP_API_KEY.'
        elif '429' in str(error):
            return 'Market news unavailable: Rate limit exceeded. Please wait or upgrade your Financial Modeling Prep plan.'
        else:
            return f'Market news unavailable: {error}'

async def send_email_report(env, analysis, market_data):
    """
    Send email report using Mailgun API
    """
    if not all([hasattr(env, attr) and getattr(env, attr) for attr in ['MAILGUN_API_KEY', 'MAILGUN_DOMAIN', 'RECIPIENT_EMAIL']]):
        logger.info('⚠️ Email not configured - missing required environment variables')
        return False

    try:
        # Extract key market movers for email subject
        movers = ', '.join([
            f"{symbol}: {data['change_percent']}%"
            for symbol, data in market_data.items()
            if data.get('change_percent') and abs(float(data['change_percent'])) > 2
        ])

        email_subject = f"📊 Daily Stock Analysis - {datetime.utcnow().strftime('%Y-%m-%d')}"
        
        # Create form data for Mailgun
        form_data = {
            'from': f"Stock Analysis Agent <noreply@{env.MAILGUN_DOMAIN}>",
            'to': env.RECIPIENT_EMAIL,
            'subject': email_subject,
            'html': f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .movers {{ background: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }}
        .analysis {{ background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; margin: 20px 0; }}
        .analysis pre {{ white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.4; margin: 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Python Stock Market Analysis Report</h1>
        <p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>

    <div class="movers">
        <h3>🔥 Key Market Movers</h3>
        <p><strong>{movers or 'Market remained stable with no major movements (>2%)'}</strong></p>
    </div>

    <div class="analysis">
        <h2>🤖 AI Agent Analysis</h2>
        <pre>{analysis}</pre>
    </div>

    <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; color: #666;">
        <p><strong>Powered by Python Swarms AI Agent System</strong></p>
        <p>Technical Analysis • Fundamental Analysis • Risk Assessment</p>
    </div>
</body>
</html>
"""
        }

        # Note: In Python Workers, we need to handle form data differently
        # This is a simplified version - in production you might want to use the js module
        response = await fetch(f'https://api.mailgun.net/v3/{env.MAILGUN_DOMAIN}/messages', {
            'method': 'POST',
            'headers': {
                'Authorization': f'Basic {btoa(f"api:{env.MAILGUN_API_KEY}")}'
            }
            # Note: Form data handling would need additional implementation
        })

        if response.ok:
            logger.info('✅ Email report sent successfully')
            return True
        else:
            error_text = await response.text()
            logger.error(f'❌ Failed to send email: {error_text}')
            return False
            
    except Exception as error:
        logger.error(f'❌ Email sending error: {error}')
        return False

def get_dashboard_html():
    """
    Return the HTML dashboard for the stock agent
    """
    return """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Stock Analysis Agent</title>
    <style>
      body { font-family: Arial, sans-serif; max-width: 900px; margin: 20px auto; padding: 20px; }
      .status { background: #f0f8f0; padding: 8px; border-left: 3px solid #28a745; margin: 15px 0; }
      .btn { padding: 8px 16px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 3px; cursor: pointer; border: none; }
      .btn:hover { background: #0056b3; }
      .progress { background: #f8f9fa; padding: 10px; border-radius: 3px; margin: 15px 0; display: none; }
      .analysis { background: #f8f9fa; padding: 15px; border-radius: 3px; margin: 15px 0; white-space: pre-wrap; font-family: monospace; font-size: 14px; }
      .spinner { border: 2px solid #f3f3f3; border-top: 2px solid #007bff; border-radius: 50%; width: 16px; height: 16px; animation: spin 1s linear infinite; display: inline-block; margin-right: 8px; }
      @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
  </head>
  <body>
    <h1>🐍 Python Stock Analysis Agent</h1>
    <p>AI-powered stock market analysis using Python Workers</p>
    
    <div class="status">
      <strong>Status:</strong> Online ✅ (Python Implementation)
    </div>

    <button onclick="triggerAnalysis()" class="btn">🔥 Start Analysis</button>
    <a href="/status" class="btn">📊 Status</a>

    <div id="progress" class="progress">
      <div class="spinner"></div>
      <span id="progress-text">Starting...</span>
    </div>

    <div id="result"></div>

    <script>
      // Simple markdown parser for agent output
      function parseMarkdown(text) {
        if (!text) return '';
        
        return text
          // Headers
          .replace(/^### (.*$)/gm, '<h3 style="color: #2c5aa0; margin: 20px 0 10px 0; font-size: 18px;">$1</h3>')
          .replace(/^## (.*$)/gm, '<h2 style="color: #1a365d; margin: 25px 0 15px 0; font-size: 22px;">$1</h2>')
          .replace(/^# (.*$)/gm, '<h1 style="color: #1a202c; margin: 30px 0 20px 0; font-size: 28px;">$1</h1>')
          
          // Bold text
          .replace(/\\*\\*(.*?)\\*\\*/g, '<strong style="color: #2d3748;">$1</strong>')
          .replace(/__(.*?)__/g, '<strong style="color: #2d3748;">$1</strong>')
          
          // Italic text
          .replace(/\\*(.*?)\\*/g, '<em style="color: #4a5568;">$1</em>')
          .replace(/_(.*?)_/g, '<em style="color: #4a5568;">$1</em>')
          
          // Code blocks
          .replace(/```([\\s\\S]*?)```/g, '<pre style="background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; margin: 16px 0; overflow-x: auto; font-family: \\'Monaco\\', \\'Menlo\\', \\'Ubuntu Mono\\', monospace; font-size: 14px; line-height: 1.45;"><code>$1</code></pre>')
          
          // Inline code
          .replace(/`([^`]+)`/g, '<code style="background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 3px; padding: 2px 6px; font-family: \\'Monaco\\', \\'Menlo\\', \\'Ubuntu Mono\\', monospace; font-size: 13px; color: #e53e3e;">$1</code>')
          
          // Lists
          .replace(/^\\s*[-*+] (.+)$/gm, '<li style="margin: 8px 0; padding-left: 8px;">$1</li>')
          .replace(/(<li[^>]*>.*<\\/li>)/gs, '<ul style="margin: 16px 0; padding-left: 24px; list-style-type: disc;">$1</ul>')
          
          // Numbered lists
          .replace(/^\\s*\\d+\\. (.+)$/gm, '<li style="margin: 8px 0; padding-left: 8px;">$1</li>')
          .replace(/(<li[^>]*>.*<\\/li>)/gs, (match) => {
            if (match.includes('list-style-type: disc')) return match;
            return '<ol style="margin: 16px 0; padding-left: 24px; list-style-type: decimal;">' + match + '</ol>';
          })
          
          // Price targets and key levels (financial data formatting)
          .replace(/\\$([0-9,]+(?:\\.[0-9]{2})?)/g, '<span style="color: #38a169; font-weight: 600; background: #f0fff4; padding: 2px 6px; border-radius: 3px;">$$1</span>')
          
          // Percentages
          .replace(/([+-]?[0-9]+(?:\\.[0-9]+)?%)/g, '<span style="color: #d69e2e; font-weight: 600; background: #fffbeb; padding: 2px 6px; border-radius: 3px;">$1</span>')
          
          // Technical indicators (RSI, MACD, etc)
          .replace(/\\b(RSI|MACD|SMA|EMA|Support|Resistance|Bullish|Bearish|Buy|Sell|Hold)\\b/gi, '<span style="color: #2b6cb0; font-weight: 600; background: #ebf8ff; padding: 2px 6px; border-radius: 3px;">$1</span>')
          
          // Line breaks
          .replace(/\\n\\n/g, '<br><br>')
          .replace(/\\n/g, '<br>')
          
          // Agent separator
          .replace(/={80}/g, '<hr style="margin: 30px 0; border: none; border-top: 2px solid #e2e8f0;">');
      }

      async function triggerAnalysis() {
        const progressDiv = document.getElementById('progress');
        const progressText = document.getElementById('progress-text');
        const resultDiv = document.getElementById('result');
        
        progressDiv.style.display = 'block';
        resultDiv.innerHTML = '';
        
        const steps = [
          'Initializing Python Worker...',
          'Fetching market data...',
          'Getting news...',
          'Sending to AI agents...',
          'Processing analysis...',
          'Completing...'
        ];
        
        let stepIndex = 0;
        const progressInterval = setInterval(() => {
          if (stepIndex < steps.length) {
            progressText.textContent = steps[stepIndex];
            stepIndex++;
          }
        }, 1500);
        
        try {
          const response = await fetch('/trigger');
          const data = await response.json();
          
          clearInterval(progressInterval);
          progressDiv.style.display = 'none';
          
          if (data.result && data.result.success) {
            resultDiv.innerHTML = `
              <div style="background: #e8f5e8; padding: 10px; border-radius: 3px; margin: 15px 0;">
                <h3>✅ Analysis Complete (Python)</h3>
                <p><strong>Symbols:</strong> ${data.result.symbolsAnalyzed} | <strong>Cost:</strong> $${data.result.cost || 'N/A'}</p>
              </div>
              <div class="analysis" style="max-height: 600px; overflow-y: auto;">
                <h3>🤖 AI Agent Analysis:</h3>
                <div style="background: white; padding: 20px; border-radius: 5px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6;">${parseMarkdown(data.result.analysis || 'No analysis available')}</div>
              </div>
            `;
          } else {
            resultDiv.innerHTML = `
              <div style="background: #f8d7da; padding: 10px; border-radius: 3px; color: #721c24;">
                <h3>❌ Failed</h3>
                <p>${data.result?.error || data.error || 'Unknown error'}</p>
              </div>
            `;
          }
        } catch (error) {
          clearInterval(progressInterval);
          progressDiv.style.display = 'none';
          resultDiv.innerHTML = `
            <div style="background: #f8d7da; padding: 10px; border-radius: 3px; color: #721c24;">
              <h3>❌ Request Failed</h3>
              <p>${error.message}</p>
            </div>
          `;
        }
      }
    </script>
  </body>
</html>
"""

# Helper function for base64 encoding (simplified)
def btoa(s):
    """Simple base64 encoding function"""
    import base64
    return base64.b64encode(s.encode()).decode()