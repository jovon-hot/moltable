"""Tests: 防批量注册 — 一次性/测试邮箱域名黑名单 + 邮箱格式校验。"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from routes.auth import _is_disposable_email, _validate_email


def test_validate_email_valid():
    assert _validate_email("user@gmail.com")
    assert _validate_email("zhao@fost.com")
    assert _validate_email("a@b.co")


def test_validate_email_invalid():
    assert not _validate_email("no-at-sign")
    assert not _validate_email("no-domain@")
    assert not _validate_email("@nodomain.com")
    assert not _validate_email("")


def test_disposable_email_blocked():
    """测试域名必须被拦截（8月1日 51 个测试账号全是这类）。"""
    assert _is_disposable_email("test@test.com")
    assert _is_disposable_email("x@t.com")
    assert _is_disposable_email("a@example.com")
    assert _is_disposable_email("b@example.org")
    assert _is_disposable_email("c@mailinator.com")
    assert _is_disposable_email("d@10minutemail.com")
    assert _is_disposable_email("e@yopmail.com")


def test_disposable_email_case_insensitive():
    assert _is_disposable_email("User@Test.COM")
    assert _is_disposable_email("X@Example.com")


def test_real_email_allowed():
    """真实邮箱域名必须放行。"""
    assert not _is_disposable_email("zhao@fost.com")
    assert not _is_disposable_email("user@gmail.com")
    assert not _is_disposable_email("someone@qq.com")
    assert not _is_disposable_email("dev@outlook.com")
    assert not _is_disposable_email("name@163.com")
