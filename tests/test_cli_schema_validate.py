import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from envault.cli_schema_validate import cmd_schema_validate


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


def _write_schema(vault_dir, schema):
    (vault_dir / "schema.json").write_text(json.dumps(schema))


def _write_env(tmp_path, content):
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_run_valid_env(runner, vault_dir, tmp_path):
    _write_schema(vault_dir, {"PORT": {"type": "integer", "required": True}})
    env_file = _write_env(tmp_path, "PORT=8080\n")
    result = runner.invoke(cmd_schema_validate, ["run", env_file, "--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_run_missing_required(runner, vault_dir, tmp_path):
    _write_schema(vault_dir, {"DB_URL": {"required": True}})
    env_file = _write_env(tmp_path, "PORT=8080\n")
    result = runner.invoke(cmd_schema_validate, ["run", env_file, "--vault-dir", str(vault_dir)])
    assert result.exit_code == 1
    assert "DB_URL" in result.output
    assert "ERROR" in result.output


def test_run_warning_no_strict(runner, vault_dir, tmp_path):
    _write_schema(vault_dir, {"VER": {"pattern": r"\d+\.\d+\.\d+"}})
    env_file = _write_env(tmp_path, "VER=bad\n")
    result = runner.invoke(cmd_schema_validate, ["run", env_file, "--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert "WARN" in result.output


def test_run_warning_strict_exits_1(runner, vault_dir, tmp_path):
    _write_schema(vault_dir, {"VER": {"pattern": r"\d+\.\d+\.\d+"}})
    env_file = _write_env(tmp_path, "VER=bad\n")
    result = runner.invoke(cmd_schema_validate, ["run", env_file, "--vault-dir", str(vault_dir), "--strict"])
    assert result.exit_code == 1


def test_check_valid(runner, vault_dir):
    _write_schema(vault_dir, {"PORT": {"type": "integer"}})
    result = runner.invoke(cmd_schema_validate, ["check", "PORT", "9000", "--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_check_invalid(runner, vault_dir):
    _write_schema(vault_dir, {"PORT": {"type": "integer"}})
    result = runner.invoke(cmd_schema_validate, ["check", "PORT", "abc", "--vault-dir", str(vault_dir)])
    assert result.exit_code == 1
    assert "PORT" in result.output


def test_no_schema_all_valid(runner, vault_dir, tmp_path):
    env_file = _write_env(tmp_path, "FOO=bar\nBAZ=qux\n")
    result = runner.invoke(cmd_schema_validate, ["run", env_file, "--vault-dir", str(vault_dir)])
    assert result.exit_code == 0
