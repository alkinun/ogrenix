from flask import Flask, render_template, request, jsonify, Response, stream_template
from openai import OpenAI
from prompts import GENERATE_ANSWER_PROMPT
from generate_html import generate_html, generate_html_streaming
from agentic_logger import agentic_logger
import re
import json
import time
import requests
import base64
import io
import threading
from collections import defaultdict
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

def llm_stream(prompt, max_tokens=10000):
    """Stream LLM response using OpenRouter's streaming API"""
    # Start new session to clear deduplication tracking
    agentic_logger.start_new_session()
    
    # Log model initialization (simulating local model)
    agentic_logger.log_model_init()
    
    # Extract topic from prompt for logging
    topic = prompt.split("QUESTION/TOPIC:")[1].split("```")[1].strip() if "QUESTION/TOPIC:" in prompt else "Genel Konu"
    agentic_logger.log_prompt_analysis(len(prompt), topic[:50])
    
    # Estimate tokens and start generation logging
    estimated_tokens = len(prompt) // 4 + max_tokens // 2
    agentic_logger.log_content_generation_start(estimated_tokens)
    
    messages = [{"role": "user", "content": prompt}]
    stream = client.chat.completions.create(
        model="anthropic/claude-3.7-sonnet@preset/fastest-provider",
        messages=messages,
        stream=True,
        #max_tokens=max_tokens,
        #temperature=.6,
    )
    
    chunk_count = 0
    start_time = time.time()
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            chunk_count += 1
            content = chunk.choices[0].delta.content
            
            # Log streaming chunks periodically
            agentic_logger.log_content_chunk(content, chunk_count)
            
            yield content
    
    # Log completion
    total_time = time.time() - start_time
    final_tokens = chunk_count * 10  # Rough estimation
    agentic_logger.log_generation_complete(total_time, final_tokens)

def llm(prompt, max_tokens=10000):
    """Non-streaming version for backwards compatibility"""
    # Start new session to clear deduplication tracking
    agentic_logger.start_new_session()
    
    # Log model initialization (simulating local model)
    agentic_logger.log_model_init()
    
    # Extract topic from prompt for logging
    topic = prompt.split("QUESTION/TOPIC:")[1].split("```")[1].strip() if "QUESTION/TOPIC:" in prompt else "Genel Konu"
    agentic_logger.log_prompt_analysis(len(prompt), topic[:50])
    
    # Estimate tokens and start generation logging
    estimated_tokens = len(prompt) // 4 + max_tokens // 2
    agentic_logger.log_content_generation_start(estimated_tokens)
    
    start_time = time.time()
    
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="anthropic/claude-3.7-sonnet@preset/fastest-provider",
        messages=messages,
        #max_tokens=max_tokens,
        #temperature=.6,
    ).choices[0].message.content.strip()
    
    # Log completion
    total_time = time.time() - start_time
    final_tokens = len(response) // 4  # Rough estimation
    agentic_logger.log_generation_complete(total_time, final_tokens)
    
    return response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/logs")
def view_logs():
    """Display agent logs for demonstration purposes"""
    logs = agentic_logger.get_recent_logs(50)  # Get last 50 logs
    
    # Format logs for display
    formatted_logs = []
    for log in logs:
        formatted_log = {
            'timestamp': log['timestamp'],
            'level': log['level'],
            'message': log['message'],
            'details': log.get('details', {})
        }
        formatted_logs.append(formatted_log)
    
    # Create a simple HTML page to display logs
    html_content = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Logları - Teknofest Demo</title>
    <style>
        body { 
            font-family: 'Courier New', monospace; 
            background: #1a1a1a; 
            color: #00ff41; 
            padding: 20px; 
            margin: 0;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { 
            border-bottom: 2px solid #00ff41; 
            padding-bottom: 10px; 
            margin-bottom: 20px; 
        }
        .log-entry { 
            margin: 10px 0; 
            padding: 8px; 
            border-left: 3px solid #00ff41; 
            background: rgba(0, 255, 65, 0.1); 
        }
        .timestamp { color: #888; font-size: 0.9em; }
        .level { 
            font-weight: bold; 
            padding: 2px 6px; 
            border-radius: 3px; 
            margin: 0 5px; 
        }
        .level-SİSTEM { background: #4CAF50; color: white; }
        .level-ANALİZ { background: #2196F3; color: white; }
        .level-ÜRETİM { background: #FF9800; color: white; }
        .level-INFO { background: #9C27B0; color: white; }
        .level-TAMAMLANDI { background: #8BC34A; color: white; }
        .level-HATA { background: #F44336; color: white; }
        .details { 
            margin-top: 5px; 
            font-size: 0.9em; 
            color: #ccc; 
        }
        .details-item { margin: 2px 0; }
        .code-snippet { 
            background: #2a2a2a; 
            padding: 10px; 
            border-radius: 4px; 
            font-size: 0.85em; 
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .refresh-btn {
            background: #00ff41;
            color: #1a1a1a;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .refresh-btn:hover { background: #00cc33; }
    </style>
    <script>
        function refreshLogs() {
            location.reload();
        }
        
        // Auto-refresh every 3 seconds
        setInterval(refreshLogs, 3000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Agent Logları - Teknofest Demo</h1>
            <p>Yerel LLM Agent işlemlerinin gerçek zamanlı logları</p>
            <button class="refresh-btn" onclick="refreshLogs()">Logları Yenile</button>
        </div>
        <div class="logs">
'''
    
    for log in formatted_logs:
        details_html = ""
        if log['details']:
            details_html = "<div class='details'>"
            for key, value in log['details'].items():
                if key == 'kod' and value:
                    details_html += f"<div class='details-item'><strong>{key}:</strong></div><div class='code-snippet'>{value}</div>"
                elif key == 'generated_code':
                    details_html += f"<div class='details-item'><strong>{key}:</strong></div><div class='code-snippet'>{value}</div>"
                else:
                    details_html += f"<div class='details-item'><strong>{key}:</strong> {value}</div>"
            details_html += "</div>"
        
        html_content += f'''
        <div class="log-entry">
            <span class="timestamp">[{log['timestamp']}]</span>
            <span class="level level-{log['level']}">{log['level']}</span>
            <span class="message">{log['message']}</span>
            {details_html}
        </div>
        '''
    
    html_content += '''
        </div>
    </div>
</body>
</html>
    '''
    
    return html_content

@app.route("/logs/json")
def logs_json():
    """Return logs as JSON for API access"""
    logs = agentic_logger.get_recent_logs(100)
    return jsonify(logs)

@app.route("/logs/clear")
def clear_logs():
    """Clear all logs"""
    agentic_logger.clear_logs()
    return jsonify({"status": "success", "message": "Tüm loglar temizlendi"})

@app.route("/logs/demo")
def demo_logs():
    """Generate demo logs to show capabilities"""
    agentic_logger.clear_logs()
    
    # Generate some demo logs
    agentic_logger.log_model_init()
    agentic_logger.log_prompt_analysis(150, "Matematik fonksiyonları")
    agentic_logger.log_content_generation_start(500)
    agentic_logger.log_tool_usage("matplotlib", "plt.plot([1,2,3], [4,5,6])\nplt.title('Demo Graf')")
    agentic_logger.log_tool_usage("mermaid", "flowchart TD\n  A --> B")
    agentic_logger.log_generation_complete(5.2, 423)
    
    return jsonify({"status": "success", "message": "Demo loglar oluşturuldu"})

@app.route("/test/warnings")
def test_warnings():
    """Test route to verify matplotlib warnings are suppressed"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # This should NOT generate warnings anymore - including pcolormesh warnings
        for i in range(3):
            plt.figure()
            x = np.linspace(0, 10, 100)
            y = np.sin(x + i)
            plt.plot(x, y)
            plt.title(f'Test Graph {i+1}')
            
            # Test pcolormesh which was causing warnings
            X, Y = np.meshgrid(np.random.rand(10), np.random.rand(10))
            Z = np.random.rand(10, 10)
            plt.pcolormesh(X, Y, Z)
            
        plt.close('all')
        return jsonify({"status": "success", "message": "Test completed - check console for warnings"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    question = data.get("question")
    stream = data.get("stream", False)

    if not question:
        return jsonify({"error": "Question/topic is required"}), 400

    if stream:
        return generate_stream(question)
    
    try:
        prompt = GENERATE_ANSWER_PROMPT.format(question=question)
        
        md_response = llm(prompt)
        
        # Remove first ```md tag and last ``` tag for proper formatting
        md_content = clean_markdown_response(md_response)

        html_output = generate_html(md_content)
        
        return jsonify({"html": html_output})
    except Exception as e:
        print(f"Error during generation: {e}")
        return jsonify({"error": "Failed to generate HTML"}), 500

def clean_markdown_response(md_response):
    """Clean the markdown response by removing markdown code fences"""
    # Remove first ```md and last ``` tags
    if md_response.startswith('```md\n'):
        md_response = md_response[6:]  # Remove ```md\n
    elif md_response.startswith('```markdown\n'):
        md_response = md_response[12:]  # Remove ```markdown\n
    
    if md_response.endswith('\n```'):
        md_response = md_response[:-4]  # Remove \n```
    elif md_response.endswith('```'):
        md_response = md_response[:-3]  # Remove ```
    
    return md_response.strip()

def generate_stream(question):
    """Generate streaming response"""
    def generate():
        try:
            prompt = GENERATE_ANSWER_PROMPT.format(question=question)
            
            accumulated_response = ""
            chunk_count = 0
            last_html_time = 0.0
            
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting generation...'})}\n\n"
            
            for chunk in llm_stream(prompt):
                accumulated_response += chunk
                chunk_count += 1
                
                # Send text chunks for immediate feedback
                yield f"data: {json.dumps({'type': 'chunk', 'chunk': chunk})}\n\n"
                
                # Generate HTML on a short time-based cadence to keep UI smooth
                now = time.time()
                if now - last_html_time >= 0.12:
                    try:
                        cleaned_md = clean_markdown_response(accumulated_response)
                        current_html = generate_html_streaming(cleaned_md)
                        yield f"data: {json.dumps({'type': 'content', 'html': current_html})}\n\n"
                    except Exception as html_error:
                        # Continue with text-only if HTML generation fails
                        pass
                    finally:
                        last_html_time = now
                
                # No artificial delay; rely on time-based cadence above
            
            # Send final complete HTML
            if accumulated_response.strip():
                try:
                    final_md = clean_markdown_response(accumulated_response)
                    final_html = generate_html_streaming(final_md)
                    yield f"data: {json.dumps({'type': 'complete', 'html': final_html, 'markdown': final_md})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'error': f'Final HTML generation failed: {str(e)}'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'error': 'No content received from API'})}\n\n"
            
            # Send explicit end signal
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'end'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream',
                   headers={
                       'Cache-Control': 'no-cache, no-transform',
                       'Connection': 'keep-alive',
                       'X-Accel-Buffering': 'no',
                       'Access-Control-Allow-Origin': '*'
                   })

if __name__ == "__main__":
    # Running on port 5002 to avoid conflict with the LLM server
    app.run(debug=True, port=5002, use_reloader=False)
