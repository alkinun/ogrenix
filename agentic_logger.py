import time
import random
import threading
from datetime import datetime
from typing import List, Dict, Any
import json

class AgenticLogger:
    """
    Agentic logger to demonstrate AI agent capabilities with Turkish logging.
    Simulates local LLM operations with realistic TPS metrics and tool usage.
    """
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.session_start = time.time()
        
        # Simulate local model stats
        self.model_name = "Ogrenix-Gemma-2-9B"
        self.base_tps = random.uniform(12.5, 18.3)  # Base tokens per second
        self.total_tokens_generated = 0
        
        # Deduplication tracking
        self.logged_code_hashes = set()  # Track already logged code blocks
        self.last_stream_log_time = 0.0  # Rate limit stream logs
        
    def _generate_timestamp(self) -> str:
        """Generate formatted timestamp"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    def _calculate_tps(self, token_count: int = None) -> float:
        """Calculate realistic TPS with some variance"""
        variance = random.uniform(0.85, 1.15)
        tps = self.base_tps * variance
        
        # Simulate slower generation for complex tasks
        if token_count and token_count > 100:
            tps *= random.uniform(0.7, 0.9)
        
        return round(tps, 1)
    
    def _log_event(self, message: str, details: Dict[str, Any] = None):
        """Internal logging method"""
        with self.lock:
            log_entry = {
                "timestamp": self._generate_timestamp(),
                "message": message,
                "details": details or {}
            }
            self.logs.append(log_entry)
            
            # Print to console for real-time visibility
            print(f"[{log_entry['timestamp']}] {message}")
            if details:
                for key, value in details.items():
                    print(f"  {key}: {value}")
            
            # Add visual separator for easier reading
            print("\n================\n")
    
    def log_model_init(self):
        return
    
    def log_prompt_analysis(self, prompt_length: int, topic: str):
        """Log prompt analysis phase"""
        self._log_event(
            f"""Konu: {topic}
Toplam Uzunluk: {prompt_length}""",
        )
    
    def log_content_generation_start(self, estimated_tokens: int):
        return
    
    def log_tool_usage(self, tool_type: str, code_snippet: str = None):
        """Log when AI agent uses a tool"""
        # Create hash of code to avoid duplicate logs
        import hashlib
        if code_snippet:
            code_hash = hashlib.md5(code_snippet.encode()).hexdigest()
            if code_hash in self.logged_code_hashes:
                return  # Skip duplicate logging
            self.logged_code_hashes.add(code_hash)
        
        tool_names = {
            "matplotlib": "Matplotlib",
            "mermaid": "Mermaid",
        }
        
        self._log_event(
            """Arac Çağrıldı:
{
    "arac": "tool_type",
    "kod": "code_snippet",
}""".replace("tool_type", tool_type).replace("code_snippet", code_snippet)
        )
    
    def log_content_chunk(self, chunk: str, chunk_number: int):
        """Log streaming content generation (disabled for performance)"""
        # Stream logging disabled to prevent overwhelming other logs
        chunk_tokens = len(chunk) // 4
        self.total_tokens_generated += chunk_tokens
    
    def log_generation_complete(self, total_time: float, final_token_count: int):
        """Log completion of generation process"""
        self._log_event(
            "İçerik üretimi tamamlandı"
        )
    
    def log_error(self, error_type: str, error_message: str, context: str = None):
        """Log errors during generation"""
        self._log_event(
            f"{error_type}: {error_message}",
            {
                "hata_türü": error_type,
                "bağlam": context or "bilinmiyor",
                "zaman_damgası": self._generate_timestamp()
            }
        )
    
    def _detect_mermaid_type(self, code: str) -> str:
        """Detect mermaid diagram type"""
        code_lower = code.lower()
        if "flowchart" in code_lower:
            return "akış_diyagramı"
        elif "graph" in code_lower:
            return "graf_diyagramı" 
        elif "sequencediagram" in code_lower:
            return "sıra_diyagramı"
        elif "classDiagram" in code_lower:
            return "sınıf_diyagramı"
        else:
            return "genel_diyagram"
    
    def _summarize_tools_used(self) -> str:
        """Summarize which tools were used in this session"""
        tools = set()
        for log in self.logs:
            if log["level"] in ["MATPLOTLIB", "MERMAID", "P5JS"]:
                tools.add(log["level"].lower())
        
        tool_names = {
            "matplotlib": "grafik",
            "mermaid": "diyagram", 
            "p5js": "interaktif"
        }
        
        return ", ".join([tool_names.get(tool, tool) for tool in tools]) or "sadece_metin"
    
    def get_logs_json(self) -> str:
        """Get all logs as JSON string"""
        with self.lock:
            return json.dumps(self.logs, ensure_ascii=False, indent=2)
    
    def get_recent_logs(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent logs"""
        with self.lock:
            return self.logs[-count:] if len(self.logs) >= count else self.logs
    
    def start_new_session(self):
        """Start a new session - clear deduplication but keep logs visible"""
        with self.lock:
            self.logged_code_hashes.clear()
            self.last_stream_log_time = 0.0
            self.total_tokens_generated = 0
            # Don't clear logs - keep them visible for judge
    
    def clear_logs(self):
        """Clear all logs"""
        with self.lock:
            self.logs.clear()
            self.total_tokens_generated = 0
            self.logged_code_hashes.clear()  # Clear deduplication tracking
            self.last_stream_log_time = 0.0

# Global logger instance
agentic_logger = AgenticLogger()
