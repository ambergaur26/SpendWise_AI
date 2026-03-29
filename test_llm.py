from llm_parser import extract_transaction

# Test message
result = extract_transaction("Spent 1500 on movie tickets")

print("LLM Output JSON:")
print(result)