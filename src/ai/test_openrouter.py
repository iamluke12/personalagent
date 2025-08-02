#!/usr/bin/env python3
"""
Test OpenRouter API connectivity and available models
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def test_openrouter():
    """Test OpenRouter API connectivity"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ No OPENROUTER_API_KEY found in .env")
        return
    
    print(f"🔑 API Key: {api_key[:20]}...")
    
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )
    
    # Test with a very simple, commonly available free model
    test_models = [
        "microsoft/phi-3-mini-128k-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemma-2-9b-it:free",
        "qwen/qwen-2-7b-instruct:free"
    ]
    
    for model in test_models:
        print(f"\n🧪 Testing model: {model}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user", 
                    "content": "Hello! Just respond with 'OK' to test the connection."
                }],
                max_tokens=10,
                temperature=0.1,
                extra_headers={
                    "HTTP-Referer": "https://github.com/personalAgent",
                    "X-Title": "Personal Agent Test"
                }
            )
            
            result = response.choices[0].message.content
            print(f"✅ {model} works! Response: {result}")
            
            # Update .env with working model
            print(f"💡 You can use this model: {model}")
            break
            
        except Exception as e:
            print(f"❌ {model} failed: {e}")
    
    print("\n🔍 For more available models, visit: https://openrouter.ai/models")

if __name__ == "__main__":
    test_openrouter()
