"""LLM API cost estimator."""

from typing import Dict, List, Optional

PRICING = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "claude-opus": (15.00, 75.00),
    "claude-sonnet": (3.00, 15.00),
    "claude-haiku": (0.25, 1.25),
    "gemini-pro": (1.25, 5.00),
    "gemini-flash": (0.075, 0.30),
}


def supported_models() -> List[str]:
    return list(PRICING.keys())


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    if model not in PRICING:
        return None
    input_price, output_price = PRICING[model]
    cost = (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price
    return round(cost, 6)


def compare_costs(input_tokens: int, output_tokens: int) -> Dict[str, float]:
    costs = {}
    for model in PRICING:
        cost = calculate_cost(model, input_tokens, output_tokens)
        if cost is not None:
            costs[model] = cost
    return dict(sorted(costs.items(), key=lambda x: x[1]))
