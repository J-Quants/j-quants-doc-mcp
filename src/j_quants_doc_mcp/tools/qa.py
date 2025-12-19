"""Q&A tool for J-Quants API documentation."""

import json
from pathlib import Path
from typing import Any

FAQ_DATA_PATH = Path(__file__).parent.parent / "data" / "faq.json"


def load_faqs() -> dict[str, Any]:
    """FAQデータをロード"""
    with open(FAQ_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def answer_question(question: str) -> dict[str, Any]:
    """自然言語の質問に対してベストプラクティスや注意事項を回答する。

    Args:
        question: ユーザーからの質問(自然言語)

    Returns:
        回答情報を含む辞書:
        - matched: マッチしたFAQがあるかどうか
        - answers: マッチした回答のリスト(複数マッチする場合がある)
        - suggestion: マッチしない場合の提案メッセージ
    """
    data = load_faqs()
    question_lower = question.lower()

    # キーワードベースのマッチング
    matched_faqs = []

    for faq in data.get("faqs", []):
        # 質問文でのマッチング
        if question_lower in faq.get("question", "").lower():
            matched_faqs.append({"score": 100, "faq": faq})  # 完全一致
            continue

        # キーワードでのマッチング
        keywords = faq.get("keywords", [])
        matched_keywords = [kw for kw in keywords if kw.lower() in question_lower]

        if matched_keywords:
            # マッチしたキーワード数に基づいてスコア計算
            score = len(matched_keywords) * 10
            matched_faqs.append(
                {"score": score, "matched_keywords": matched_keywords, "faq": faq}
            )

    # スコアでソート(高い順)
    matched_faqs.sort(key=lambda x: x["score"], reverse=True)

    # 結果の構築
    if matched_faqs:
        # 上位3件を返す(スコアが高いもの)
        top_matches = matched_faqs[:3]

        answers = []
        for match in top_matches:
            faq = match["faq"]
            answer_item = {
                "category": faq.get("category", ""),
                "question": faq.get("question", ""),
                "answer": faq.get("answer", ""),
                "related_endpoints": faq.get("related_endpoints", []),
            }

            # マッチしたキーワードがある場合は含める
            if "matched_keywords" in match:
                answer_item["matched_keywords"] = match["matched_keywords"]

            answers.append(answer_item)

        return {"matched": True, "count": len(answers), "answers": answers}
    else:
        # マッチしなかった場合
        # すべてのカテゴリを提示
        categories = list({faq.get("category", "") for faq in data.get("faqs", [])})

        return {
            "matched": False,
            "suggestion": "該当するFAQが見つかりませんでした。以下のカテゴリから質問を選んでください、または具体的なキーワードを含めて質問してください。",
            "available_categories": categories,
            "hint": "質問例: '認証方法は?', 'レート制限について', 'トークンの有効期限', 'ページネーションの方法'",
        }
