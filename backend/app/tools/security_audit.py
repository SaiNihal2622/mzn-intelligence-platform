import os
import re
import sys

def run_audit():
    print("\n🛡️ Starting Zero-Leak Security Audit...")
    
    # Patterns for API keys
    patterns = {
        "OpenRouter": r"sk-or-v1-[a-f0-9]{64}",
        "Gemini": r"AIzaSy[A-Za-z0-9_-]{35}"
    }
    
    flagged_files = []
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    
    # Files/Dirs to ignore
    ignore = {".git", "venv", "__pycache__", ".next", "node_modules", ".env"}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore]
        for file in files:
            if file.endswith((".py", ".js", ".jsx", ".md", ".env.example")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        for name, pattern in patterns.items():
                            if re.search(pattern, content):
                                flagged_files.append((path, name))
                except Exception:
                    continue

    if not flagged_files:
        print("✅ Audit Passed: No hardcoded API keys detected in the codebase.")
        print("🔒 Security State: HARDENED")
    else:
        print(f"🚨 Audit Failed: Found {len(flagged_files)} potential leaks!")
        for path, name in flagged_files:
            print(f"   - [{name}] Found in: {path}")
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
