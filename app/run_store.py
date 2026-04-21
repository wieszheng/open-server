"""
最新执行结果持久化（每次执行覆盖上一次，只保留最新）

存储结构：
  open-server/data/
    run_meta.json          ← 本次执行汇总（case_id、total/passed/failed、时间）
    screenshots/
      {node_id}.png        ← 节点执行后截图（无截图则不存在）
    node_results.json      ← 节点结果列表
"""
import base64
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

# data 目录与 run_store.py 同级
_DATA_DIR = Path(__file__).parent.parent / "data"
_SHOT_DIR = _DATA_DIR / "screenshots"
_META_FILE = _DATA_DIR / "run_meta.json"
_NODES_FILE = _DATA_DIR / "node_results.json"


def _ensure_dirs():
    _DATA_DIR.mkdir(exist_ok=True)
    _SHOT_DIR.mkdir(exist_ok=True)


def clear_run():
    """每次新执行开始前清空上一次结果。"""
    _ensure_dirs()
    if _SHOT_DIR.exists():
        shutil.rmtree(_SHOT_DIR)
    _SHOT_DIR.mkdir()
    _META_FILE.unlink(missing_ok=True)
    _NODES_FILE.unlink(missing_ok=True)


def save_meta(job_id: str, case_id: int, case_name: str):
    """写入执行汇总（初始状态，执行完成后更新）。"""
    _ensure_dirs()
    meta = {
        "job_id": job_id,
        "case_id": case_id,
        "case_name": case_name,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
        "total": 0,
        "passed": 0,
        "failed": 0,
    }
    _META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def finish_meta(total: int, passed: int, failed: int):
    """执行完成后更新汇总统计。"""
    if not _META_FILE.exists():
        return
    meta = json.loads(_META_FILE.read_text(encoding="utf-8"))
    meta.update({
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "passed": passed,
        "failed": failed,
    })
    _META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def save_node_result(
    node_id: str,
    node_type: str,
    label: str,
    success: bool,
    message: str,
    duration: float,
    screenshot_b64: str | None,
):
    """追加一条节点结果，并保存截图文件。"""
    _ensure_dirs()

    # 追加到 node_results.json
    results: list[dict] = []
    if _NODES_FILE.exists():
        results = json.loads(_NODES_FILE.read_text(encoding="utf-8"))

    has_shot = False
    if screenshot_b64:
        # 去掉 data:image/png;base64, 前缀
        raw = screenshot_b64.split(",", 1)[-1]
        try:
            png = base64.b64decode(raw)
            (_SHOT_DIR / f"{node_id}.png").write_bytes(png)
            has_shot = True
        except Exception:
            pass

    results.append({
        "node_id": node_id,
        "node_type": node_type,
        "label": label,
        "success": success,
        "message": message,
        "duration": round(duration, 4),
        "has_shot": has_shot,
        "ts": datetime.now(timezone.utc).isoformat(),
    })
    _NODES_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# 查询接口
# ---------------------------------------------------------------------------

def get_meta() -> dict | None:
    if not _META_FILE.exists():
        return None
    return json.loads(_META_FILE.read_text(encoding="utf-8"))


def get_node_results() -> list[dict]:
    if not _NODES_FILE.exists():
        return []
    return json.loads(_NODES_FILE.read_text(encoding="utf-8"))


def get_screenshot(node_id: str) -> bytes | None:
    path = _SHOT_DIR / f"{node_id}.png"
    if not path.exists():
        return None
    return path.read_bytes()
