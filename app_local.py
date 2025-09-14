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

# Global dictionary to track image generation status
image_generation_status = defaultdict(dict)

def generate_image(prompt):
    """Generate image using Google Gemini 2.5 Flash Image Preview via OpenRouter"""
    try:
        response = client_openrouter.chat.completions.create(
            model="google/gemini-2.5-flash-image-preview",
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
        )
        
        # The response contains the image as base64 data directly in content
        content = response.choices[0].message.content
        
        # The content should be base64 encoded image data
        if content and len(content) > 100:  # Base64 images are quite long
            # Remove any potential prefixes or whitespace
            content = content.strip()
            
            # Check if it's already valid base64 (it should be)
            try:
                # Test if it's valid base64
                base64.b64decode(content)
                return content
            except Exception:
                # If not valid base64, it might have some prefix, try to clean it
                # Look for base64 pattern
                import re
                base64_match = re.search(r'[A-Za-z0-9+/]+=*', content)
                if base64_match and len(base64_match.group(0)) > 100:
                    return base64_match.group(0)
            
        return None
        
    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return None

def llm_stream(prompt, max_tokens=6000):
    """Stream LLM response using OpenRouter's streaming API"""
    messages = [{"role": "user", "content": prompt}]
    stream = client.chat.completions.create(
        model="/home/alkin/Desktop/GradyanAkincilari/models/General-TR",
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
        model="/home/alkin/Desktop/GradyanAkincilari/models/General-TR",
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
    """Generate streaming response with non-blocking image generation"""
    def generate():
        try:
            prompt = GENERATE_ANSWER_PROMPT.format(question=question)
            
            accumulated_response = ""
            chunk_count = 0
            session_id = str(time.time())  # Unique session ID
            processed_image_blocks = set()  # Track processed image blocks
            
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting generation...'})}\n\n"
            
            for chunk in llm_stream(prompt):
                accumulated_response += chunk
                chunk_count += 1
                
                # Send text chunks for immediate feedback
                yield f"data: {json.dumps({'type': 'chunk', 'chunk': chunk})}\n\n"
                
                # Generate HTML every 2 chunks for maximum smoothness
                if chunk_count % 2 == 0:
                    try:
                        cleaned_md = clean_markdown_response(accumulated_response)
                        # Use streaming version that doesn't block on image generation
                        current_html = generate_html_streaming(cleaned_md, session_id, processed_image_blocks)
                        yield f"data: {json.dumps({'type': 'content', 'html': current_html})}\n\n"
                    except Exception as html_error:
                        # Continue with text-only if HTML generation fails
                        pass
                
                # Tiny delay to avoid overwhelming the client while keeping it ultra smooth
                time.sleep(0.0005)
            
            # Send final complete HTML (non-blocking; keep async image flow)
            if accumulated_response.strip():
                try:
                    final_md = clean_markdown_response(accumulated_response)
                    # Use streaming renderer to avoid blocking on image generation
                    final_html = generate_html_streaming(final_md, session_id, processed_image_blocks)
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
                       'Cache-Control': 'no-cache',
                       'Connection': 'keep-alive',
                       'Access-Control-Allow-Origin': '*'
                   })

@app.route("/image_status/<prompt_hash>", methods=["GET"])
def get_image_status(prompt_hash):
    """Get the status of an image generation request"""
    try:
        # Check if image is ready in our global status dict
        if prompt_hash in image_generation_status and 'image_data' in image_generation_status[prompt_hash]:
            img_base64 = image_generation_status[prompt_hash]['image_data']
            image_id = f"ai_image_{prompt_hash[:8]}"
            
            if img_base64:
                html = f'''<div class="ai-image-container" id="{image_id}">
    <img src="data:image/png;base64,{img_base64}" alt="AI Generated Image" class="ai-generated-image"/>
    <details class="code-toggle">
        <summary>Prompt'u Göster</summary>
        <pre class="code-block"><code class="language-text">{image_generation_status[prompt_hash].get('prompt', '')}</code></pre>
    </details>
</div>'''
                return jsonify({"status": "ready", "html": html})
            else:
                return jsonify({"status": "failed"})
        else:
            return jsonify({"status": "generating"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

if __name__ == "__main__":
    # Running on port 5001 to avoid conflict with the LLM server
    app.run(debug=True, port=5001, use_reloader=False)
