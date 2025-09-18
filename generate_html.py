import re
import markdown
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from markdown.extensions import codehilite, tables, toc
import hashlib
import uuid
import requests
import threading
import time
import warnings
from agentic_logger import agentic_logger

# Suppress matplotlib warnings for cleaner console output
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', category=RuntimeWarning, module='matplotlib')
warnings.filterwarnings('ignore', category=UserWarning, message='.*pcolormesh.*')
warnings.filterwarnings('ignore', category=UserWarning, message='.*FigureCanvasAgg.*')
warnings.filterwarnings('ignore', category=UserWarning, message='.*cell centers.*')
warnings.filterwarnings('ignore', category=UserWarning, message='.*cell edges.*')
warnings.filterwarnings('ignore', category=UserWarning, message='.*monotonically.*')
matplotlib.pyplot.ioff()  # Turn off interactive mode
plt.rcParams['figure.max_open_warning'] = 0  # Disable figure limit warnings

# Additional matplotlib configuration to prevent warnings
import matplotlib
matplotlib.rcParams['axes.formatter.useoffset'] = False
matplotlib.rcParams['figure.raise_window'] = False

def generate_html(md_str):
    """
    Convert markdown with special components (mermaid, matplotlib, p5js) to polished HTML
    
    Args:
        md_str (str): Markdown string with special code blocks
        
    Returns:
        str: Complete HTML document with embedded components
    """
    
    # Step 0: Replace any incomplete special code fences with placeholders
    md_str = preprocess_incomplete_blocks(md_str)
    
    # Step 1: Process matplotlib code blocks
    processed_md = process_matplotlib_blocks(md_str)
    
    # Step 2: Process mermaid diagrams
    processed_md = process_mermaid_blocks(processed_md)
    
    # Step 3: Process p5.js sketches
    processed_md = process_p5js_blocks(processed_md)
    
    # AI image blocks removed
    
    # Step 5: Convert markdown to HTML
    md_processor = markdown.Markdown(
        extensions=[
            'codehilite',
            'tables',
            'toc',
            'fenced_code',
            'attr_list',
            'def_list',
            'footnotes',
            'md_in_html'
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True
            },
            'toc': {
                'title': 'İçindekiler'
            }
        }
    )
    
    html_content = md_processor.convert(processed_md)
    
    # Step 6: Generate complete HTML document
    full_html = generate_complete_html(html_content)
    
    return full_html

def generate_html_streaming(md_str):
    """Streaming-safe HTML rendering"""
    
    # Step 0: Replace any incomplete special code fences with placeholders
    md_str = preprocess_incomplete_blocks(md_str)
    
    # Step 1: Process matplotlib code blocks
    processed_md = process_matplotlib_blocks(md_str)
    
    # Step 2: Process mermaid diagrams
    processed_md = process_mermaid_blocks(processed_md)
    
    # Step 3: Process p5.js sketches
    processed_md = process_p5js_blocks(processed_md)
    
    # AI image blocks removed in streaming
    
    # Step 5: Convert markdown to HTML
    md_processor = markdown.Markdown(
        extensions=[
            'codehilite',
            'tables',
            'toc',
            'fenced_code',
            'attr_list',
            'def_list',
            'footnotes',
            'md_in_html'
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True
            },
            'toc': {
                'title': 'İçindekiler'
            }
        }
    )
    
    html_content = md_processor.convert(processed_md)
    
    # Step 6: Generate complete HTML document
    full_html = generate_complete_html(html_content)
    
    return full_html

def preprocess_incomplete_blocks(md_str: str) -> str:
    """Detect incomplete special code fences during streaming and replace them
    with placeholder containers so users see a loader box instead of raw code.
    
    This handles the following fence starts when the closing ``` is missing:
    - ```mermaid
    - ```p5js
    - ```python.matplotlib
    
    """
    def replace_incomplete(md: str, fence_lang: str, placeholder_html: str) -> str:
        # Look for occurrences of the starting fence
        start_token = f"```{fence_lang}"
        search_pos = 0
        while True:
            start_idx = md.find(start_token, search_pos)
            if start_idx == -1:
                break
            # Find the next closing fence after the start
            close_idx = md.find("\n```", start_idx + len(start_token))
            if close_idx == -1:
                # No closing fence → replace from start to end with placeholder
                return md[:start_idx] + placeholder_html
            # Otherwise continue searching after this closed block
            search_pos = close_idx + 4
        return md
    
    # Mermaid placeholder
    mermaid_placeholder = (
        '<div class="diagram-container">\n'
        '    <div class="mermaid" data-pending="1"></div>\n'
        '    <details class="code-toggle">\n'
        '        <summary>Kodu Göster</summary>\n'
        '        <pre class="code-block"><code class="language-mermaid"></code></pre>\n'
        '    </details>\n'
        '</div>'
    )
    # p5.js placeholder
    p5_placeholder = (
        '<div class="p5js-container">\n'
        '    <div class="p5js" data-pending="1">\n'
        '        <div class="p5js-canvas"></div>\n'
        '    </div>\n'
        '    <details class="code-toggle">\n'
        '        <summary>Kodu Göster</summary>\n'
        '        <pre class="code-block"><code class="language-javascript"></code></pre>\n'
        '    </details>\n'
        '</div>'
    )
    # Matplotlib placeholder
    mpl_placeholder = (
        '<div class="chart-container" data-pending="1">\n'
        '    <!-- Grafik hazırlanıyor... -->\n'
        '</div>'
    )
    
    md_str = replace_incomplete(md_str, 'mermaid', mermaid_placeholder)
    md_str = replace_incomplete(md_str, 'p5js', p5_placeholder)
    md_str = replace_incomplete(md_str, 'python.matplotlib', mpl_placeholder)
    return md_str

def process_matplotlib_blocks(md_str):
    """Extract and execute matplotlib code blocks, replace with img tags"""
    
    # Pattern to match ```python.matplotlib code blocks
    pattern = r'```python\.matplotlib\n(.*?)\n```'
    
    def clean_matplotlib_code(code):
        """Remove emoji characters from matplotlib title functions, fix string literals, and clean plt.show() calls"""
        import re
        
        def clean_title_text(text):
            # Remove emoji and special Unicode characters, keep only ASCII letters, numbers, and common symbols
            # Also replace newlines with spaces
            text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
            return re.sub(r'[^\w\s\(\)\[\]\{\}\+\-\*\/\=\.\,\:\;\|\^\$\\\\°\']+', '', text).strip()
        
        # Remove plt.show() calls to prevent warnings in non-interactive mode
        code = re.sub(r'plt\.show\(\s*\)', '', code, flags=re.MULTILINE)
        
        # Simple approach: fix all multi-line strings in the code first
        lines = code.split('\n')
        in_multiline_string = False
        quote_char = None
        fixed_lines = []
        current_line = ""
        
        for line in lines:
            if not in_multiline_string:
                # Check if this line starts a multi-line string
                if ("title(" in line or "set_title(" in line):
                    # Look for unclosed quotes
                    single_quotes = line.count("'") - line.count("\\'")
                    double_quotes = line.count('"') - line.count('\\"')
                    
                    # If odd number of quotes, this starts a multi-line string
                    if single_quotes % 2 == 1:
                        in_multiline_string = True
                        quote_char = "'"
                        current_line = line
                        continue
                    elif double_quotes % 2 == 1:
                        in_multiline_string = True 
                        quote_char = '"'
                        current_line = line
                        continue
                
                fixed_lines.append(line)
            else:
                # We're in a multi-line string, look for the closing quote
                current_line += "\\n" + line  # Add escaped newline
                if quote_char and quote_char in line and not line.endswith('\\' + quote_char):
                    # Found the closing quote, end multi-line string
                    in_multiline_string = False
                    fixed_lines.append(current_line)
                    current_line = ""
                    quote_char = None
        
        code = '\n'.join(fixed_lines)
        
        # Now clean the titles - remove emojis and normalize
        code = re.sub(r"(\w*\.?(?:title|set_title))\('([^']*)'", 
                     lambda m: f"{m.group(1)}('{clean_title_text(m.group(2))}'", code)
        
        code = re.sub(r'(\w*\.?(?:title|set_title))\("([^"]*)"',
                     lambda m: f'{m.group(1)}("{clean_title_text(m.group(2))}"', code)
        
        return code
    
    def replace_matplotlib(match):
        code = match.group(1)
        
        try:
            # Clean the code to remove emojis from titles and plt.show() calls
            cleaned_code = clean_matplotlib_code(code)
            
            # Close any existing figures to prevent memory leaks and warnings
            plt.close('all')
            
            # Create a new figure with minimal styling
            plt.figure(figsize=(10, 6))
            plt.style.use('seaborn-v0_8-whitegrid')
            
            # Create execution context with necessary imports
            exec_globals = {
                'plt': plt,
                'matplotlib': matplotlib,
                '__builtins__': __builtins__
            }
            
            # Add optional imports with error handling
            try:
                import numpy as np
                exec_globals['np'] = np
                exec_globals['numpy'] = np
            except ImportError:
                pass
                
            try:
                import seaborn as sns
                exec_globals['sns'] = sns
                exec_globals['seaborn'] = sns
            except ImportError:
                pass
                
            try:
                import pandas as pd
                exec_globals['pd'] = pd
                exec_globals['pandas'] = pd
            except ImportError:
                pass
                
            # Add standard library modules
            import math
            import random
            exec_globals['math'] = math
            exec_globals['random'] = random
            
            # Execute the cleaned matplotlib code with comprehensive warning suppression
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                exec(cleaned_code, exec_globals)
            
            # Save plot to base64 string with warning suppression
            img_buffer = io.BytesIO()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                           facecolor='#faf9f7', edgecolor='none')
            img_buffer.seek(0)
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close('all')  # Close all figures to free memory and prevent warnings
            
            # Log tool usage
            agentic_logger.log_tool_usage("matplotlib", code)
            
            # Generate unique ID for the chart
            chart_id = f"chart_{uuid.uuid4().hex[:8]}"
            
            # Return HTML img tag with styling
            return f'''<div class="chart-container" id="{chart_id}">
    <img src="data:image/png;base64,{img_str}" alt="Grafik" class="chart-image"/>
    <details class="code-toggle">
        <summary>Kodu Göster</summary>
        <pre class="code-block"><code class="language-python">{code}</code></pre>
    </details>
</div>'''
            
        except Exception as e:
            # Ensure cleanup even on error
            plt.close('all')
            
            # Log error
            agentic_logger.log_error("Matplotlib Execution Error", str(e), f"Code: {code[:100]}...")
            
            # Return error message if code execution fails
            return f'''<div class="error-box">
    <div class="error-title">Grafik Hatası</div>
    <div class="error-message">{str(e)}</div>
    <details class="code-toggle">
        <summary>Kod</summary>
        <pre class="code-block"><code class="language-python">{code}</code></pre>
    </details>
</div>'''
    
    return re.sub(pattern, replace_matplotlib, md_str, flags=re.DOTALL)

def process_mermaid_blocks(md_str):
    """Process mermaid code blocks and prepare them for rendering"""
    
    # Pattern to match ```mermaid code blocks
    pattern = r'```mermaid\n(.*?)\n```'
    
    def sanitize_mermaid_code(code: str) -> str:
        """Make common LLM outputs valid for Mermaid.
        - Replace unicode arrows with Mermaid connectors
        - Normalize smart quotes
        - If the diagram is a single line (no newlines), insert newlines after the header
          and before each node/edge so Mermaid can parse it without semicolons.
        """
        import re as _re
        if not code:
            return code
        # Normalize arrows and quotes
        code = (code
                .replace('→', '-->')
                .replace('⇒', '-->')
                .replace('—>', '-->')
                .replace('->', '-->')
                .replace('“', '"').replace('”', '"').replace('’', "'")
        )
        # If it's a one-liner flowchart/graph, break it into multiple lines
        if ('\n' not in code) and code.strip().startswith(('flowchart', 'graph')):
            m = _re.match(r'^(\s*(?:flowchart|graph)\s+\w+)\s+(.*)$', code.strip())
            if m:
                header, rest = m.group(1), m.group(2)
                # Insert newlines before probable node/edge starts: " A[", " A(", " A-->"
                rest = _re.sub(r"\s+(?=([A-Za-z][A-Za-z0-9_]*)\s*(?:\[|\(|-->|==|===|<-|->))", "\n", rest)
                # Also break after closing bracket/paren when followed by another node
                rest = _re.sub(r"\](?=\s*[A-Za-z][A-Za-z0-9_]*\s*(?:\[|\(|-->|==|===|<-|->))", "]\n", rest)
                rest = _re.sub(r"\)(?=\s*[A-Za-z][A-Za-z0-9_]*\s*(?:\[|\(|-->|==|===|<-|->))", ")\n", rest)
                code = f"{header}\n{rest}"
        return code
    
    def replace_mermaid(match):
        mermaid_code = sanitize_mermaid_code(match.group(1).strip())
        
        diagram_id = f"mermaid_{uuid.uuid4().hex[:8]}"
        stable_key = hashlib.sha1(mermaid_code.encode('utf-8')).hexdigest()[:16]
        
        # Log tool usage
        agentic_logger.log_tool_usage("mermaid", mermaid_code)
        
        return f'''<div class="diagram-container" id="{diagram_id}">
    <div class="mermaid" data-mermaid-key="{stable_key}">{mermaid_code}</div>
    <details class="code-toggle">
        <summary>Kodu Göster</summary>
        <pre class="code-block"><code class="language-mermaid">{mermaid_code}</code></pre>
    </details>
</div>'''
    
    return re.sub(pattern, replace_mermaid, md_str, flags=re.DOTALL)

def process_p5js_blocks(md_str):
    """Process p5.js code blocks and prepare them for rendering"""
    
    # Pattern to match ```p5js code blocks
    pattern = r'```p5js\n(.*?)\n```'
    
    def replace_p5js(match):
        p5js_code = match.group(1).strip()
        
        sketch_id = f"p5js_{uuid.uuid4().hex[:8]}"
        canvas_id = f"canvas_{sketch_id}"
        
        # Log tool usage
        agentic_logger.log_tool_usage("p5js", p5js_code)
        
        return f'''<div class="p5js-container" id="{sketch_id}">
    <div class="p5js">
        <div class="p5js-canvas" id="{canvas_id}"></div>
        <script class="p5js-sketch">{p5js_code}</script>
    </div>
    <details class="code-toggle">
        <summary>Kodu Göster</summary>
        <pre class="code-block"><code class="language-javascript">{p5js_code}</code></pre>
    </details>
</div>'''
    
    return re.sub(pattern, replace_p5js, md_str, flags=re.DOTALL)

def process_image_blocks(md_str):
    return md_str

def process_image_blocks_streaming(md_str):
    return md_str

def get_existing_image_html(prompt_hash, image_prompt):
    return ''

def start_background_image_generation(prompt_hash, image_prompt, session_id):
    return None

def generate_complete_html(html_content):
    """Generate complete HTML document with minimal, modern styling"""
    
    html_tpl = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ders Notları</title>
    
    <!-- Mermaid JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.0/mermaid.min.js"></script>
    
    <!-- p5.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
    
    <!-- Highlight.js for code syntax highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    
    <!-- MathJax for LaTeX rendering (correct path) -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.2/es5/tex-mml-chtml.js"></script>
    
    <!-- Inter Font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* CSS Reset */
        *, *::before, *::after {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        /* Root Variables - Beige Light Theme */
        :root {{
            /* Base Colors */
            --bg-primary: #faf9f7;
            --bg-secondary: #f5f4f1;
            --bg-tertiary: #ebe9e6;
            --bg-accent: #e8e6e3;
            
            /* Text Colors */
            --text-primary: #2c2a26;
            --text-secondary: #5a5753;
            --text-muted: #8b8680;
            --text-accent: #6b4e3d;
            
            /* Border Colors */
            --border-light: #e8e6e3;
            --border-medium: #d4d1cc;
            --border-dark: #bfbbb4;
            
            /* Accent Colors */
            --accent-primary: #8b5a3c;
            --accent-secondary: #a67c52;
            --accent-hover: #7a4d33;
            
            /* Status Colors */
            --error-bg: #fdf2f2;
            --error-border: #f5b2b2;
            --error-text: #c53030;
            
            /* Shadows */
            --shadow-sm: 0 1px 2px rgba(44, 42, 38, 0.05);
            --shadow-md: 0 4px 6px rgba(44, 42, 38, 0.07);
            --shadow-lg: 0 10px 15px rgba(44, 42, 38, 0.1);
            
            /* Typography */
            --font-mono: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            
            /* Spacing */
            --space-xs: 0.25rem;
            --space-sm: 0.5rem;
            --space-md: 1rem;
            --space-lg: 1.5rem;
            --space-xl: 2rem;
            --space-2xl: 3rem;
        }}
        
        /* Base Styles */
        html {{
            font-size: 16px;
            line-height: 1.6;
            /* Keep scrollbar space reserved to avoid layout shifts during smooth scroll */
            scrollbar-gutter: stable both-edges;
        }}
        
        body {{
            font-family: var(--font-sans);
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-weight: 400;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            /* Prevent iOS/Chrome rubber-banding from causing jitter in nested content */
            overscroll-behavior-y: none;
        }}
        
        /* Layout */
        .container {{
            max-width: 120ch;
            margin: 0 auto;
            /* Reduced top/bottom padding from 3rem to 1.5rem */
            padding: var(--space-lg) var(--space-lg);
        }}
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600;
            line-height: 1.3;
            color: var(--text-primary);
            margin-bottom: var(--space-lg);
        }}
        
        h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            margin-bottom: var(--space-2xl);
            padding-bottom: var(--space-lg);
            border-bottom: 1px solid var(--border-light);
        }}
        
        h2 {{
            font-size: 1.75rem;
            margin-top: var(--space-2xl);
            margin-bottom: var(--space-lg);
        }}
        
        h3 {{
            font-size: 1.375rem;
            margin-top: var(--space-xl);
            color: var(--text-accent);
        }}
        
        h4 {{
            font-size: 1.125rem;
            margin-top: var(--space-lg);
            color: var(--text-secondary);
        }}
        
        p {{
            margin-bottom: var(--space-lg);
            color: var(--text-secondary);
            line-height: 1.7;
        }}
        
        /* Links */
        a {{
            color: var(--accent-primary);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s ease;
        }}
        
        a:hover {{
            border-bottom-color: var(--accent-primary);
        }}
        
        /* Lists */
        ul, ol {{
            margin: var(--space-lg) 0;
            padding-left: var(--space-xl);
        }}
        
        li {{
            margin-bottom: var(--space-sm);
            color: var(--text-secondary);
        }}
        
        ul li::marker {{
            color: var(--text-muted);
        }}
        
        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: var(--space-xl) 0;
            font-size: 0.9rem;
        }}
        
        th, td {{
            text-align: left;
            padding: var(--space-md);
            border-bottom: 1px solid var(--border-light);
        }}
        
        th {{
            font-weight: 600;
            color: var(--text-primary);
            background-color: var(--bg-secondary);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }}
        
        tbody tr:hover {{
            background-color: var(--bg-secondary);
        }}
        
        /* Code */
        code {{
            font-family: var(--font-mono);
            font-size: 0.875em;
            background-color: var(--bg-tertiary);
            padding: 0.125em 0.25em;
            border-radius: 3px;
            color: var(--text-primary);
        }}
        
        pre {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: 6px;
            padding: var(--space-lg);
            margin: var(--space-xl) 0;
            overflow-x: auto;
            font-size: 0.875rem;
            line-height: 1.5;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            border-radius: 0;
        }}
        
        .code-block {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: 6px;
            padding: var(--space-lg);
            margin: var(--space-md) 0 0 0;
            overflow-x: auto;
            font-size: 0.875rem;
        }}
        
        /* Blockquotes */
        blockquote {{
            border-left: 3px solid var(--accent-secondary);
            padding-left: var(--space-lg);
            margin: var(--space-xl) 0;
            color: var(--text-secondary);
            font-style: italic;
        }}
        
        /* Interactive Elements */
        .code-toggle {{
            margin-top: var(--space-md);
        }}
        
        .code-toggle summary {{
            cursor: pointer;
            color: var(--text-muted);
            font-size: 0.875rem;
            user-select: none;
            padding: var(--space-sm) var(--space-md);
            border-top: 1px solid var(--border-light);
            transition: color 0.2s ease;
        }}
        
        .code-toggle summary:hover {{
            color: var(--text-secondary);
        }}
        
        .code-toggle[open] summary {{
            color: var(--text-secondary);
            margin-bottom: var(--space-sm);
        }}
        
        /* Chart Containers */
        .chart-container {{
            margin: var(--space-xl) 0;
            border: 1px solid var(--border-light);
            border-radius: 8px;
            overflow: hidden;
            background-color: var(--bg-secondary);
        }}
        
        .chart-image {{
            width: 100%;
            height: auto;
            display: block;
            background-color: var(--bg-primary);
        }}
        
        /* AI Generated Image Containers */
        .ai-image-container {{
            margin: var(--space-2xl) auto;
            border: 1px solid var(--border-light);
            border-radius: 10px;
            overflow: hidden;
            background-color: var(--bg-secondary);
            /* shrink to image width and center */
            width: fit-content;
            max-width: 100%;
            display: block;
            box-shadow: var(--shadow-sm);
        }}
        
        .ai-generated-image {{
            width: auto;
            max-width: 100%;
            max-height: 75vh;
            height: auto;
            display: block;
            background-color: var(--bg-primary);
            object-fit: contain;
        }}
        
        /* Diagram Containers */
        .diagram-container {{
            margin: var(--space-xl) 0;
            border: 1px solid var(--border-light);
            border-radius: 8px;
            background-color: var(--bg-secondary);
        }}
        
        .mermaid {{
            padding: var(--space-xl);
            background-color: var(--bg-primary);
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
        }}
        /* Scale SVGs to fit container with max dimensions */
        .mermaid svg {{
            max-width: 100% !important;
            max-height: 600px !important;
            width: auto !important;
            height: auto !important;
            object-fit: contain !important;
        }}
        .mermaid .messageText, .mermaid .nodeLabel, .mermaid text {{ font-family: var(--font-sans) !important; }}
        /* While streaming, hide raw mermaid text and show a soft placeholder */
        .mermaid[data-pending="1"] {{ color: transparent; position: relative; min-height: 120px; }}
        .mermaid[data-pending="1"]::after {{ content: 'Diyagram hazırlanıyor…'; color: var(--text-muted); position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-size: 0.95rem; }}
        /* p5.js placeholder while streaming */
        .p5js[data-pending="1"] {{ position: relative; }}
        .p5js[data-pending="1"]::after {{ content: 'Sketch hazırlanıyor…'; color: var(--text-muted); position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-size: 0.95rem; }}
        /* Matplotlib placeholder while streaming */
        .chart-container[data-pending="1"] {{ position: relative; min-height: 160px; background-color: var(--bg-secondary); }}
        .chart-container[data-pending="1"]::after {{ content: 'Grafik hazırlanıyor…'; color: var(--text-muted); position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-size: 0.95rem; }}
        /* AI image placeholder while generating */
        .ai-image-container[data-pending="1"] {{ position: relative; min-height: 240px; background-color: var(--bg-secondary); width: fit-content; max-width: 100%; min-width: 340px; margin-left: auto; margin-right: auto; }}
        .ai-image-container[data-pending="1"]::after {{ content: 'Görsel oluşturuluyor…'; color: var(--text-muted); position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-size: 0.95rem; }}
        
        /* p5.js Containers */
        .p5js-container {{
            margin: var(--space-xl) 0;
            border: 1px solid var(--border-light);
            border-radius: 8px;
            overflow: hidden;
            background-color: var(--bg-secondary);
        }}
        
        .p5js {{
            padding: var(--space-lg);
            background-color: var(--bg-primary);
            text-align: center;
            min-height: 450px;
            position: relative;
        }}
        
        .p5js-canvas {{
            width: 100%;
            height: auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .p5js-canvas canvas {{
            border-radius: 4px;
            box-shadow: var(--shadow-sm);
            max-width: 100%;
            height: auto;
        }}
        
        .p5js-sketch {{
            display: none;
        }}
        
        /* Error Handling */
        .error-box {{
            background-color: var(--error-bg);
            border: 1px solid var(--error-border);
            border-radius: 6px;
            padding: var(--space-lg);
            margin: var(--space-xl) 0;
        }}
        
        .error-title {{
            font-weight: 600;
            color: var(--error-text);
            margin-bottom: var(--space-sm);
        }}
        
        .error-message {{
            color: var(--error-text);
            font-size: 0.875rem;
            font-family: var(--font-mono);
        }}
        
        /* Table of Contents */
        .toc {{
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-light);
            border-radius: 8px;
            padding: var(--space-lg);
            margin: var(--space-xl) 0;
        }}
        
        .toc ul {{
            list-style: none;
            padding-left: 0;
            margin: 0;
        }}
        
        .toc li {{
            margin-bottom: var(--space-sm);
        }}
        
        .toc a {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .toc a:hover {{
            color: var(--accent-primary);
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .container {{
                padding: var(--space-lg) var(--space-md);
            }}
            
            h1 {{
                font-size: 1.875rem;
            }}
            
            h2 {{
                font-size: 1.5rem;
            }}
            
            table {{
                font-size: 0.8rem;
            }}
            
            th, td {{
                padding: var(--space-sm);
            }}
            
            pre, .code-block {{
                padding: var(--space-md);
                font-size: 0.8rem;
            }}
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            
            .code-toggle {{
                display: none;
            }}
            
            .chart-container,
            .diagram-container {{
                break-inside: avoid;
            }}
        }}
        
        /* Focus Styles */
        details[open] {{
            outline: none;
        }}
        
        summary:focus {{
            outline: 2px solid var(--accent-primary);
            outline-offset: 2px;
        }}
        
        /* Smooth Transitions */
        * {{
            transition: background-color 0.2s ease, border-color 0.2s ease;
        }}
        
        /* MathJax Styling */
        .MathJax {{
            color: var(--text-primary) !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
    
    <script>
        // Initialize Mermaid once and render any present diagrams
        (function ensureMermaidInitialized() {
            try {
                if (!window.__MERMAID_INITED__) {
                    mermaid.initialize({{
                        startOnLoad: false,
                        securityLevel: 'loose',
                        theme: 'base',
                        themeVariables: {{
                            primaryColor: '#f5f4f1',
                            primaryTextColor: '#2c2a26',
                            primaryBorderColor: '#8b5a3c',
                            lineColor: '#8b5a3c',
                            sectionBkgColor: '#faf9f7',
                            altSectionBkgColor: '#f5f4f1',
                            gridColor: '#e8e6e3',
                            textColor: '#2c2a26',
                            taskBkgColor: '#f5f4f1',
                            taskTextColor: '#2c2a26',
                            activeTaskBkgColor: '#8b5a3c',
                            activeTaskBorderColor: '#7a4d33',
                            fontFamily: 'Inter, sans-serif',
                            fontSize: '14px'
                        }}
                    }});
                    window.__MERMAID_INITED__ = true;
                }}
                const targets = document.querySelectorAll('.mermaid');
                if (targets.length) {{
                    if (typeof mermaid.run === 'function') {{
                        mermaid.run({{ querySelector: '.mermaid' }});
                    }} else if (typeof mermaid.init === 'function') {{
                        mermaid.init(undefined, targets);
                    }}
                }}
            }} catch (e) {{
                console.warn('Mermaid init error:', e);
            }}
        }})();
        
        // Initialize syntax highlighting
        hljs.highlightAll();
        
        // Initialize p5.js sketches after DOM and p5.js are fully loaded
        function waitForP5AndInitialize() {
            if (typeof p5 !== 'undefined') {
                initializeP5Sketches();
            } else {
                console.log('Waiting for p5.js to load...');
                setTimeout(waitForP5AndInitialize, 100);
            }
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', waitForP5AndInitialize);
        } else {
            waitForP5AndInitialize();
        }
        
        // Configure MathJax
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']]
            },
            svg: {
                fontCache: 'global'
            }
        };
        
        // Add smooth scrolling for anchor links (avoid double-jump jitter)
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const hash = this.getAttribute('href');
                if (!hash || hash === '#') return;
                const target = document.querySelector(hash);
                if (!target) return;

                // Prevent default hash jump which can cause an extra snap
                e.preventDefault();

                // Use nearest block positioning to reduce layout snapping
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'nearest',
                    inline: 'nearest'
                });
            });
        });

        console.log('📝 Minimal tema yüklendi');
    </script>
</body>
</html>'''

    # Normalize escaped braces used earlier for f-strings, then inject content
    normalized = html_tpl.replace("{{", "{").replace("}}", "}")
    return normalized.replace("{html_content}", html_content)

# Example usage and test
if __name__ == "__main__":
    # Test markdown content
    test_markdown = open("md_in.txt", encoding='utf-8').read()

    html = generate_html(test_markdown)
    with open('html_output.html', 'w', encoding='utf-8') as f:
        f.write(html)
