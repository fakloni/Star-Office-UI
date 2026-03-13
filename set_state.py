#!/usr/bin/env python3
"""Update Star Office UI state (for testing or agent-driven sync).

For automatic state sync from OpenClaw: add a rule in your agent SOUL.md or AGENTS.md:
  Before starting a task: run `python3 set_state.py writing "doing XYZ"`.
  After finishing: run `python3 set_state.py idle "ready"`.
The office UI reads state from the same state.json this script writes.
"""

import json
import os
import sys
from datetime import datetime

HISTORY_FILE = os.environ.get(
    "STAR_OFFICE_HISTORY_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "status-history.json"),
)
HISTORY_MAX_ROUNDS = int(os.environ.get("STAR_STATUS_HISTORY_ROUNDS", "10"))

STATE_FILE = os.environ.get(
    "STAR_OFFICE_STATE_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json"),
)

VALID_STATES = [
    "idle",
    "writing",
    "researching",
    "executing",
    "syncing",
    "error"
]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "state": "idle",
        "detail": "待命中...",
        "progress": 0,
        "updated_at": datetime.now().isoformat()
    }

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("rounds"), list):
                return data
        except Exception:
            pass
    return {"maxRounds": HISTORY_MAX_ROUNDS, "rounds": []}


def save_history(history):
    history["maxRounds"] = HISTORY_MAX_ROUNDS
    rounds = history.get("rounds", [])
    if len(rounds) > HISTORY_MAX_ROUNDS:
        rounds = rounds[-HISTORY_MAX_ROUNDS:]
    history["rounds"] = rounds
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def append_history_step(state_name, detail, ts):
    history = load_history()
    rounds = history.get("rounds", [])

    # idle 只负责收尾，不单独开新轮次
    if state_name == "idle":
        if rounds and not rounds[-1].get("endAt"):
            rounds[-1].setdefault("steps", []).append({"state": state_name, "detail": detail, "at": ts})
            rounds[-1]["endAt"] = ts
            rounds[-1]["title"] = rounds[-1].get("title") or (rounds[-1]["steps"][0].get("detail") if rounds[-1].get("steps") else "")
        history["rounds"] = rounds
        save_history(history)
        return

    # 非 idle：若无进行中轮次则新建
    if (not rounds) or rounds[-1].get("endAt"):
        rounds.append({
            "id": f"r{int(datetime.now().timestamp() * 1000)}",
            "startAt": ts,
            "endAt": None,
            "title": detail or state_name,
            "steps": []
        })

    rounds[-1].setdefault("steps", []).append({"state": state_name, "detail": detail, "at": ts})
    if not rounds[-1].get("title"):
        rounds[-1]["title"] = detail or state_name

    history["rounds"] = rounds
    save_history(history)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python set_state.py <state> [detail]")
        print(f"状态选项: {', '.join(VALID_STATES)}")
        print("\n例子:")
        print("  python set_state.py idle")
        print("  python set_state.py researching \"在查 Godot MCP...\"")
        print("  python set_state.py writing \"在写热点日报模板...\"")
        sys.exit(1)
    
    state_name = sys.argv[1]
    detail = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if state_name not in VALID_STATES:
        print(f"无效状态: {state_name}")
        print(f"有效选项: {', '.join(VALID_STATES)}")
        sys.exit(1)
    
    state = load_state()
    now_iso = datetime.now().isoformat()
    state["state"] = state_name
    state["detail"] = detail
    state["updated_at"] = now_iso

    save_state(state)
    append_history_step(state_name, detail, now_iso)
    print(f"状态已更新: {state_name} - {detail}")
