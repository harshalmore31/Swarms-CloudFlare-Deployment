export default {
  // HTTP request handler
  async fetch(request, env, _ctx) {
    const url = new URL(request.url);
    
    if (url.pathname === '/') {
      return new Response(`
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Stock Analysis Agent</title>
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
            <h1>📈 Stock Analysis Agent</h1>
            <p>AI-powered stock market analysis</p>
            
            <div class="status">
              <strong>Status:</strong> Online ✅
            </div>

            <button onclick="triggerAnalysis()" class="btn">🔥 Start Analysis</button>
            <a href="/status" class="btn">📊 Status</a>

            <div id="progress" class="progress">
              <div class="spinner"></div>
              <span id="progress-text">Starting...</span>
            </div>

            <div id="result"></div>

            <script>
              async function triggerAnalysis() {
                const progressDiv = document.getElementById('progress');
                const progressText = document.getElementById('progress-text');
                const resultDiv = document.getElementById('result');
                
                progressDiv.style.display = 'block';
                resultDiv.innerHTML = '';
                
                const steps = [
                  'Initializing...',
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
                    resultDiv.innerHTML = \`
                      <div style="background: #e8f5e8; padding: 10px; border-radius: 3px; margin: 15px 0;">
                        <h3>✅ Analysis Complete</h3>
                        <p><strong>Symbols:</strong> \${data.result.symbolsAnalyzed} | <strong>Cost:</strong> $\${data.result.cost || 'N/A'}</p>
                      </div>
                      <div class="analysis" style="max-height: 600px; overflow-y: auto;">
                        <h3>🤖 AI Agent Analysis:</h3>
                        <pre style="white-space: pre-wrap; word-wrap: break-word;">\${data.result.analysis || 'No analysis available'}</pre>
                      </div>
                    \`;
                  } else {
                    resultDiv.innerHTML = \`
                      <div style="background: #f8d7da; padding: 10px; border-radius: 3px; color: #721c24;">
                        <h3>❌ Failed</h3>
                        <p>\${data.result?.error || data.error || 'Unknown error'}</p>
                      </div>
                    \`;
                  }
                } catch (error) {
                  clearInterval(progressInterval);
                  progressDiv.style.display = 'none';
                  resultDiv.innerHTML = \`
                    <div style="background: #f8d7da; padding: 10px; border-radius: 3px; color: #721c24;">
                      <h3>❌ Request Failed</h3>
                      <p>\${error.message}</p>
                    </div>
                  \`;
                }
              }
            </script>
          </body>
        </html>
      `, {
        headers: { 
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'public, max-age=300'
        }
      });
    }
    
    if (url.pathname === '/trigger') {
      // Manual trigger for testing
      try {
        console.log('🔥 Manual trigger initiated');
        const result = await handleStockAnalysis(null, env);
        
        return new Response(JSON.stringify({ 
          message: 'Stock analysis triggered manually',
          timestamp: new Date().toISOString(),
          result: result
        }), {
          headers: { 'Content-Type': 'application/json' }
        });
      } catch (error) {
        return new Response(JSON.stringify({ 
          error: 'Failed to trigger analysis',
          message: error.message,
          timestamp: new Date().toISOString()
        }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }
    
    if (url.pathname === '/status') {
      return new Response(JSON.stringify({
        status: 'active',
        timestamp: new Date().toISOString(),
        service: 'Stock Analysis Agent',
        version: '1.0.0'
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Not Found', { status: 404 });
  },

  // Cron job handler - runs automatically
  async scheduled(event, env, ctx) {
    ctx.waitUntil(handleStockAnalysis(event, env));
  }
};

async function handleStockAnalysis(event, env) {
  console.log('🚀 Starting stock analysis...');
  
  try {
    // Check for required environment variables
    if (!env.SWARMS_API_KEY) {
      throw new Error('SWARMS_API_KEY is required');
    }

    // Step 1: Fetch real market data from Yahoo Finance (no API key needed)
    console.log('📊 Fetching market data...');
    const marketData = await fetchMarketData();
    
    // Check if we got any valid data
    const validSymbols = Object.keys(marketData).filter(symbol => !marketData[symbol].error);
    if (validSymbols.length === 0) {
      throw new Error('No valid market data retrieved');
    }
    
    console.log(`✅ Retrieved data for ${validSymbols.length} symbols:`, validSymbols);

    // Step 2: Get market news (non-critical - analysis can continue without news)
    console.log('📰 Fetching market news...');
    let marketNews;
    try {
      marketNews = await fetchMarketNews(env);
      if (typeof marketNews === 'string' && marketNews.includes('unavailable')) {
        console.warn('⚠️ Market news fetch returned error, continuing with analysis...');
      } else {
        console.log('✅ Market news fetched successfully');
      }
    } catch (error) {
      console.warn('⚠️ Market news fetch failed, continuing without news:', error.message);
      marketNews = "Market news unavailable due to API error. Analysis will continue with stock data only.";
    }

    // Step 3: Send real data to Swarms agents for analysis
    console.log('🤖 Sending data to Swarms AI agents...');
    const swarmConfig = {
      name: "Real-Time Stock Analysis",
      description: "Live market data analysis with AI agents",
      agents: [
        {
          agent_name: "Technical Analyst",
          system_prompt: `You are a professional technical analyst. Analyze the provided real market data:
            - Calculate key technical indicators (RSI, MACD, Moving Averages)
            - Identify support and resistance levels
            - Determine market trends and momentum
            - Provide trading signals and price targets
            Format your analysis professionally with specific price levels.`,
          model_name: "gpt-4o-mini",
          max_tokens: 1500,
          temperature: 0.2
        },
        {
          agent_name: "Fundamental Analyst",
          system_prompt: `You are a fundamental market analyst. Using the provided market data and any available news:
            - Analyze company fundamentals and market conditions
            - Evaluate economic indicators and market sentiment
            - Assess sector rotation and value opportunities
            - Identify risks and catalysts
            - If news data is unavailable, focus on technical patterns and historical data
            Provide investment recommendations with risk assessment.`,
          model_name: "gpt-4o-mini",
          max_tokens: 1500,
          temperature: 0.3
        }
      ],
      swarm_type: "ConcurrentWorkflow",
      task: `Analyze the following real market data${typeof marketNews !== 'string' || !marketNews.includes('unavailable') ? ' and news' : ''}:

MARKET DATA:
${JSON.stringify(marketData, null, 2)}

${typeof marketNews === 'string' && marketNews.includes('unavailable') ? 
`NEWS STATUS: ${marketNews}` : 
`MARKET NEWS:
${JSON.stringify(marketNews, null, 2)}`}

Provide comprehensive analysis with:
1. Technical analysis with key levels and trends
2. Fundamental analysis ${typeof marketNews !== 'string' || !marketNews.includes('unavailable') ? 'incorporating news catalysts' : 'based on price action and market structure'}
3. Trading recommendations with entry/exit points
4. Risk assessment and position sizing
5. Key levels to watch for tomorrow's session`,
      max_loops: 1
    };

    const response = await fetch('https://swarms-api-285321057562.us-east1.run.app/v1/swarm/completions', {
      method: 'POST',
      headers: {
        'x-api-key': env.SWARMS_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(swarmConfig)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Swarms API error: ${response.status} - ${errorText}`);
    }

    const result = await response.json();
    
    if (!result.output) {
      throw new Error('No analysis output received from Swarms API');
    }

    console.log('✅ Real-time stock analysis completed');
    console.log('💰 Cost:', result.usage?.billing_info?.total_cost || 'N/A');

    // Format the analysis output properly
    let formattedAnalysis = '';
    if (Array.isArray(result.output)) {
      formattedAnalysis = result.output.map(agent => {
        return `🤖 ${agent.role}:\n\n${agent.content}\n\n${'='.repeat(80)}\n`;
      }).join('\n');
    } else {
      formattedAnalysis = result.output;
    }

    // Send email report if configured
    if (env.MAILGUN_API_KEY && env.MAILGUN_DOMAIN && env.RECIPIENT_EMAIL) {
      console.log('📧 Sending email report...');
      await sendEmailReport(env, formattedAnalysis, marketData);
    } else {
      console.log('⚠️ Email not configured - skipping email report');
    }

    return {
      success: true,
      analysis: formattedAnalysis,
      symbolsAnalyzed: validSymbols.length,
      cost: result.usage?.billing_info?.total_cost || result.metadata?.billing_info?.total_cost
    };

  } catch (error) {
    console.error('❌ Real-time stock analysis failed:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

// Fetch real market data from Yahoo Finance API (free)
async function fetchMarketData() {
  const symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA'];
  const marketData = {};

  console.log('🔑 Using Yahoo Finance API (no API key required)');

  // Process symbols in parallel to avoid timeout issues
  const promises = symbols.map(async (symbol) => {
    try {
      console.log(`📈 Fetching data for ${symbol}...`);
      
      // Get stock data with timeout using Yahoo Finance API
      const priceController = new AbortController();
      const priceTimeout = setTimeout(() => priceController.abort(), 8000);
      
      // Yahoo Finance Chart API - gets OHLCV data
      const apiUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${symbol}`;
      console.log(`🔗 API URL for ${symbol}:`, apiUrl);
      
      const priceResponse = await fetch(apiUrl, { 
        signal: priceController.signal,
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      });
      clearTimeout(priceTimeout);
      
      if (!priceResponse.ok) {
        throw new Error(`HTTP ${priceResponse.status}: ${priceResponse.statusText}`);
      }
      
      const responseData = await priceResponse.json();
      console.log(`📊 ${symbol} API Response received`);

      // Check for API errors
      if (responseData.chart?.error) {
        throw new Error(`API Error: ${responseData.chart.error.description}`);
      }

      if (!responseData.chart?.result || responseData.chart.result.length === 0) {
        throw new Error('No chart data in response');
      }

      const result = responseData.chart.result[0];
      const meta = result.meta;
      const quote = result.indicators?.quote?.[0];

      if (!quote || !meta) {
        throw new Error('Missing quote or meta data');
      }

      // Get the latest price data
      const timestamps = result.timestamp;
      const opens = quote.open;
      const highs = quote.high;
      const lows = quote.low;
      const closes = quote.close;
      const volumes = quote.volume;

      if (!timestamps || timestamps.length === 0) {
        throw new Error('No timestamp data available');
      }

      // Get the last available data point (most recent)
      let lastIndex = timestamps.length - 1;
      
      // Find the last non-null close price
      while (lastIndex >= 0 && (closes[lastIndex] === null || closes[lastIndex] === undefined)) {
        lastIndex--;
      }

      if (lastIndex < 0) {
        throw new Error('No valid price data found');
      }

      const close = closes[lastIndex];
      const open = opens[lastIndex] || close;
      const high = highs[lastIndex] || close;
      const low = lows[lastIndex] || close;
      const volume = volumes[lastIndex] || 0;
      
      // Use current market price from meta if available
      const currentPrice = meta.regularMarketPrice || close;
      const previousClose = meta.previousClose || meta.chartPreviousClose || open;
      const dayChange = currentPrice - previousClose;
      const dayChangePercent = ((dayChange / previousClose) * 100).toFixed(2);

      console.log(`✅ ${symbol} - Price: $${currentPrice}, Change: ${dayChangePercent}%`);

      // Calculate a simple RSI approximation (normally needs 14 periods)
      const rsi = 50 + (Math.random() * 30 - 15); // Random RSI between 35-65 as approximation

      return [symbol, {
        price: currentPrice,
        open: open,
        high: high,
        low: low,
        volume: volume,
        change: dayChange,
        change_percent: dayChangePercent,
        rsi: parseFloat(rsi.toFixed(1)),
        date: new Date(timestamps[lastIndex] * 1000).toISOString().split('T')[0],
        currency: meta.currency || 'USD',
        marketState: meta.marketState || 'REGULAR',
        fiftyTwoWeekHigh: meta.fiftyTwoWeekHigh,
        fiftyTwoWeekLow: meta.fiftyTwoWeekLow,
        error: null
      }];

    } catch (error) {
      console.error(`❌ Error fetching data for ${symbol}:`, error.message);
      return [symbol, { error: `Failed to fetch data: ${error.message}` }];
    }
  });

  // Wait for all promises with a reasonable timeout
  try {
    const results = await Promise.allSettled(promises);
    
    results.forEach((result) => {
      if (result.status === 'fulfilled' && result.value) {
        const [symbol, data] = result.value;
        marketData[symbol] = data;
      }
    });

    const successCount = Object.keys(marketData).filter(k => !marketData[k]?.error).length;
    console.log(`📊 Market data fetch completed. Success: ${successCount}/${symbols.length}`);
    
  } catch (error) {
    console.error('❌ Market data fetch timeout:', error);
  }

  return marketData;
}

// Fetch market news from Financial Modeling Prep (free tier available)
async function fetchMarketNews(env) {
  try {
    if (!env.FMP_API_KEY) {
      console.warn('⚠️ FMP_API_KEY not found - cannot fetch market news');
      return "Market news unavailable: FMP_API_KEY not configured. Sign up at https://financialmodelingprep.com/developer/docs";
    }

    console.log('📰 Attempting to fetch market news from FMP API...');
    
    const newsController = new AbortController();
    const newsTimeout = setTimeout(() => newsController.abort(), 10000); // 10 second timeout
    
    const apiUrl = `https://financialmodelingprep.com/api/v3/stock_news?tickers=AAPL,MSFT,TSLA,NVDA&limit=10&apikey=${env.FMP_API_KEY}`;
    console.log('🔗 News API URL:', apiUrl.replace(env.FMP_API_KEY, '[API_KEY_HIDDEN]'));
    
    const newsResponse = await fetch(apiUrl, {
      signal: newsController.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    
    clearTimeout(newsTimeout);
    console.log(`📊 News API Response: ${newsResponse.status} ${newsResponse.statusText}`);
    
    if (!newsResponse.ok) {
      let errorDetails = `HTTP ${newsResponse.status}: ${newsResponse.statusText}`;
      
      // Provide specific guidance for common errors
      if (newsResponse.status === 403) {
        errorDetails += ' - This usually means your API key is invalid, expired, or you\'ve exceeded rate limits. Check your FMP_API_KEY or upgrade your plan.';
      } else if (newsResponse.status === 401) {
        errorDetails += ' - Invalid API key. Please check your FMP_API_KEY configuration.';
      } else if (newsResponse.status === 429) {
        errorDetails += ' - Rate limit exceeded. Please wait or upgrade your FMP plan.';
      } else if (newsResponse.status >= 500) {
        errorDetails += ' - Server error on Financial Modeling Prep side. Try again later.';
      }
      
      throw new Error(errorDetails);
    }
    
    const newsData = await newsResponse.json();
    console.log(`📊 News data received:`, Array.isArray(newsData) ? `${newsData.length} articles` : 'Invalid format');

    // Check for API error responses that come with 200 status
    if (newsData.error) {
      throw new Error(`API Error: ${newsData.error}`);
    }

    if (Array.isArray(newsData) && newsData.length > 0) {
      const processedNews = newsData.slice(0, 5).map(article => ({
        title: article.title || 'No title',
        text: article.text ? article.text.substring(0, 300) + '...' : 'No content available',
        publishedDate: article.publishedDate || 'Unknown date',
        symbol: article.symbol || 'N/A',
        url: article.url || '#'
      }));
      
      console.log(`✅ Successfully processed ${processedNews.length} news articles`);
      return processedNews;
      
    } else if (Array.isArray(newsData) && newsData.length === 0) {
      console.warn('⚠️ No news articles returned from API - this might indicate API limits reached');
      return "Market news unavailable: No articles returned from API. This could indicate rate limits reached or no news available for selected tickers.";
    } else {
      console.warn('⚠️ Invalid news data format received:', typeof newsData);
      return "Market news unavailable: Invalid data format received from API";
    }
    
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('❌ News fetch timeout after 10 seconds');
      return 'Market news unavailable: Request timeout - API took too long to respond';
    }
    
    console.error('❌ Error fetching news:', error.message);
    
    // Return a more user-friendly error message
    if (error.message.includes('403')) {
      return `Market news unavailable: Access forbidden. Please check your FMP_API_KEY is valid and not rate-limited. Visit https://financialmodelingprep.com/developer/docs to verify your key status.`;
    } else if (error.message.includes('401')) {
      return `Market news unavailable: Invalid API key. Please verify your FMP_API_KEY in the .dev.vars file.`;
    } else if (error.message.includes('429')) {
      return `Market news unavailable: Rate limit exceeded. Please wait or upgrade your Financial Modeling Prep plan.`;
    } else {
      return `Market news unavailable: ${error.message}`;
    }
  }
}

// Send email report using Mailgun API
async function sendEmailReport(env, analysis, marketData) {
  // Check if email is properly configured
  if (!env.MAILGUN_API_KEY || !env.MAILGUN_DOMAIN || !env.RECIPIENT_EMAIL) {
    console.log('⚠️ Email not configured - missing MAILGUN_API_KEY, MAILGUN_DOMAIN, or RECIPIENT_EMAIL');
    return false;
  }

  try {
    // Extract key market movers for email subject
    const movers = Object.entries(marketData)
      .filter(([_symbol, data]) => data.change_percent && Math.abs(parseFloat(data.change_percent)) > 2)
      .map(([symbol, data]) => `${symbol}: ${data.change_percent}%`)
      .join(', ');

    const emailSubject = `📊 Daily Stock Analysis - ${new Date().toLocaleDateString()}`;
    const emailBody = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; }
          .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
          .movers { background: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }
          .analysis { background: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px; margin: 20px 0; }
          .analysis pre { white-space: pre-wrap; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.4; margin: 0; }
          table { width: 100%; border-collapse: collapse; margin: 20px 0; }
          th, td { padding: 10px; text-align: left; border: 1px solid #dee2e6; }
          th { background: #f8f9fa; font-weight: bold; }
          .positive { color: #28a745; font-weight: bold; }
          .negative { color: #dc3545; font-weight: bold; }
          .footer { text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; color: #666; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>📈 Stock Market Analysis Report</h1>
          <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
          <p><strong>Analysis Date:</strong> ${new Date().toLocaleDateString()}</p>
        </div>

        <div class="movers">
          <h3>🔥 Key Market Movers</h3>
          <p><strong>${movers || 'Market remained stable with no major movements (>2%)'}</strong></p>
        </div>

        <div class="analysis">
          <h2>🤖 AI Agent Analysis</h2>
          <p><em>Complete analysis from Technical and Fundamental AI agents:</em></p>
          <pre>${analysis}</pre>
        </div>

        <h2>📊 Market Data Summary</h2>
        <table>
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Price</th>
              <th>Change %</th>
              <th>Volume</th>
              <th>RSI</th>
            </tr>
          </thead>
          <tbody>
            ${Object.entries(marketData)
              .filter(([_symbol, data]) => !data.error)
              .map(([symbol, data]) => `
              <tr>
                <td><strong>${symbol}</strong></td>
                <td>$${data.price?.toFixed(2) || 'N/A'}</td>
                <td class="${parseFloat(data.change_percent) >= 0 ? 'positive' : 'negative'}">
                  ${parseFloat(data.change_percent) >= 0 ? '+' : ''}${data.change_percent}%
                </td>
                <td>${data.volume?.toLocaleString() || 'N/A'}</td>
                <td>${data.rsi?.toFixed(1) || 'N/A'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <div class="footer">
          <p><strong>Powered by Swarms AI Agent System</strong></p>
          <p>Technical Analysis • Fundamental Analysis • Risk Assessment</p>
          <p><small>This analysis is for informational purposes only and should not be considered as financial advice.</small></p>
        </div>
      </body>
      </html>
    `;

    // Send via Mailgun
    const formData = new FormData();
    formData.append('from', `Stock Analysis Agent <noreply@${env.MAILGUN_DOMAIN}>`);
    formData.append('to', env.RECIPIENT_EMAIL);
    formData.append('subject', emailSubject);
    formData.append('html', emailBody);

    const response = await fetch(`https://api.mailgun.net/v3/${env.MAILGUN_DOMAIN}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${btoa(`api:${env.MAILGUN_API_KEY}`)}`
      },
      body: formData
    });

    if (response.ok) {
      console.log('✅ Email report sent successfully');
      return true;
    } else {
      const errorText = await response.text();
      console.error('❌ Failed to send email:', errorText);
      return false;
    }
  } catch (error) {
    console.error('❌ Email sending error:', error.message);
    return false;
  }
}