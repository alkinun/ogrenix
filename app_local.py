from flask import Flask, render_template, request, jsonify, Response, stream_template
from openai import OpenAI
from prompts import GENERATE_ANSWER_PROMPT
from generate_html import generate_html, generate_html_streaming
import re
import json
import time
import requests
import base64
import io
import threading
from collections import defaultdict
import os

client_openrouter = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

client = OpenAI(
    base_url="http://0.0.0.0:8000/v1",
    api_key="EMPTY"
)

def llm_stream(prompt, max_tokens=6000):
    """Stream LLM response using OpenRouter's streaming API"""
    messages = [{"role": "user", "content": prompt}]
    stream = client.chat.completions.create(
        model="unsloth/GLM-4-32B-0414-unsloth-bnb-4bit",
        messages=messages,
        stream=True,
        #max_tokens=max_tokens,
        #temperature=.6,
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

def llm(prompt, max_tokens=6000):
    """Non-streaming version for backwards compatibility"""
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="unsloth/GLM-4-32B-0414-unsloth-bnb-4bit",
        messages=messages,
        #max_tokens=max_tokens,
        #temperature=.6,
    ).choices[0].message.content.strip()
    return response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

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
    # Running on port 5001 to avoid conflict with the LLM server
    app.run(debug=True, port=5001, use_reloader=False)
