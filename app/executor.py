"""
工作流执行引擎（服务端）
- 非设备节点：服务端直接执行
- App UI 操作节点：触发 on_node_delegate 回调，等待本地 Agent 返回结果
"""
import re
import time
import asyncio
import inspect
from graphlib import TopologicalSorter, CycleError
from typing import Any, Callable

_VAR_RE = re.compile(r"\{\{(\w+)\}\}")

# 需要委派给本地 Agent 执行的节点类型（与前端 nodes.tsx APP_UI_NODE_TYPES 保持一致）
DELEGATE_TYPES = {
    "appUiAction",       # 旧类型，向后兼容
    "appLaunchApp", "appClick", "appLongPress", "appDoubleClick",
    "appType", "appClearText", "appSwipe", "appTapXy",
    "appWaitElement", "appGetText", "appScreenshot", "appPressKey",
}


def _render(value: Any, ctx: dict) -> Any:
    if isinstance(value, str):
        return _VAR_RE.sub(lambda m: str(ctx.get(m.group(1), m.group(0))), value)
    return value


def _build_graph(nodes: list, edges: list) -> dict[str, set]:
    node_ids = {n["id"] for n in nodes}
    deps: dict[str, set] = {n["id"]: set() for n in nodes}
    for e in edges:
        src, tgt = e.get("source"), e.get("target")
        if src in node_ids and tgt in node_ids:
            deps[tgt].add(src)
    return deps


async def _call(fn, *args):
    if fn is None:
        return
    result = fn(*args)
    if inspect.isawaitable(result):
        await result


async def execute_flow(
    flow: dict,
    *,
    on_node_start: Callable | None = None,
    on_node_done: Callable | None = None,
    on_node_delegate: Callable | None = None,
) -> dict:
    """
    执行工作流。
    on_node_start(node_id, label)
    on_node_done(node_id, label, success, message, duration_s)
    on_node_delegate(node_id, label, node_data) -> (success, message, duration_s)
        当节点类型在 DELEGATE_TYPES 中时调用，由调用方决定如何执行（如转发给本地 Agent）
    """
    nodes: list = flow.get("nodes", [])
    edges: list = flow.get("edges", [])

    if not nodes:
        return {"total": 0, "passed": 0, "failed": 0}

    node_map = {n["id"]: n for n in nodes}
    deps = _build_graph(nodes, edges)

    try:
        sorter = TopologicalSorter(deps)
        sorter.prepare()
    except CycleError as e:
        raise RuntimeError(f"工作流存在循环依赖: {e}") from e

    ctx: dict = {}
    total = len(nodes)
    passed = 0

    while sorter.is_active():
        ready = list(sorter.get_ready())
        for nid in ready:
            node = node_map[nid]
            data = node.get("data", {})
            label = data.get("label") or nid
            t0 = time.perf_counter()

            await _call(on_node_start, nid, label)

            ntype = node.get("type", "")
            if ntype in DELEGATE_TYPES and on_node_delegate is not None:
                # 委派给本地 Agent 执行，注入 _node_type 以便 Agent 识别
                data_with_type = {**data, "_node_type": ntype}
                result = on_node_delegate(nid, label, data_with_type)
                if inspect.isawaitable(result):
                    result = await result
                success, message = result[0], result[1]
                duration = result[2] if len(result) > 2 else time.perf_counter() - t0
            else:
                success, message = await _execute_node(node, ctx)
                duration = time.perf_counter() - t0

            if success:
                passed += 1

            await _call(on_node_done, nid, label, success, message, duration)
            sorter.done(nid)

        await asyncio.sleep(0)

    return {"total": total, "passed": passed, "failed": total - passed}


# ---------------------------------------------------------------------------
# 节点处理器（服务端可直接执行的类型）
# ---------------------------------------------------------------------------

async def _execute_node(node: dict, ctx: dict) -> tuple[bool, str]:
    ntype = node.get("type", "")
    data = node.get("data", {})
    handlers = {
        "httpRequest": _run_http,
        "webUiAction": _run_web_ui,
        "sqlQuery":    _run_sql,
        "assertion":   _run_assertion,
        "extract":     _run_extract,
        "script":      _run_script,
        "wait":        _run_wait,
        "condition":   _run_condition,
    }
    handler = handlers.get(ntype)
    if handler is None:
        return False, f"未知节点类型: {ntype}"
    try:
        return await handler(data, ctx)
    except Exception as exc:
        return False, str(exc)


async def _run_http(data: dict, ctx: dict) -> tuple[bool, str]:
    import httpx, json as _json

    method = data.get("method", "GET").upper()
    url = _render(data.get("url", ""), ctx)
    if not url:
        return False, "URL 不能为空"

    headers_raw = _render(data.get("headers", ""), ctx)
    body_raw = _render(data.get("body", ""), ctx)
    timeout = float(data.get("timeout", 30000)) / 1000

    try:
        headers = _json.loads(headers_raw) if headers_raw else {}
    except Exception:
        headers = {}
    try:
        body = _json.loads(body_raw) if body_raw else None
    except Exception:
        body = body_raw or None

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, headers=headers, json=body)

    ctx["_last_response_status"] = resp.status_code
    ctx["_last_response_body"] = resp.text
    ctx["_last_response_headers"] = dict(resp.headers)
    ctx["_last_response_cookies"] = dict(resp.cookies)
    try:
        ctx["_last_response_json"] = resp.json()
    except Exception:
        ctx["_last_response_json"] = None

    return True, f"{resp.status_code} {resp.reason_phrase}"


async def _run_web_ui(data: dict, ctx: dict) -> tuple[bool, str]:
    action = data.get("action", "click")
    await asyncio.sleep(0.05)
    return True, f"[stub] webUI.{action} OK"


async def _run_sql(data: dict, ctx: dict) -> tuple[bool, str]:
    query = data.get("query", "")
    extract_var = data.get("extractVar", "")
    await asyncio.sleep(0.02)
    if extract_var:
        ctx[extract_var] = "[stub sql result]"
    return True, "[stub] SQL OK"


async def _run_assertion(data: dict, ctx: dict) -> tuple[bool, str]:
    import re as _re
    assert_type = data.get("assertType", "status_code")
    expected = _render(str(data.get("expected", "")), ctx)

    if assert_type == "status_code":
        actual = str(ctx.get("_last_response_status", ""))
        if actual == expected:
            return True, f"status_code {actual} == {expected}"
        return False, f"AssertionError: status_code expected={expected} actual={actual}"

    body = ctx.get("_last_response_body", "")

    if assert_type == "contains":
        if expected in body:
            return True, f"body contains '{expected}'"
        return False, f"AssertionError: body 不包含 '{expected}'"

    if assert_type == "equals":
        if body == expected:
            return True, "body equals expected"
        return False, f"AssertionError: equals failed\n  expected: {expected!r}\n  actual:   {body!r}"

    if assert_type == "regex":
        if not expected:
            return False, "regex 模式不能为空"
        if _re.search(expected, body):
            return True, f"body matches /{expected}/"
        return False, f"AssertionError: body 不匹配 /{expected}/"

    if assert_type == "json_path":
        import jsonpath_ng as _jng
        expression = _render(data.get("expression", ""), ctx)
        resp_json = ctx.get("_last_response_json")
        if resp_json is None:
            return False, "上一步没有 JSON 响应"
        try:
            matches = [m.value for m in _jng.parse(expression).find(resp_json)]
            actual_val = matches[0] if len(matches) == 1 else matches
            actual_str = str(actual_val)
            if actual_str == expected:
                return True, f"{expression} == {expected}"
            return False, f"AssertionError: {expression} expected={expected!r} actual={actual_str!r}"
        except Exception as exc:
            return False, f"JSONPath 解析失败: {exc}"

    if assert_type == "not_empty":
        expression = _render(data.get("expression", ""), ctx)
        resp_json = ctx.get("_last_response_json")
        try:
            import jsonpath_ng as _jng
            matches = [m.value for m in _jng.parse(expression).find(resp_json or {})]
            val = matches[0] if matches else None
        except Exception:
            val = body
        if val not in (None, "", [], {}):
            return True, f"{expression} is not empty"
        return False, f"AssertionError: {expression} is empty or null"

    return False, f"不支持的断言类型: {assert_type}"


async def _run_extract(data: dict, ctx: dict) -> tuple[bool, str]:
    import re as _re
    source = data.get("source", "json_path")
    expression = data.get("expression", "")
    var_name = data.get("varName", "")

    if not var_name:
        return False, "varName 不能为空"

    if source == "json_path":
        import jsonpath_ng as _jng
        resp_json = ctx.get("_last_response_json")
        if resp_json is None:
            return False, "上一步没有 JSON 响应"
        try:
            matches = [m.value for m in _jng.parse(expression).find(resp_json)]
            if not matches:
                return False, f"JSONPath {expression!r} 无匹配结果"
            ctx[var_name] = matches[0] if len(matches) == 1 else matches
            return True, f"{var_name} = {ctx[var_name]!r}"
        except Exception as exc:
            return False, f"JSONPath 解析失败: {exc}"

    if source == "regex":
        body = ctx.get("_last_response_body", "")
        if not expression:
            return False, "正则表达式不能为空"
        m = _re.search(expression, body)
        if not m:
            return False, f"正则 {expression!r} 无匹配"
        ctx[var_name] = m.group(1) if m.lastindex else m.group(0)
        return True, f"{var_name} = {ctx[var_name]!r}"

    if source == "header":
        headers: dict = ctx.get("_last_response_headers", {})
        key = expression.lower()
        val = headers.get(key) or headers.get(expression)
        if val is None:
            return False, f"响应头 {expression!r} 不存在"
        ctx[var_name] = val
        return True, f"{var_name} = {val!r}"

    if source == "cookie":
        cookies: dict = ctx.get("_last_response_cookies", {})
        val = cookies.get(expression)
        if val is None:
            return False, f"Cookie {expression!r} 不存在"
        ctx[var_name] = val
        return True, f"{var_name} = {val!r}"

    if source == "html_css":
        try:
            from html.parser import HTMLParser

            class _CSSExtractor(HTMLParser):
                def __init__(self, selector: str):
                    super().__init__()
                    self.selector = selector
                    self.results: list[str] = []
                    self._tag, self._cls, self._id = None, None, None
                    # 仅支持简单选择器：tag / .class / #id / tag.class
                    if "#" in selector:
                        parts = selector.split("#", 1)
                        self._tag = parts[0] or None
                        self._id = parts[1]
                    elif "." in selector:
                        parts = selector.split(".", 1)
                        self._tag = parts[0] or None
                        self._cls = parts[1]
                    else:
                        self._tag = selector
                    self._capture = False
                    self._buf = ""

                def handle_starttag(self, tag, attrs):
                    attrs_d = dict(attrs)
                    tag_match = self._tag is None or tag == self._tag
                    id_match = self._id is None or attrs_d.get("id") == self._id
                    cls_match = self._cls is None or self._cls in attrs_d.get("class", "").split()
                    if tag_match and id_match and cls_match:
                        self._capture = True
                        self._buf = ""

                def handle_data(self, data):
                    if self._capture:
                        self._buf += data

                def handle_endtag(self, tag):
                    if self._capture and (self._tag is None or tag == self._tag):
                        self.results.append(self._buf.strip())
                        self._capture = False

            parser = _CSSExtractor(expression)
            parser.feed(ctx.get("_last_response_body", ""))
            if not parser.results:
                return False, f"CSS 选择器 {expression!r} 无匹配"
            ctx[var_name] = parser.results[0] if len(parser.results) == 1 else parser.results
            return True, f"{var_name} = {ctx[var_name]!r}"
        except Exception as exc:
            return False, str(exc)

    return False, f"不支持的提取方式: {source}"


async def _run_script(data: dict, ctx: dict) -> tuple[bool, str]:
    lang = data.get("language", "python")
    code = data.get("code", "")
    await asyncio.sleep(0.05)
    return True, f"[stub] {lang} script OK ({len(code)} chars)"


async def _run_wait(data: dict, ctx: dict) -> tuple[bool, str]:
    seconds = float(data.get("seconds", 2))
    await asyncio.sleep(seconds)
    return True, f"waited {seconds}s"


async def _run_condition(data: dict, ctx: dict) -> tuple[bool, str]:
    expression = _render(data.get("expression", "true"), ctx).strip()
    if not expression:
        return False, "条件表达式不能为空"

    try:
        result = _safe_eval(expression, ctx)
    except Exception as exc:
        return False, f"条件表达式求值失败: {exc}"

    passed = bool(result)
    return passed, f"condition({expression!r}) → {result!r}"


def _safe_eval(expr: str, ctx: dict):
    """
    安全求值布尔/算术表达式。
    支持：比较运算、逻辑运算（and/or/not）、算术运算、字符串字面量、ctx 变量引用。
    禁止：函数调用、属性访问、import、exec 等。
    """
    import ast, operator as _op

    _BINOPS = {
        ast.Add: _op.add, ast.Sub: _op.sub,
        ast.Mult: _op.mul, ast.Div: _op.truediv,
        ast.Mod: _op.mod, ast.Pow: _op.pow,
        ast.BitAnd: _op.and_, ast.BitOr: _op.or_,
    }
    _CMPOPS = {
        ast.Eq: _op.eq, ast.NotEq: _op.ne,
        ast.Lt: _op.lt, ast.LtE: _op.le,
        ast.Gt: _op.gt, ast.GtE: _op.ge,
        ast.In: lambda a, b: a in b,
        ast.NotIn: lambda a, b: a not in b,
    }
    _UNOPS = {ast.USub: _op.neg, ast.Not: _op.not_, ast.UAdd: _op.pos}

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in ("True", "true"):  return True
            if node.id in ("False", "false"): return False
            if node.id in ("None", "null"):   return None
            if node.id in ctx:
                return ctx[node.id]
            raise ValueError(f"未定义变量: {node.id!r}")
        if isinstance(node, ast.BinOp):
            op = _BINOPS.get(type(node.op))
            if op is None:
                raise ValueError(f"不支持的运算符: {type(node.op).__name__}")
            return op(_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op = _UNOPS.get(type(node.op))
            if op is None:
                raise ValueError(f"不支持的一元运算符: {type(node.op).__name__}")
            return op(_eval(node.operand))
        if isinstance(node, ast.BoolOp):
            vals = [_eval(v) for v in node.values]
            return all(vals) if isinstance(node.op, ast.And) else any(vals)
        if isinstance(node, ast.Compare):
            left = _eval(node.left)
            for op_node, comparator in zip(node.ops, node.comparators):
                op = _CMPOPS.get(type(op_node))
                if op is None:
                    raise ValueError(f"不支持的比较运算符: {type(op_node).__name__}")
                right = _eval(comparator)
                if not op(left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.IfExp):
            return _eval(node.body) if _eval(node.test) else _eval(node.orelse)
        raise ValueError(f"不支持的表达式节点: {type(node).__name__}")

    tree = ast.parse(expr, mode="eval")
    return _eval(tree)
