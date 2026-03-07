"""
Code Sandbox Module
Provides secure code execution environment for running and testing code.
Supports multiple programming languages, resource limits, and output capture.
"""

import asyncio
import logging
import subprocess
import tempfile
import os
import json
import sys
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeLanguage(Enum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    RUST = "rust"
    GO = "go"
    RUBY = "ruby"
    PHP = "php"


class ExecutionStatus(Enum):
    """Status of code execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    MEMORY_ERROR = "memory_error"
    ERROR = "error"


@dataclass
class ExecutionResult:
    """Result of code execution."""
    execution_id: str
    status: ExecutionStatus
    language: CodeLanguage
    code: str
    output: str
    error: str
    exit_code: int
    execution_time: float
    memory_used: float
    start_time: float
    end_time: float


@dataclass
class SandboxConfig:
    """Configuration for the code sandbox."""
    max_execution_time: float = 30.0  # seconds
    max_memory: int = 256  # MB
    max_output_size: int = 1000000  # bytes
    allowed_imports: List[str] = field(default_factory=list)
    forbidden_imports: List[str] = field(default_factory=list)
    enable_network: bool = False
    enable_filesystem: bool = False
    allowed_files: List[str] = field(default_factory=list)


class CodeSandbox:
    """
    Code Sandbox for OMNI-AI.
    
    Provides secure code execution capabilities including:
    - Multi-language support
    - Resource limits (time, memory, output)
    - Input/output capture
    - Error handling and reporting
    - Security restrictions
    - Execution statistics
    """
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        Initialize Code Sandbox.
        
        Args:
            config: Sandbox configuration
        """
        self.config = config or SandboxConfig()
        self.executions: Dict[str, ExecutionResult] = {}
        self.temp_dir = tempfile.mkdtemp(prefix="omni_sandbox_")
        
        # Language-specific configurations
        self.language_configs = {
            CodeLanguage.PYTHON: {
                "extension": ".py",
                "command": ["python3", "-u"],
                "timeout": self.config.max_execution_time
            },
            CodeLanguage.JAVASCRIPT: {
                "extension": ".js",
                "command": ["node"],
                "timeout": self.config.max_execution_time
            },
            CodeLanguage.JAVA: {
                "extension": ".java",
                "compile_command": ["javac"],
                "run_command": ["java"],
                "timeout": self.config.max_execution_time
            },
            CodeLanguage.CPP: {
                "extension": ".cpp",
                "compile_command": ["g++", "-o"],
                "run_command": [],
                "timeout": self.config.max_execution_time
            },
            CodeLanguage.RUST: {
                "extension": ".rs",
                "compile_command": ["rustc", "-o"],
                "run_command": [],
                "timeout": self.config.max_execution_time
            },
            CodeLanguage.GO: {
                "extension": ".go",
                "compile_command": ["go", "build", "-o"],
                "run_command": [],
                "timeout": self.config.max_execution_time
            }
        }
        
        logger.info("Code Sandbox initialized")
    
    async def execute_code(self,
                          code: str,
                          language: CodeLanguage,
                          input_data: Optional[str] = None,
                          config: Optional[SandboxConfig] = None) -> ExecutionResult:
        """
        Execute code in the sandbox.
        
        Args:
            code: Source code to execute
            language: Programming language
            input_data: Optional input data for stdin
            config: Optional sandbox config override
            
        Returns:
            ExecutionResult object
        """
        execution_id = f"exec_{len(self.executions)}"
        start_time = asyncio.get_event_loop().time()
        
        # Use provided config or default
        sandbox_config = config or self.config
        
        # Security check for Python code
        if language == CodeLanguage.PYTHON:
            security_check = await self._check_python_security(code, sandbox_config)
            if not security_check["allowed"]:
                return ExecutionResult(
                    execution_id=execution_id,
                    status=ExecutionStatus.ERROR,
                    language=language,
                    code=code,
                    output="",
                    error=security_check["reason"],
                    exit_code=1,
                    execution_time=0.0,
                    memory_used=0.0,
                    start_time=start_time,
                    end_time=start_time
                )
        
        # Create temporary file for code
        temp_file = self._create_temp_file(code, language)
        
        try:
            # Execute the code
            result = await self._run_code(
                temp_file,
                language,
                input_data,
                sandbox_config,
                execution_id,
                start_time
            )
            
            self.executions[execution_id] = result
            return result
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            end_time = asyncio.get_event_loop().time()
            
            error_result = ExecutionResult(
                execution_id=execution_id,
                status=ExecutionStatus.ERROR,
                language=language,
                code=code,
                output="",
                error=str(e),
                exit_code=1,
                execution_time=end_time - start_time,
                memory_used=0.0,
                start_time=start_time,
                end_time=end_time
            )
            
            self.executions[execution_id] = error_result
            return error_result
    
    async def _run_code(self,
                       temp_file: str,
                       language: CodeLanguage,
                       input_data: Optional[str],
                       config: SandboxConfig,
                       execution_id: str,
                       start_time: float) -> ExecutionResult:
        """Run code in subprocess."""
        lang_config = self.language_configs.get(language)
        
        if not lang_config:
            raise ValueError(f"Unsupported language: {language}")
        
        output = ""
        error = ""
        exit_code = 0
        execution_time = 0.0
        memory_used = 0.0
        status = ExecutionStatus.COMPLETED
        
        try:
            # Handle compilation for compiled languages
            if "compile_command" in lang_config:
                compile_success = await self._compile_code(
                    temp_file,
                    language,
                    lang_config
                )
                if not compile_success:
                    status = ExecutionStatus.FAILED
                    error = "Compilation failed"
            
            # Prepare command
            if language in [CodeLanguage.JAVA, CodeLanguage.CPP, CodeLanguage.RUST, CodeLanguage.GO]:
                # Compiled languages
                executable = temp_file.replace(lang_config["extension"], "")
                command = [executable]
            else:
                # Interpreted languages
                command = lang_config["command"] + [temp_file]
            
            # Run code with timeout
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            # Write input if provided
            if input_data:
                process.stdin.write(input_data.encode())
                process.stdin.close()
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.max_execution_time
                )
                
                output = stdout.decode('utf-8', errors='replace')
                error = stderr.decode('utf-8', errors='replace')
                exit_code = process.returncode
                execution_time = asyncio.get_event_loop().time() - start_time
                
                # Check exit status
                if exit_code != 0:
                    status = ExecutionStatus.FAILED
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                status = ExecutionStatus.TIMEOUT
                error = f"Execution timeout after {config.max_execution_time}s"
                execution_time = config.max_execution_time
            
            # Truncate output if too large
            if len(output) > config.max_output_size:
                output = output[:config.max_output_size]
                output += "\n... (output truncated)"
            
            if len(error) > config.max_output_size:
                error = error[:config.max_output_size]
                error += "\n... (error truncated)"
            
        except Exception as e:
            status = ExecutionStatus.ERROR
            error = str(e)
            logger.error(f"Execution error: {e}")
        
        end_time = asyncio.get_event_loop().time()
        
        return ExecutionResult(
            execution_id=execution_id,
            status=status,
            language=language,
            code="",  # Don't store full code in result
            output=output,
            error=error,
            exit_code=exit_code,
            execution_time=execution_time,
            memory_used=memory_used,
            start_time=start_time,
            end_time=end_time
        )
    
    async def _compile_code(self,
                           temp_file: str,
                           language: CodeLanguage,
                           lang_config: Dict[str, Any]) -> bool:
        """Compile code for compiled languages."""
        try:
            if language == CodeLanguage.JAVA:
                compile_cmd = lang_config["compile_command"] + [temp_file]
            elif language == CodeLanguage.CPP:
                executable = temp_file.replace(".cpp", "")
                compile_cmd = lang_config["compile_command"] + [executable, temp_file]
            elif language == CodeLanguage.RUST:
                executable = temp_file.replace(".rs", "")
                compile_cmd = lang_config["compile_command"] + [executable, temp_file]
            elif language == CodeLanguage.GO:
                executable = temp_file.replace(".go", "")
                compile_cmd = lang_config["compile_command"] + [executable, temp_file]
            else:
                return True
            
            process = await asyncio.create_subprocess_exec(
                *compile_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30.0
            )
            
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Compilation error: {e}")
            return False
    
    async def _check_python_security(self, code: str, config: SandboxConfig) -> Dict[str, Any]:
        """Check Python code for security issues."""
        result = {"allowed": True, "reason": ""}
        
        # Check for forbidden imports
        for forbidden in config.forbidden_imports:
            if forbidden in code:
                result["allowed"] = False
                result["reason"] = f"Forbidden import: {forbidden}"
                return result
        
        # Check for dangerous operations
        dangerous_patterns = [
            "__import__",
            "exec(",
            "eval(",
            "compile(",
            "open(",
            "os.system",
            "subprocess.",
            "pickle.",
            "marshal."
        ]
        
        if not config.enable_filesystem:
            dangerous_patterns.extend(["open(", "file(", "os.path"])
        
        if not config.enable_network:
            dangerous_patterns.extend(["urllib.", "requests.", "socket.", "http."])
        
        for pattern in dangerous_patterns:
            if pattern in code:
                # Allow some patterns in comments
                lines = code.split('\n')
                for line in lines:
                    if pattern in line and not line.strip().startswith('#'):
                        result["allowed"] = False
                        result["reason"] = f"Potentially dangerous operation: {pattern}"
                        return result
        
        return result
    
    def _create_temp_file(self, code: str, language: CodeLanguage) -> str:
        """Create temporary file for code."""
        lang_config = self.language_configs.get(language, {})
        extension = lang_config.get("extension", ".txt")
        
        temp_file = os.path.join(
            self.temp_dir,
            f"code_{len(self.executions)}{extension}"
        )
        
        with open(temp_file, 'w') as f:
            f.write(code)
        
        return temp_file
    
    async def validate_code(self, code: str, language: CodeLanguage) -> Dict[str, Any]:
        """
        Validate code syntax without executing.
        
        Args:
            code: Source code to validate
            language: Programming language
            
        Returns:
            Validation result
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            if language == CodeLanguage.PYTHON:
                # Python syntax check
                try:
                    compile(code, '<string>', 'exec')
                except SyntaxError as e:
                    result["valid"] = False
                    result["errors"].append({
                        "line": e.lineno,
                        "column": e.offset,
                        "message": str(e.msg)
                    })
            
            elif language == CodeLanguage.JAVASCRIPT:
                # Basic JS syntax check
                if "function" not in code and "const" not in code and "let" not in code:
                    result["warnings"].append("No function or variable declarations found")
            
            # Add more language validators as needed
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(str(e))
        
        return result
    
    async def analyze_code(self, code: str, language: CodeLanguage) -> Dict[str, Any]:
        """
        Analyze code for complexity, quality, and patterns.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        analysis = {
            "language": language.value,
            "lines": len(code.split('\n')),
            "characters": len(code),
            "complexity": 0,
            "functions": 0,
            "classes": 0,
            "imports": [],
            "issues": []
        }
        
        try:
            lines = code.split('\n')
            
            if language == CodeLanguage.PYTHON:
                # Count functions and classes
                for line in lines:
                    if line.strip().startswith('def '):
                        analysis["functions"] += 1
                    elif line.strip().startswith('class '):
                        analysis["classes"] += 1
                    elif line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_stmt = line.strip().split()[1]
                        analysis["imports"].append(import_stmt)
                
                # Simple complexity (cyclomatic complexity approximation)
                complexity_keywords = ['if ', 'elif ', 'for ', 'while ', 'except ']
                for line in lines:
                    for keyword in complexity_keywords:
                        if keyword in line:
                            analysis["complexity"] += 1
            
            # Add more language-specific analyzers
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
        
        return analysis
    
    async def get_execution(self, execution_id: str) -> Optional[ExecutionResult]:
        """
        Get execution result by ID.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            ExecutionResult or None
        """
        return self.executions.get(execution_id)
    
    def list_executions(self) -> List[str]:
        """List all execution IDs."""
        return list(self.executions.keys())
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


async def main():
    """Example usage of Code Sandbox."""
    sandbox = CodeSandbox()
    
    # Execute Python code
    python_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""
    
    result = await sandbox.execute_code(python_code, CodeLanguage.PYTHON)
    print(f"Python execution:\n{result.output}")
    print(f"Status: {result.status.value}")
    print(f"Time: {result.execution_time:.3f}s")
    
    # Analyze code
    analysis = await sandbox.analyze_code(python_code, CodeLanguage.PYTHON)
    print(f"\nCode analysis:\n{json.dumps(analysis, indent=2)}")
    
    # Cleanup
    sandbox.cleanup()


if __name__ == "__main__":
    asyncio.run(main())