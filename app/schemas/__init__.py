"""Pydantic Schemas"""
from app.schemas.script import (
    ScriptBase,
    ScriptCreate,
    ScriptUpdate,
    ScriptResponse,
)
from app.schemas.test_case import (
    TestCaseBase,
    TestCaseCreate,
    TestCaseUpdate,
    TestCaseResponse,
)
from app.schemas.directory import (
    DirectoryBase,
    DirectoryCreate,
    DirectoryUpdate,
    DirectoryResponse,
)
from app.schemas.console import (
    TestExecutionBase,
    TestExecutionCreate,
    TestExecutionResponse,
    TestDurationTrend,
    ConsoleStats,
)
from app.schemas.workflow import (
    FlowUpsert,
    FlowResponse,
    WorkflowResponse,
    WorkflowUpdate,
)

__all__ = [
    # Script
    "ScriptBase",
    "ScriptCreate",
    "ScriptUpdate",
    "ScriptResponse",
    # Test Case
    "TestCaseBase",
    "TestCaseCreate",
    "TestCaseUpdate",
    "TestCaseResponse",
    # Directory
    "DirectoryBase",
    "DirectoryCreate",
    "DirectoryUpdate",
    "DirectoryResponse",
    # Console
    "TestExecutionBase",
    "TestExecutionCreate",
    "TestExecutionResponse",
    "TestDurationTrend",
    "ConsoleStats",
    # Workflow
    "FlowUpsert",
    "FlowResponse",
    "WorkflowResponse",
    "WorkflowUpdate",
]
