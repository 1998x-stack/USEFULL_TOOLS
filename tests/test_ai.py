"""Tests for AI/LLM utility tools."""

from devkit.ai.cost_calculator import calculate_cost, compare_costs, supported_models
from devkit.ai.prompt_template import render_template, save_template, load_template, list_templates


def test_calculate_cost_gpt4o():
    cost = calculate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
    assert isinstance(cost, float)
    assert cost > 0


def test_calculate_cost_unknown_model():
    cost = calculate_cost("unknown-model", input_tokens=1000, output_tokens=500)
    assert cost is None


def test_compare_costs():
    result = compare_costs(input_tokens=1000, output_tokens=500)
    assert isinstance(result, dict)
    assert len(result) > 0


def test_supported_models():
    models = supported_models()
    assert "gpt-4o" in models
    assert "claude-sonnet" in models


def test_render_template():
    template = "Hello, {name}! You are {age} years old."
    result = render_template(template, {"name": "Alice", "age": "30"})
    assert result == "Hello, Alice! You are 30 years old."


def test_render_template_jinja2():
    template = "Items: {% for item in items %}{{ item }}, {% endfor %}"
    result = render_template(template, {"items": ["a", "b", "c"]})
    assert "a" in result
    assert "b" in result


def test_save_and_load_template(tmp_path):
    save_template("test_prompt", "Hello {name}", prompts_dir=str(tmp_path))
    loaded = load_template("test_prompt", prompts_dir=str(tmp_path))
    assert loaded == "Hello {name}"


def test_list_templates(tmp_path):
    (tmp_path / "prompt_a.txt").write_text("template a")
    (tmp_path / "prompt_b.txt").write_text("template b")
    templates = list_templates(prompts_dir=str(tmp_path))
    assert "prompt_a" in templates
    assert "prompt_b" in templates
