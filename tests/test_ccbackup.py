"""Tests for ccbackup core backup logic."""

import re

# Import from ccbackup module
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import ccbackup


class TestSanitizeContent:
    """Test sensitive content sanitization."""

    def test_sanitize_api_key(self):
        content = '{"api_key": "sk-ant-abc123-secret"}'
        result = ccbackup.sanitize_content(content)
        assert "sk-ant-abc123-secret" not in result
        assert "<YOUR_API_KEY>" in result

    def test_sanitize_anthropic_token(self):
        content = "token is sk-ant-abcdef123456"
        result = ccbackup.sanitize_content(content)
        assert "sk-ant-abcdef123456" not in result
        assert "<YOUR_ANTHROPIC_TOKEN>" in result

    def test_sanitize_preserves_normal_content(self):
        content = '{"name": "my-project", "version": "1.0"}'
        result = ccbackup.sanitize_content(content)
        assert result == content

    def test_sanitize_multiple_patterns(self):
        content = '{"api_key": "secret123", "token": "tok456"}'
        result = ccbackup.sanitize_content(content)
        assert "secret123" not in result
        assert "tok456" not in result


class TestDetectSensitive:
    """Test sensitive information detection."""

    def test_detect_in_file_with_secrets(self, tmp_path):
        f = tmp_path / "settings.json"
        f.write_text('{"api_key": "real-secret-key"}')
        findings = ccbackup.detect_sensitive_in_file(f)
        assert len(findings) > 0
        assert any(name == "api_key" for name, _ in findings)

    def test_detect_in_clean_file(self, tmp_path):
        f = tmp_path / "clean.json"
        f.write_text('{"name": "test"}')
        findings = ccbackup.detect_sensitive_in_file(f)
        assert len(findings) == 0

    def test_detect_nonexistent_file(self, tmp_path):
        f = tmp_path / "nope.json"
        findings = ccbackup.detect_sensitive_in_file(f)
        assert findings == []

    def test_detect_placeholder_ignored(self, tmp_path):
        f = tmp_path / "settings.json"
        f.write_text('{"api_key": "<YOUR_API_KEY>"}')
        findings = ccbackup.detect_sensitive_in_file(f)
        assert len(findings) == 0


class TestGetMachineInfo:
    """Test machine info retrieval."""

    def test_returns_tuple(self):
        result = ccbackup.get_machine_info()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_hostname_sanitized(self):
        hostname, username = ccbackup.get_machine_info()
        assert re.match(r"^[\w\-]+$", hostname)
        assert re.match(r"^[\w\-]+$", username)


class TestGetDefaultBackupPath:
    """Test backup path generation."""

    def test_path_format(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ccbackup, "BACKUP_DIR", tmp_path / "backups")
        path = ccbackup.get_default_backup_path()
        assert path.suffix == ".zip"
        assert "ccbackup_" in path.name
        assert path.parent.exists()

    def test_path_contains_timestamp(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ccbackup, "BACKUP_DIR", tmp_path / "backups")
        path = ccbackup.get_default_backup_path()
        # Should contain date pattern YYYYMMDD
        assert re.search(r"\d{8}_\d{6}", path.name)


class TestCopyFileWithSanitize:
    """Test file copy with optional sanitization."""

    def test_copy_without_sanitize(self, tmp_path):
        src = tmp_path / "src.json"
        src.write_text('{"api_key": "secret"}')
        dest = tmp_path / "out" / "dest.json"
        ccbackup.copy_file_with_sanitize(src, dest, sanitize=False)
        assert dest.read_text() == '{"api_key": "secret"}'

    def test_copy_with_sanitize(self, tmp_path):
        src = tmp_path / "src.json"
        src.write_text('{"api_key": "secret"}')
        dest = tmp_path / "out" / "dest.json"
        ccbackup.copy_file_with_sanitize(src, dest, sanitize=True)
        content = dest.read_text()
        assert "secret" not in content
        assert "<YOUR_API_KEY>" in content

    def test_copy_binary_not_sanitized(self, tmp_path):
        src = tmp_path / "data.bin"
        src.write_bytes(b"\x00\x01\x02")
        dest = tmp_path / "out" / "data.bin"
        ccbackup.copy_file_with_sanitize(src, dest, sanitize=True)
        assert dest.read_bytes() == b"\x00\x01\x02"


class TestCopyDirectoryWithSanitize:
    """Test directory copy."""

    def test_copy_directory(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.json").write_text('{"key": "val"}')
        (src / "sub").mkdir()
        (src / "sub" / "b.txt").write_text("hello")
        dest = tmp_path / "dest"
        ccbackup.copy_directory_with_sanitize(src, dest)
        assert (dest / "a.json").read_text() == '{"key": "val"}'
        assert (dest / "sub" / "b.txt").read_text() == "hello"

    def test_copy_nonexistent_directory(self, tmp_path):
        src = tmp_path / "nope"
        dest = tmp_path / "dest"
        ccbackup.copy_directory_with_sanitize(src, dest)
        assert not dest.exists()


class TestSensitivePatterns:
    """Test SENSITIVE_PATTERNS coverage."""

    def test_all_patterns_compile(self):
        for pattern, name in ccbackup.SENSITIVE_PATTERNS:
            re.compile(pattern)  # Should not raise
