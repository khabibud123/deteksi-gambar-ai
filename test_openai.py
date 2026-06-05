#!/usr/bin/env python
"""Test OpenAI Integration"""

from openai_integration import openai_analyzer, get_openai_status

print("=" * 60)
print("OPENAI INTEGRATION TEST")
print("=" * 60)

# Get status
status = get_openai_status()

print(f"\n✅ API Key Configured: {status['api_key_configured']}")
print(f"✅ Library: {status['library']}")
print(f"✅ Model: {status['model']}")
print(f"✅ OpenAI Available: {status['available']}")

if status['available']:
    print("\n🎉 OpenAI is READY to use!")
    print("\nTesting with sample detection data...")
    
    sample_data = {
        'status': 'AI Generated',
        'aiConfidence': 85,
        'humanConfidence': 15,
        'fuzzySugenoScore': 0.82,
        'accuracy': 87,
        'entropy': 5.2,
        'noise': 12,
        'edges': 25,
        'blurScore': 5,
        'brightness': 120,
        'contrast': 2.1,
        'saturation': 45,
        'glcmContrast': 0.45,
        'glcmHomogeneity': 0.72,
        'glcmEnergy': 0.35,
        'glcmCorrelation': 0.68,
    }
    
    try:
        insight = openai_analyzer.analyze_detection_result(sample_data)
        print(f"\n✅ Insight retrieved successfully!")
        print(f"\nInsight Preview:\n{str(insight)[:200]}...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
else:
    print("\n❌ OpenAI is NOT available!")
    print("Troubleshooting:")
    print("1. Check OPENAI_API_KEY in .env file")
    print("2. Verify API key is valid at https://platform.openai.com/api-keys")
    print("3. Check internet connection")

print("\n" + "=" * 60)
