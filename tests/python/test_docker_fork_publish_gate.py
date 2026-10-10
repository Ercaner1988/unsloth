"""Forks must not enter Docker publishing automatically."""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("workflow", ["docker-publish.yml", "docker-publish-rocm.yml"])
@pytest.mark.parametrize("repository", ["unslothai/unsloth", "Ercaner1988/unsloth"])
@pytest.mark.parametrize("event", ["schedule", "push", "workflow_dispatch"])
def test_publish_gate(workflow, repository, event):
    data = yaml.load((ROOT / ".github/workflows" / workflow).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert "workflow_dispatch" in data["on"]
    expression = data["jobs"]["prepare"]["if"].removeprefix("${{").removesuffix("}}")
    expression = expression.replace("github.repository", repr(repository))
    expression = expression.replace("github.event_name", repr(event)).replace("||", "or")
    allowed = eval(expression.strip(), {"__builtins__": {}}, {})
    assert allowed == (repository == "unslothai/unsloth" or event == "workflow_dispatch")


def test_skipped_prepare_cannot_run_registry_cleanup():
    data = yaml.load((ROOT / ".github/workflows/docker-publish.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    cleanup = data["jobs"]["cleanup"]
    assert "prepare" in cleanup["needs"]
    assert "needs.prepare.result == 'success'" in cleanup["if"]
