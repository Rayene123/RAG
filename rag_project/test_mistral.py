"""
Quick test script for Mistral AI API
"""
import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

# Load environment variables from .env file
load_dotenv()

# Check if API key is set
mistral_api_key = os.getenv("MISTRAL_API_KEY")

if not mistral_api_key:
    print("❌ MISTRAL_API_KEY not found!")
    print("\n📝 Steps to get started:")
    print("1. Go to: https://console.mistral.ai/")
    print("2. Sign up (free trial with €5 credits)")
    print("3. Get your API key")
    print("4. Set it in PowerShell:")
    print('   $env:MISTRAL_API_KEY="your-key-here"')
    exit(1)

print("✅ MISTRAL_API_KEY found!")
print("\n🧪 Testing Mistral AI API...\n")

# Test the connection
try:
    llm = ChatMistralAI(
        model="mistral-small-latest",
        temperature=0.7,
        mistral_api_key=mistral_api_key
    )
    
    # Simple test prompt
    response = llm.invoke("Say 'Mistral AI is working!' if you can read this.")
    
    print("✅ SUCCESS! Mistral AI is working!")
    print(f"\n📨 Response: {response.content}")
    
    print("\n🎉 Available models:")
    print("  - mistral-small-latest (Fast, cost-effective, recommended)")
    print("  - mistral-medium-latest (Balanced performance)")
    print("  - mistral-large-latest (Best quality, more expensive)")
    print("  - open-mistral-7b (Open source, fast)")
    print("  - codestral-latest (Code-specialized)")
    
    print("\n✅ You're ready to use the agents!")
    print("   Run: python agents/historian_agent.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n💡 Check:")
    print("  1. Your API key is correct")
    print("  2. You have credits remaining")
    print("  3. You have internet connection")
    print("  4. langchain-mistralai is installed: pip install langchain-mistralai")
