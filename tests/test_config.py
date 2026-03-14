"""
tests/test_config.py
---------------------
Unit tests for Config validation and default value behaviour.
"""

import pytest
from research_agent.config import Config


class TestConfig:

    def test_raises_if_api_key_missing(self):
        """Config.validate() must raise if openai_api_key is empty."""
        cfg = Config(openai_api_key="")
        with pytest.raises(ValueError, match="API key"):
            cfg.validate()

    def test_no_error_with_valid_key(self):
        """Config.validate() should pass silently when key is present."""
        cfg = Config(openai_api_key="sk-test")
        cfg.validate()  # should not raise

    def test_raises_if_max_papers_too_small(self):
        cfg = Config(openai_api_key="sk-test", max_papers=0)
        with pytest.raises(ValueError, match="max_papers"):
            cfg.validate()

    def test_raises_if_max_papers_too_large(self):
        cfg = Config(openai_api_key="sk-test", max_papers=100)
        with pytest.raises(ValueError, match="max_papers"):
            cfg.validate()

    def test_default_models(self):
        """Check default model names haven't been accidentally changed."""
        cfg = Config(openai_api_key="sk-test")
        assert cfg.summarization_model == "gpt-4o-mini"
        assert cfg.synthesis_model == "gpt-4o"
        assert cfg.embedding_model == "text-embedding-3-small"

    def test_output_dir_is_path(self):
        """output_dir should always be a Path object after __post_init__."""
        from pathlib import Path
        cfg = Config(openai_api_key="sk-test", output_dir="my_outputs")
        assert isinstance(cfg.output_dir, Path)
