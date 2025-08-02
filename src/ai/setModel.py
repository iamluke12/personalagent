#!/usr/bin/env python3
"""
Model Management Tool for personalAgent
Allows listing available models and setting the active model via command line
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.secure_credentials import SecureCredentialManager

# Load environment variables
load_dotenv()

class ModelManager:
    def __init__(self):
        self.config_file = os.path.expanduser("~/personalAgent/.env")
        self.available_providers = ['openai', 'openrouter', 'gemini', 'anthropic']
        self.credential_manager = SecureCredentialManager()
    
    def _get_api_key(self, key_name: str) -> str:
        """Get API key from secure storage or environment"""
        # Try secure storage first
        api_key = self.credential_manager.get_credential(key_name)
        if api_key:
            return api_key
        
        # Fallback to environment variable
        api_key = os.getenv(key_name)
        if api_key and api_key != f'your_{key_name.split("_")[0].lower()}_key_here':
            return api_key
        
        return None
    
    def get_openai_models(self):
        """Get available OpenAI models"""
        api_key = self._get_api_key('OPENAI_API_KEY')
        if not api_key:
            return []
        
        try:
            client = OpenAI(api_key=api_key)
            models = client.models.list()
            openai_models = []
            
            # Filter for chat completion models
            for model in models.data:
                if any(prefix in model.id for prefix in ['gpt-', 'chatgpt']):
                    openai_models.append({
                        'id': model.id,
                        'provider': 'openai',
                        'name': model.id,
                        'owned_by': model.owned_by
                    })
            
            return sorted(openai_models, key=lambda x: x['id'])
        except Exception as e:
            print(f"⚠️ Error fetching OpenAI models: {e}")
            return []
    
    def get_openrouter_models(self):
        """Get available OpenRouter models"""
        api_key = self._get_api_key('OPENROUTER_API_KEY')
        if not api_key:
            return []
        
        try:
            # OpenRouter models API endpoint
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://github.com/personalAgent",
                    "X-Title": "Personal Agent Model List"
                }
            )
            response.raise_for_status()
            
            models_data = response.json()
            openrouter_models = []
            
            for model in models_data.get('data', []):
                openrouter_models.append({
                    'id': model['id'],
                    'provider': 'openrouter',
                    'name': model['id'],
                    'pricing': model.get('pricing', {}),
                    'context_length': model.get('context_length', 'Unknown'),
                    'free': ':free' in model['id'] or model.get('pricing', {}).get('prompt', '0') == '0'
                })
            
            return sorted(openrouter_models, key=lambda x: (not x['free'], x['id']))
        except Exception as e:
            print(f"⚠️ Error fetching OpenRouter models: {e}")
            return []
    
    def get_gemini_models(self):
        """Get available Gemini models"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_key_here':
            return []
        
        # Common Gemini models (since there's no direct API to list them)
        gemini_models = [
            {
                'id': 'gemini-1.5-flash',
                'provider': 'gemini',
                'name': 'Gemini 1.5 Flash',
                'description': 'Fast and efficient model for most tasks'
            },
            {
                'id': 'gemini-1.5-pro',
                'provider': 'gemini',
                'name': 'Gemini 1.5 Pro',
                'description': 'Most capable model for complex reasoning'
            },
            {
                'id': 'gemini-pro',
                'provider': 'gemini',
                'name': 'Gemini Pro',
                'description': 'Optimized for complex reasoning tasks'
            }
        ]
        
        return gemini_models
    
    def get_anthropic_models(self):
        """Get available Anthropic models"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_anthropic_key_here':
            return []
        
        # Common Claude models (since there's no direct API to list them)
        anthropic_models = [
            {
                'id': 'claude-3-5-sonnet-20241022',
                'provider': 'anthropic',
                'name': 'Claude 3.5 Sonnet',
                'description': 'Most intelligent Claude model'
            },
            {
                'id': 'claude-3-haiku-20240307',
                'provider': 'anthropic',
                'name': 'Claude 3 Haiku',
                'description': 'Fastest and most compact model'
            },
            {
                'id': 'claude-3-opus-20240229',
                'provider': 'anthropic',
                'name': 'Claude 3 Opus',
                'description': 'Most powerful model for complex tasks'
            }
        ]
        
        return anthropic_models
    
    def list_all_models(self, provider_filter=None):
        """List all available models"""
        all_models = []
        
        if not provider_filter or provider_filter == 'openai':
            all_models.extend(self.get_openai_models())
        
        if not provider_filter or provider_filter == 'openrouter':
            all_models.extend(self.get_openrouter_models())
        
        if not provider_filter or provider_filter == 'gemini':
            all_models.extend(self.get_gemini_models())
        
        if not provider_filter or provider_filter == 'anthropic':
            all_models.extend(self.get_anthropic_models())
        
        return all_models
    
    def update_env_file(self, provider, model):
        """Update the .env file with new provider and model"""
        try:
            # Read current .env file
            with open(self.config_file, 'r') as f:
                lines = f.readlines()
            
            # Update the lines
            new_lines = []
            for line in lines:
                if line.startswith('LLM_PROVIDER='):
                    new_lines.append(f'LLM_PROVIDER={provider}\n')
                elif line.startswith('LLM_MODEL='):
                    new_lines.append(f'LLM_MODEL={model}\n')
                else:
                    new_lines.append(line)
            
            # Write back to file
            with open(self.config_file, 'w') as f:
                f.writelines(new_lines)
            
            print(f"✅ Updated LLM configuration:")
            print(f"   Provider: {provider}")
            print(f"   Model: {model}")
            
        except Exception as e:
            print(f"❌ Error updating .env file: {e}")
    
    def get_current_config(self):
        """Get current LLM configuration"""
        provider = os.getenv('LLM_PROVIDER', 'openai')
        model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
        return provider, model

def main():
    """Main CLI interface"""
    manager = ModelManager()
    
    if len(sys.argv) < 2:
        print("🤖 Personal Agent Model Manager")
        print("=" * 40)
        
        # Show current configuration
        provider, model = manager.get_current_config()
        print(f"Current: {provider} / {model}")
        print()
        
        print("Usage:")
        print("  python setModel.py list [provider]  - List available models")
        print("  python setModel.py set <provider> <model>  - Set active model")
        print("  python setModel.py current  - Show current configuration")
        print()
        print("Providers: openai, openrouter, gemini, anthropic")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'current':
        provider, model = manager.get_current_config()
        print(f"🎯 Current LLM Configuration:")
        print(f"   Provider: {provider}")
        print(f"   Model: {model}")
    
    elif command == 'list':
        provider_filter = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"🤖 Available Models{f' ({provider_filter})' if provider_filter else ''}:")
        print("=" * 60)
        
        models = manager.list_all_models(provider_filter)
        
        if not models:
            print("❌ No models available. Check your API keys.")
            return
        
        for model in models:
            provider_icon = {
                'openai': '🟢',
                'openrouter': '🔄',
                'gemini': '💎',
                'anthropic': '🧠'
            }.get(model['provider'], '❓')
            
            print(f"{provider_icon} {model['provider'].upper()}: {model['id']}")
            
            if 'description' in model:
                print(f"   📝 {model['description']}")
            
            if 'free' in model and model['free']:
                print(f"   💰 FREE")
            
            if 'context_length' in model and model['context_length'] != 'Unknown':
                print(f"   📏 Context: {model['context_length']}")
            
            print()
    
    elif command == 'set':
        if len(sys.argv) < 4:
            print("❌ Usage: python setModel.py set <provider> <model>")
            return
        
        provider = sys.argv[2].lower()
        model = sys.argv[3]
        
        if provider not in manager.available_providers:
            print(f"❌ Invalid provider. Available: {', '.join(manager.available_providers)}")
            return
        
        # Validate the model exists
        models = manager.list_all_models(provider)
        model_ids = [m['id'] for m in models]
        
        if model not in model_ids:
            print(f"❌ Model '{model}' not found for provider '{provider}'")
            print(f"Available models for {provider}:")
            for model_id in model_ids[:5]:  # Show first 5
                print(f"  - {model_id}")
            if len(model_ids) > 5:
                print(f"  ... and {len(model_ids) - 5} more")
            return
        
        manager.update_env_file(provider, model)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: list, set, current")

if __name__ == "__main__":
    main()
