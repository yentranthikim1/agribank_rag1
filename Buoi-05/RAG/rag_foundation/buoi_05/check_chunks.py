#!/usr/bin/env python3
"""Check chunk quality and Vietnamese text normalization."""
import json
import sys
from pathlib import Path

output_dir = Path("storage") / "output"
result_file = output_dir / "TT_02_2023_NHNN_result.json"

if not result_file.exists():
    print(f"File not found: {result_file}")
    sys.exit(1)

with open(result_file, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 80)
print("KIỂM TRA CHẤT LƯỢNG CHUNK & CHUẨN HÓA TIẾNG VIỆT")
print("=" * 80)
print(f"File: {data['source']}")
print(f"Tổng cảnh báo: {len(data.get('warnings', []))}")
print()

# Check first 3 chunks from each strategy
for strategy in ["fixed_size", "semantic", "hierarchical"]:
    print(f"\n>>> Chiến lược: {strategy.upper()}")
    print(f"Số chunk: {data['strategies'][strategy]['count']}")
    
    chunks = [c for c in data['chunks'] if c['strategy'] == strategy][:2]
    for i, chunk in enumerate(chunks, 1):
        text = chunk['text']
        # Check for encoding issues
        has_unicode_replacement = "\\ufffd" in repr(text) or "\\uffef" in repr(text)
        is_normalized = all(ord(c) < 127 or ord(c) >= 0x100 for c in text)
        
        print(f"\n  Chunk {i}:")
        print(f"    Độ dài: {len(text)} ký tự")
        print(f"    Chuẩn hóa Unicode: {'✓ OK' if is_normalized else '✗ LỖI'}")
        print(f"    Encoding sạch: {'✓ OK' if not has_unicode_replacement else '✗ LỖI'}")
        print(f"    Nội dung (100 ký tự đầu):")
        print(f"    {text[:100]}...")

print("\n" + "=" * 80)
print("✅ Kiểm tra hoàn tất!")
print("=" * 80)
