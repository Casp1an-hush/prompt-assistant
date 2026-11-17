# -*- coding: utf-8 -*-
"""并发槽位测试：验证闸门上限、释放与僵尸槽位自愈。

这段是之前「跑不动」故障的根因——客户端断连导致 finally 不执行、
名额永久泄漏。这里锁死行为：超时槽位必须被自动回收，不能让后来者一直 busy。
"""
from __future__ import annotations

import time

import pytest

import config
import errors
import llm


@pytest.fixture(autouse=True)
def clean_slots(monkeypatch):
    """每个用例从空的槽位表开始，且把上限固定为 2。"""
    monkeypatch.setattr(config, "MAX_CONCURRENCY", 2)
    with llm._gate_lock:
        llm._slots.clear()
    yield
    with llm._gate_lock:
        llm._slots.clear()


def test_acquire_and_release():
    assert llm.active_slots() == 0
    token = llm.acquire_slot()
    assert token
    assert llm.active_slots() == 1
    llm.release_slot(token)
    assert llm.active_slots() == 0


def test_acquire_respects_limit():
    monkeypatch_max = config.MAX_CONCURRENCY
    t1 = llm.acquire_slot()
    t2 = llm.acquire_slot()
    assert llm.active_slots() == monkeypatch_max
    with pytest.raises(errors.BusyError) as exc:
        llm.acquire_slot()
    assert exc.value.http_status == 429
    llm.release_slot(t1)
    llm.release_slot(t2)


def test_release_is_idempotent():
    """background 任务和生成器 finally 会各释放一次，重复释放不能出错。"""
    token = llm.acquire_slot()
    llm.release_slot(token)
    llm.release_slot(token)
    llm.release_slot("从没存在过的-token")
    assert llm.active_slots() == 0


def test_touch_refreshes_liveness():
    token = llm.acquire_slot()
    with llm._gate_lock:
        born, last = llm._slots[token]
        llm._slots[token] = (born, last - 100)
        refreshed_before = llm._slots[token][1]
    llm.touch_slot(token)
    with llm._gate_lock:
        assert llm._slots[token][1] > refreshed_before


def test_idle_zombie_slot_is_reaped(monkeypatch):
    """断连残留的槽位超过 idle TTL 后自动回收，后来者能立刻拿到名额。"""
    monkeypatch.setattr(config, "MAX_CONCURRENCY", 1)
    token = llm.acquire_slot()
    with llm._gate_lock:
        born, last = llm._slots[token]
        # 把最后活跃时间改到很久以前，模拟客户端断连后无人续租
        llm._slots[token] = (born, last - llm.SLOT_IDLE_TTL - 1)

    # active_slots 内部会触发 _reap
    assert llm.active_slots() == 0
    assert llm.acquire_slot()  # 不再 busy
    llm.release_slot(token)


def test_overlong_slot_is_reaped_by_max_ttl(monkeypatch):
    """即使一直有心跳，超过绝对上限的槽位也要回收，防止无限占用。"""
    monkeypatch.setattr(config, "MAX_CONCURRENCY", 1)
    token = llm.acquire_slot()
    with llm._gate_lock:
        _, last = llm._slots[token]
        llm._slots[token] = (last - llm.SLOT_MAX_TTL - 1, last)

    assert llm.active_slots() == 0
    llm.release_slot(token)


def test_reap_keeps_healthy_slots(monkeypatch):
    """健康的活跃槽位不能被误回收。"""
    monkeypatch.setattr(config, "MAX_CONCURRENCY", 2)
    tokens = [llm.acquire_slot(), llm.acquire_slot()]
    llm.touch_slot(tokens[0])
    assert llm.active_slots() == 2
    for token in tokens:
        llm.release_slot(token)
