#!/usr/bin/env python3
"""Detailed Vietnamese text analysis."""
import json
import unicodedata
from pathlib import Path

output_dir = Path("storage") / "output"
result_file = output_dir / "TT_02_2023_NHNN_result.json"

with open(result_file, "r", encoding="utf-8") as f:
    data = json.load(f)

print("=" * 80)
print("PHÂN TÍCH CHI TIẾT CÁC CHUNK")
print("=" * 80)

# Get first chunk from each strategy
for strategy in ["fixed_size", "semantic", "hierarchical"]:
    chunks = [c for c in data['chunks'] if c['strategy'] == strategy]
    if not chunks:
        continue
    
    chunk = chunks[0]
    text = chunk['text']
    
    print(f"\n{'='*80}")
    print(f"Chiến lược: {strategy.upper()}")
    print(f"{'='*80}")
    print(f"Độ dài: {len(text)} ký tự")
    
    # Check normalization forms
    nfc = unicodedata.normalize('NFC', text)
    nfd = unicodedata.normalize('NFD', text)
    nfkc = unicodedata.normalize('NFKC', text)
    
    print(f"\nSo sánh dạng chuẩn:")
    print(f"  NFC hiện tại == NFC định tính: {nfc == text}")
    print(f"  NFC == NFD: {nfc == nfd}")
    print(f"  NFC == NFKC: {nfc == nfkc}")
    
    # Check for combining marks
    combining_marks = [c for c in text if unicodedata.combining(c) > 0]
    print(f"  Tổng combining marks: {len(combining_marks)}")
    
    # Show first 200 chars
    print(f"\nNội dung (200 ký tự đầu):")
    preview = text[:200]
    print(f"  Text: {preview}")
    
    # Show Unicode codepoints for first 50 chars
    print(f"\nUnicode codepoints (30 ký tự đầu):")
    codepoints = ' '.join(f"U+{ord(c):04X}" for c in text[:30])
    print(f"  {codepoints}")
    
    # Check character categories
    categories = {}
    for c in text:
        cat = unicodedata.category(c)
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nKategories ký tự:")
    for cat, count in sorted(categories.items()):
        cat_name = {
            'Lu': 'Uppercase Letter',
            'Ll': 'Lowercase Letter',
            'Lm': 'Modifier Letter',
            'Lo': 'Other Letter',
            'Zs': 'Space Separator',
            'Po': 'Other Punctuation',
            'Pd': 'Dash Punctuation',
            'Pc': 'Connector Punctuation',
            'No': 'Other Number',
            'Nd': 'Decimal Number',
            'Cc': 'Control',
            'Cs': 'Surrogate',
        }.get(cat, cat)
        print(f"  {cat} ({cat_name}): {count}")

print("\n" + "=" * 80)
