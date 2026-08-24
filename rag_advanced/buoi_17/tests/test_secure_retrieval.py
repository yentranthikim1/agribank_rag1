from scripts.secure_retrieval import SecureRetrievalAdapter


def test_kiem_toan_vien_can_access_policy_docs():
    adapter = SecureRetrievalAdapter()
    docs, denied_count, status = adapter.retrieve_with_rbac(
        "niêm phong tiền mặt",
        "KiemToanVien",
        top_k=3,
    )

    assert status == "SUCCESS"
    assert docs
    assert denied_count >= 0
    assert any("niêm phong" in doc["text"].lower() for doc in docs)
