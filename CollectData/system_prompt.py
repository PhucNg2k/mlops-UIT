SYSTEM_PROMPT = """
Bạn là một chuyên gia giáo dục và lịch sử, có nhiệm vụ tạo ra bộ dữ liệu câu hỏi-trả lời chất lượng cao dựa trên các văn bản lịch sử.
"""

USER_PROMPT = """
Hãy phân tích văn bản dưới đây và tạo {NUM_PAIRS} cặp câu hỏi-trả lời để sử dụng cho việc fine-tune mô hình hỏi đáp.
Với mỗi cặp câu hỏi-trả lời:

+ Câu hỏi phải đa dạng về loại (who, what, when, where, why, how) và độ khó (từ đơn giản đến phức tạp yêu cầu suy luận).
+ Câu trả lời phải chính xác, dựa hoàn toàn vào thông tin trong văn bản gốc.
+ Câu trả lời phải đầy đủ, rõ ràng và chính xác về mặt học thuật.
+ Cả câu hỏi và câu trả lời phải được viết bằng tiếng Việt tự nhiên, phù hợp với văn phong giáo dục.

Văn bản nguồn:

{INPUT_CONTENT}

Xuất kết quả theo định dạng JSON sau:

[
  {{
    "question": "Câu hỏi 1?",
    "answer": "Câu trả lời 1."
  }},
  {{
    "question": "Câu hỏi 2?",
    "answer": "Câu trả lời 2."
  }},
  ...
]
"""