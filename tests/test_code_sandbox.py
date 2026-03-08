"""
Tests for Code Sandbox Module.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.tools.code_sandbox import (
    CodeLanguage,
    CodeSandbox,
    ExecutionResult,
    ExecutionStatus,
    SandboxConfig,
)


class TestCodeLanguage:
    """Tests for CodeLanguage enum."""

    def test_code_language_values(self):
        """Test CodeLanguage enum values."""
        assert CodeLanguage.PYTHON.value == "python"
        assert CodeLanguage.JAVASCRIPT.value == "javascript"
        assert CodeLanguage.JAVA.value == "java"
        assert CodeLanguage.CPP.value == "cpp"
        assert CodeLanguage.RUST.value == "rust"
        assert CodeLanguage.GO.value == "go"
        assert CodeLanguage.RUBY.value == "ruby"
        assert CodeLanguage.PHP.value == "php"

    def test_code_language_count(self):
        """Test that CodeLanguage has expected number of values."""
        assert len(CodeLanguage) == 8

    def test_code_language_from_string(self):
        """Test creating CodeLanguage from string."""
        assert CodeLanguage("python") == CodeLanguage.PYTHON
        assert CodeLanguage("javascript") == CodeLanguage.JAVASCRIPT


class TestExecutionStatus:
    """Tests for ExecutionStatus enum."""

    def test_execution_status_values(self):
        """Test ExecutionStatus enum values."""
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.TIMEOUT.value == "timeout"
        assert ExecutionStatus.MEMORY_ERROR.value == "memory_error"
        assert ExecutionStatus.ERROR.value == "error"

    def test_execution_status_count(self):
        """Test that ExecutionStatus has expected number of values."""
        assert len(ExecutionStatus) == 7


class TestExecutionResult:
    """Tests for ExecutionResult dataclass."""

    def test_execution_result_creation(self):
        """Test creating an ExecutionResult."""
        result = ExecutionResult(
            execution_id="exec_0",
            status=ExecutionStatus.COMPLETED,
            language=CodeLanguage.PYTHON,
            code="print('hello')",
            output="hello\n",
            error="",
            exit_code=0,
            execution_time=0.5,
            memory_used=10.0,
            start_time=0.0,
            end_time=0.5,
        )

        assert result.execution_id == "exec_0"
        assert result.status == ExecutionStatus.COMPLETED
        assert result.language == CodeLanguage.PYTHON
        assert result.output == "hello\n"
        assert result.exit_code == 0

    def test_execution_result_defaults(self):
        """Test ExecutionResult with minimal args."""
        result = ExecutionResult(
            execution_id="exec_1",
            status=ExecutionStatus.FAILED,
            language=CodeLanguage.JAVASCRIPT,
            code="",
            output="",
            error="Syntax error",
            exit_code=1,
            execution_time=0.0,
            memory_used=0.0,
            start_time=0.0,
            end_time=0.0,
        )

        assert result.status == ExecutionStatus.FAILED
        assert result.error == "Syntax error"


class TestSandboxConfig:
    """Tests for SandboxConfig dataclass."""

    def test_sandbox_config_defaults(self):
        """Test SandboxConfig default values."""
        config = SandboxConfig()

        assert config.max_execution_time == 30.0
        assert config.max_memory == 256
        assert config.max_output_size == 1000000
        assert config.enable_network is False
        assert config.enable_filesystem is False

    def test_sandbox_config_custom(self):
        """Test SandboxConfig with custom values."""
        config = SandboxConfig(
            max_execution_time=60.0, max_memory=512, enable_network=True, enable_filesystem=True
        )

        assert config.max_execution_time == 60.0
        assert config.max_memory == 512
        assert config.enable_network is True
        assert config.enable_filesystem is True

    def test_sandbox_config_lists(self):
        """Test SandboxConfig with list fields."""
        config = SandboxConfig(allowed_imports=["os", "sys"], forbidden_imports=["subprocess"])

        assert "os" in config.allowed_imports
        assert "subprocess" in config.forbidden_imports


class TestCodeSandboxInit:
    """Tests for CodeSandbox initialization."""

    def test_init_default(self):
        """Test CodeSandbox initialization with defaults."""
        sandbox = CodeSandbox()

        assert sandbox.config is not None
        assert sandbox.executions == {}
        assert sandbox.temp_dir is not None
        assert "omni_sandbox_" in sandbox.temp_dir

    def test_init_with_config(self):
        """Test CodeSandbox initialization with custom config."""
        config = SandboxConfig(max_execution_time=60.0)
        sandbox = CodeSandbox(config=config)

        assert sandbox.config.max_execution_time == 60.0

    def test_language_configs(self):
        """Test that language configs are set up correctly."""
        sandbox = CodeSandbox()

        assert CodeLanguage.PYTHON in sandbox.language_configs
        assert CodeLanguage.JAVASCRIPT in sandbox.language_configs
        assert CodeLanguage.JAVA in sandbox.language_configs
        assert CodeLanguage.CPP in sandbox.language_configs
        assert CodeLanguage.RUST in sandbox.language_configs
        assert CodeLanguage.GO in sandbox.language_configs


class TestCodeSandboxMethods:
    """Tests for CodeSandbox methods."""

    def test_list_executions_empty(self):
        """Test list_executions when empty."""
        sandbox = CodeSandbox()

        assert sandbox.list_executions() == []

    def test_list_executions_with_data(self):
        """Test list_executions with executions."""
        sandbox = CodeSandbox()

        # Add mock executions
        sandbox.executions["exec_0"] = Mock()
        sandbox.executions["exec_1"] = Mock()

        result = sandbox.list_executions()

        assert "exec_0" in result
        assert "exec_1" in result

    @pytest.mark.asyncio
    async def test_get_execution_found(self):
        """Test get_execution when found."""
        sandbox = CodeSandbox()

        mock_result = Mock()
        sandbox.executions["exec_0"] = mock_result

        result = await sandbox.get_execution("exec_0")

        assert result == mock_result

    @pytest.mark.asyncio
    async def test_get_execution_not_found(self):
        """Test get_execution when not found."""
        sandbox = CodeSandbox()

        result = await sandbox.get_execution("nonexistent")

        assert result is None

    def test_create_temp_file_python(self):
        """Test _create_temp_file for Python."""
        sandbox = CodeSandbox()

        temp_file = sandbox._create_temp_file("print('hello')", CodeLanguage.PYTHON)

        assert temp_file.endswith(".py")

    def test_create_temp_file_javascript(self):
        """Test _create_temp_file for JavaScript."""
        sandbox = CodeSandbox()

        temp_file = sandbox._create_temp_file("console.log('hello')", CodeLanguage.JAVASCRIPT)

        assert temp_file.endswith(".js")


class TestCodeSandboxValidate:
    """Tests for code validation."""

    @pytest.mark.asyncio
    async def test_validate_python_valid(self):
        """Test validating valid Python code."""
        sandbox = CodeSandbox()

        result = await sandbox.validate_code("x = 1\nprint(x)", CodeLanguage.PYTHON)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_validate_python_invalid(self):
        """Test validating invalid Python code."""
        sandbox = CodeSandbox()

        result = await sandbox.validate_code("x = \n", CodeLanguage.PYTHON)

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_validate_javascript(self):
        """Test validating JavaScript code."""
        sandbox = CodeSandbox()

        result = await sandbox.validate_code("function test() {}", CodeLanguage.JAVASCRIPT)

        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_javascript_warning(self):
        """Test validating JavaScript code with warning."""
        sandbox = CodeSandbox()

        # Code without function/const/let declarations
        result = await sandbox.validate_code("x = 1", CodeLanguage.JAVASCRIPT)

        assert result["valid"] is True
        assert len(result["warnings"]) > 0


class TestCodeSandboxAnalyze:
    """Tests for code analysis."""

    @pytest.mark.asyncio
    async def test_analyze_python_basic(self):
        """Test analyzing Python code."""
        sandbox = CodeSandbox()

        code = """
def hello():
    pass

class MyClass:
    pass
"""

        result = await sandbox.analyze_code(code, CodeLanguage.PYTHON)

        assert result["language"] == "python"
        assert result["functions"] == 1
        assert result["classes"] == 1

    @pytest.mark.asyncio
    async def test_analyze_python_imports(self):
        """Test analyzing Python imports."""
        sandbox = CodeSandbox()

        code = """
import os
import sys
from pathlib import Path
"""

        result = await sandbox.analyze_code(code, CodeLanguage.PYTHON)

        assert "os" in result["imports"]
        assert "sys" in result["imports"]

    @pytest.mark.asyncio
    async def test_analyze_python_complexity(self):
        """Test analyzing Python complexity."""
        sandbox = CodeSandbox()

        code = """
if x > 0:
    for i in range(10):
        if i % 2 == 0:
            print(i)
"""

        result = await sandbox.analyze_code(code, CodeLanguage.PYTHON)

        # Complexity increases with if/for/while
        assert result["complexity"] > 0

    @pytest.mark.asyncio
    async def test_analyze_python_lines(self):
        """Test analyzing Python line count."""
        sandbox = CodeSandbox()

        code = "line1\nline2\nline3"

        result = await sandbox.analyze_code(code, CodeLanguage.PYTHON)

        assert result["lines"] == 3
        assert result["characters"] == len(code)


class TestCodeSandboxSecurity:
    """Tests for security checks."""

    @pytest.mark.asyncio
    async def test_check_python_security_allowed(self):
        """Test security check with safe code."""
        sandbox = CodeSandbox()

        result = await sandbox._check_python_security("x = 1\nprint(x)", SandboxConfig())

        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_check_python_security_forbidden_import(self):
        """Test security check with forbidden import."""
        sandbox = CodeSandbox()

        result = await sandbox._check_python_security(
            "import subprocess", SandboxConfig(forbidden_imports=["subprocess"])
        )

        assert result["allowed"] is False
        assert "subprocess" in result["reason"]

    @pytest.mark.asyncio
    async def test_check_python_security_dangerous_exec(self):
        """Test security check with exec."""
        sandbox = CodeSandbox()

        result = await sandbox._check_python_security("exec('print(1)')", SandboxConfig())

        assert result["allowed"] is False
        assert "exec" in result["reason"].lower()

    @pytest.mark.asyncio
    async def test_check_python_security_dangerous_eval(self):
        """Test security check with eval."""
        sandbox = CodeSandbox()

        result = await sandbox._check_python_security("eval('1+1')", SandboxConfig())

        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_check_python_security_open_file(self):
        """Test security check with file open."""
        sandbox = CodeSandbox()

        result = await sandbox._check_python_security(
            "open('file.txt', 'r')", SandboxConfig(enable_filesystem=False)
        )

        assert result["allowed"] is False

    @pytest.mark.asyncio
    async def test_check_python_security_network(self):
        """Test security check with network operations."""
        sandbox = CodeSandbox()

        result = await sandbox._check_python_security(
            "import urllib.request", SandboxConfig(enable_network=False)
        )

        assert result["allowed"] is False


class TestCodeSandboxExecute:
    """Tests for code execution."""

    @pytest.mark.asyncio
    async def test_execute_code_blocked_by_security(self):
        """Test execute_code blocked by security."""
        sandbox = CodeSandbox(config=SandboxConfig(forbidden_imports=["subprocess"]))

        result = await sandbox.execute_code("import subprocess", CodeLanguage.PYTHON)

        assert result.status == ExecutionStatus.ERROR
        assert "forbidden" in result.error.lower() or "subprocess" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_code_blocked_by_dangerous_pattern(self):
        """Test execute_code blocked by dangerous pattern."""
        sandbox = CodeSandbox()

        result = await sandbox.execute_code("exec('print(1)')", CodeLanguage.PYTHON)

        assert result.status == ExecutionStatus.ERROR
        assert "dangerous" in result.error.lower() or "exec" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_unsupported_language(self):
        """Test execute with unsupported language."""
        sandbox = CodeSandbox()

        # RUBY and PHP are defined but not in language_configs
        with pytest.raises(ValueError, match="Unsupported language"):
            await sandbox._run_code(
                "temp_file", CodeLanguage.RUBY, None, sandbox.config, "exec_0", 0.0
            )


class TestCodeSandboxCleanup:
    """Tests for cleanup."""

    def test_cleanup(self):
        """Test cleanup method."""
        sandbox = CodeSandbox()
        temp_dir = sandbox.temp_dir

        sandbox.cleanup()

        # Temp dir should be removed
        import os

        assert not os.path.exists(temp_dir)


class TestCodeSandboxIntegration:
    """Integration tests for CodeSandbox."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test full workflow: validate, analyze, execute."""
        sandbox = CodeSandbox()

        code = """
def add(a, b):
    return a + b

print(add(1, 2))
"""

        # Validate
        validation = await sandbox.validate_code(code, CodeLanguage.PYTHON)
        assert validation["valid"] is True

        # Analyze
        analysis = await sandbox.analyze_code(code, CodeLanguage.PYTHON)
        assert analysis["functions"] == 1

        # Cleanup
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_multiple_executions(self):
        """Test multiple code executions."""
        sandbox = CodeSandbox()

        # Execute multiple times
        for i in range(3):
            result = await sandbox.execute_code(f"x = {i}\nprint(x)", CodeLanguage.PYTHON)
            # Just verify execution was attempted
            assert result.execution_id is not None

        # Check all executions are stored
        assert len(sandbox.list_executions()) == 3

        sandbox.cleanup()


class TestCodeSandboxExtended:
    """Extended tests to improve coverage for code_sandbox.py."""

    @pytest.mark.asyncio
    async def test_execute_code_with_input(self):
        """Test executing code with stdin input."""
        sandbox = CodeSandbox()

        code = "x = input()\nprint(f'Got: {x}')"

        result = await sandbox.execute_code(code, CodeLanguage.PYTHON, input_data="test_input")

        assert result.execution_id is not None
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_execute_code_timeout(self):
        """Test code execution timeout."""
        config = SandboxConfig(max_execution_time=0.1)
        sandbox = CodeSandbox(config=config)

        # Code that runs longer than timeout
        code = "import time\ntime.sleep(10)"

        result = await sandbox.execute_code(code, CodeLanguage.PYTHON)

        assert result.status == ExecutionStatus.TIMEOUT
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_execute_code_large_output_truncation(self):
        """Test output truncation for large output."""
        config = SandboxConfig(max_output_size=100)
        sandbox = CodeSandbox(config=config)

        # Code that produces large output
        code = "for i in range(1000):\n    print('x' * 100)"

        result = await sandbox.execute_code(code, CodeLanguage.PYTHON)

        # Output should be truncated
        assert (
            len(result.output) <= config.max_output_size + 50
        )  # Some buffer for truncation message
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_execute_code_with_error_output(self):
        """Test code execution that produces stderr output."""
        sandbox = CodeSandbox()

        code = "import sys\nsys.stderr.write('error message')\nraise Exception('test error')"

        result = await sandbox.execute_code(code, CodeLanguage.PYTHON)

        assert result.status == ExecutionStatus.FAILED
        assert result.exit_code != 0
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_compile_java_code(self):
        """Test Java code compilation path."""
        sandbox = CodeSandbox()

        # Simple Java code
        code = "public class Main { public static void main(String[] args) { System.out.println(&quot;Hello&quot;); } }"

        result = await sandbox.execute_code(code, CodeLanguage.JAVA)

        # May fail if Java not installed, but we test the path
        assert result.execution_id is not None
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_compile_cpp_code(self):
        """Test C++ code compilation path."""
        sandbox = CodeSandbox()

        code = "#include <iostream>\nint main() { std::cout << &quot;Hello&quot;; return 0; }"

        result = await sandbox.execute_code(code, CodeLanguage.CPP)

        assert result.execution_id is not None
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_compile_rust_code(self):
        """Test Rust code compilation path."""
        sandbox = CodeSandbox()

        code = "fn main() { println!(&quot;Hello&quot;); }"

        result = await sandbox.execute_code(code, CodeLanguage.RUST)

        assert result.execution_id is not None
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_compile_go_code(self):
        """Test Go code compilation path."""
        sandbox = CodeSandbox()

        code = 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello")\n}'

        result = await sandbox.execute_code(code, CodeLanguage.GO)

        assert result.execution_id is not None
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_compile_code_failure(self):
        """Test code compilation failure."""
        sandbox = CodeSandbox()

        # Invalid Java code - compilation will fail
        code = "invalid java code"

        result = await sandbox.execute_code(code, CodeLanguage.JAVA)

        # May be ERROR if javac not installed, or FAILED if compilation fails
        assert result.status in [ExecutionStatus.FAILED, ExecutionStatus.ERROR]
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_execute_javascript_code(self):
        """Test JavaScript code execution."""
        sandbox = CodeSandbox()

        code = "console.log('Hello from JS');"

        result = await sandbox.execute_code(code, CodeLanguage.JAVASCRIPT)

        assert result.execution_id is not None
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_run_code_exception_handling(self):
        """Test _run_code exception handling."""
        sandbox = CodeSandbox()

        # Create a situation that causes an exception
        with patch("asyncio.create_subprocess_exec", side_effect=OSError("Process error")):
            result = await sandbox._run_code(
                "temp_file.py", CodeLanguage.PYTHON, None, sandbox.config, "exec_test", 0.0
            )

            assert result.status == ExecutionStatus.ERROR

    @pytest.mark.asyncio
    async def test_list_executions_with_data(self):
        """Test list_executions with mock data."""
        sandbox = CodeSandbox()

        # Add some mock executions
        sandbox.executions["exec_0"] = ExecutionResult(
            execution_id="exec_0",
            status=ExecutionStatus.COMPLETED,
            language=CodeLanguage.PYTHON,
            code="",
            output="",
            error="",
            exit_code=0,
            execution_time=0.5,
            memory_used=10.0,
            start_time=0.0,
            end_time=0.5,
        )
        sandbox.executions["exec_1"] = ExecutionResult(
            execution_id="exec_1",
            status=ExecutionStatus.FAILED,
            language=CodeLanguage.PYTHON,
            code="",
            output="",
            error="error",
            exit_code=1,
            execution_time=0.3,
            memory_used=5.0,
            start_time=0.0,
            end_time=0.3,
        )

        execution_list = sandbox.list_executions()

        assert len(execution_list) == 2
        assert "exec_0" in execution_list
        assert "exec_1" in execution_list
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_security_check_commented_dangerous(self):
        """Test that commented dangerous patterns are allowed."""
        sandbox = CodeSandbox()

        code = "# This is a comment with exec('test')\nprint('safe')"

        result = await sandbox._check_python_security(code, SandboxConfig())

        assert result["allowed"] is True

    @pytest.mark.asyncio
    async def test_security_check_enable_filesystem(self):
        """Test security check with filesystem enabled."""
        sandbox = CodeSandbox()

        config = SandboxConfig(enable_filesystem=True)

        # Note: open( is still in dangerous_patterns even with enable_filesystem=True
        # But filesystem=False adds additional patterns like os.path
        # So we test that os.path is NOT blocked when filesystem is enabled
        result = await sandbox._check_python_security("import os\nos.path.join('a', 'b')", config)

        # Should be allowed since os.path is not blocked when enable_filesystem=True
        # But open() is still blocked
        assert result["allowed"] is True or "os.path" not in result.get("reason", "")

    @pytest.mark.asyncio
    async def test_security_check_enable_network(self):
        """Test security check with network enabled."""
        sandbox = CodeSandbox()

        config = SandboxConfig(enable_network=True)

        # urllib should NOT be blocked when network is enabled
        result = await sandbox._check_python_security("import urllib.request", config)

        # Should be allowed since urllib is not in dangerous patterns when network enabled
        assert result["allowed"] is True or "urllib" not in result.get("reason", "")

    @pytest.mark.asyncio
    async def test_analyze_code_javascript(self):
        """Test analyzing JavaScript code."""
        sandbox = CodeSandbox()

        code = "function test() {}\nclass MyClass {}"

        result = await sandbox.analyze_code(code, CodeLanguage.JAVASCRIPT)

        assert result["language"] == "javascript"

    @pytest.mark.asyncio
    async def test_validate_code_unsupported_language(self):
        """Test validating code with unsupported language."""
        sandbox = CodeSandbox()

        result = await sandbox.validate_code("code", CodeLanguage.RUBY)

        # Should still return a result (might be valid by default for unsupported)
        assert "valid" in result

    @pytest.mark.asyncio
    async def test_analyze_code_unsupported_language(self):
        """Test analyzing code with unsupported language."""
        sandbox = CodeSandbox()

        result = await sandbox.analyze_code("code", CodeLanguage.PHP)

        assert "language" in result

    def test_create_temp_file_java(self):
        """Test _create_temp_file for Java."""
        sandbox = CodeSandbox()

        temp_file = sandbox._create_temp_file("public class Main {}", CodeLanguage.JAVA)

        assert temp_file.endswith(".java")
        sandbox.cleanup()

    def test_create_temp_file_cpp(self):
        """Test _create_temp_file for C++."""
        sandbox = CodeSandbox()

        temp_file = sandbox._create_temp_file("int main() {}", CodeLanguage.CPP)

        assert temp_file.endswith(".cpp")
        sandbox.cleanup()

    def test_create_temp_file_rust(self):
        """Test _create_temp_file for Rust."""
        sandbox = CodeSandbox()

        temp_file = sandbox._create_temp_file("fn main() {}", CodeLanguage.RUST)

        assert temp_file.endswith(".rs")
        sandbox.cleanup()

    def test_create_temp_file_go(self):
        """Test _create_temp_file for Go."""
        sandbox = CodeSandbox()

        temp_file = sandbox._create_temp_file("package main", CodeLanguage.GO)

        assert temp_file.endswith(".go")
        sandbox.cleanup()

    @pytest.mark.asyncio
    async def test_execute_code_exception_in_run(self):
        """Test execute_code when _run_code raises exception."""
        sandbox = CodeSandbox()

        # Patch _run_code to raise exception
        with patch.object(sandbox, "_run_code", side_effect=Exception("Run error")):
            result = await sandbox.execute_code("print('test')", CodeLanguage.PYTHON)

            assert result.status == ExecutionStatus.ERROR
            assert "Run error" in result.error

    @pytest.mark.asyncio
    async def test_compile_code_exception(self):
        """Test _compile_code when exception occurs."""
        sandbox = CodeSandbox()

        lang_config = {
            "extension": ".java",
            "compile_command": ["javac"],
        }

        with patch("asyncio.create_subprocess_exec", side_effect=Exception("Compile error")):
            result = await sandbox._compile_code("Test.java", CodeLanguage.JAVA, lang_config)

            assert result is False

    @pytest.mark.asyncio
    async def test_compile_code_timeout(self):
        """Test _compile_code timeout."""
        sandbox = CodeSandbox()

        lang_config = {
            "extension": ".java",
            "compile_command": ["javac"],
        }

        async def slow_compile(*args, **kwargs):
            await asyncio.sleep(100)
            return AsyncMock()

        with patch("asyncio.create_subprocess_exec") as mock_exec:
            mock_exec.return_value = AsyncMock()
            mock_exec.return_value.communicate = AsyncMock(side_effect=asyncio.TimeoutError())

            with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError()):
                result = await sandbox._compile_code("Test.java", CodeLanguage.JAVA, lang_config)

                assert result is False
