from app.llm.service import get_llm_provider


provider = get_llm_provider()

answer = provider.generate(
    "Answer in exactly one sentence: What does KYC mean?"
)

print("\nMODEL ANSWER:\n")
print(answer)
