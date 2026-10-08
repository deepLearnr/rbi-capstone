from app.rag.simplification import simplify_regulation


request = (
    "Summarize the September 18, 2026 Commercial Banks KYC amendment. "
    "Explain what changed for FPIs, why it matters, who is affected, "
    "what bank employees should know, and the effective date."
)

result = simplify_regulation(request)

print(result.model_dump_json(indent=2))
