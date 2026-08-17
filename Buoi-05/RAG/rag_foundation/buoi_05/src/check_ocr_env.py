import importlib
import sys
from typing import List, Tuple


TOOLS: List[Tuple[str, str, str]] = [
    ("Python", "python", "3.11"),
    ("PyMuPDF", "fitz", ""),
    ("Pillow", "PIL", ""),
    ("Llama Cloud", "llama_cloud", ""),
    ("Pydantic", "pydantic", ""),
    ("Streamlit", "streamlit", ""),
    ("python-dotenv", "dotenv", ""),
]


def get_module_version(module_name: str) -> str:
    try:
        module = importlib.import_module(module_name)
        for attr in ("__version__", "version"):
            version = getattr(module, attr, None)
            if version:
                return str(version)
        return "installed"
    except Exception:
        return "n/a"


def check_python() -> Tuple[bool, str, str]:
    version = sys.version.split()[0]
    ok = sys.version_info >= (3, 10)
    note = "Cần Python 3.10+ cho OCR/RAG" if not ok else "Đủ phiên bản yêu cầu"
    return ok, version, note


def check_tool(name: str, module_name: str) -> Tuple[str, str, str]:
    if name == "Python":
        ok, version, note = check_python()
        return ("PASS" if ok else "FAIL", version, note)

    try:
        importlib.import_module(module_name)
        version = get_module_version(module_name)
        return ("PASS", version, "Sẵn sàng sử dụng")
    except Exception:
        return ("FAIL", "n/a", "Thiếu package / chưa cài đặt")


def main() -> int:
    rows: List[Tuple[str, str, str, str]] = []
    for tool_name, module_name, _ in TOOLS:
        status, version, note = check_tool(tool_name, module_name)
        rows.append((tool_name, status, version, note))

    header = ("{:<18} {:<8} {:<18} {:<28}").format(
        "Công cụ", "Trạng thái", "Phiên bản", "Ghi chú"
    )
    separator = "-" * len(header)

    print("=" * len(header))
    print("KIỂM TRA MÔI TRƯỜNG OCR / RAG")
    print("=" * len(header))
    print(header)
    print(separator)

    for tool_name, status, version, note in rows:
        print(("{:<18} {:<8} {:<18} {:<28}").format(tool_name, status, version, note))

    print("=" * len(header))
    failed = any(status == "FAIL" for _, status, _, _ in rows)
    if failed:
        print("Kết luận: Môi trường chưa hoàn toàn sẵn sàng. Hãy cài đặt các gói FAIL trước khi chạy OCR/RAG.")
        print("Gợi ý: pip install PyMuPDF Pillow llama-cloud pydantic streamlit python-dotenv")
    else:
        print("Kết luận: Môi trường OCR/RAG đã sẵn sàng.")

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
