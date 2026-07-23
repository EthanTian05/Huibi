"""PostgreSQL读写：用户历史提交与进步追踪，对应Docs/01-系统架构与Agent设计.md
「历史进步仪表盘」。用`psycopg`（v3）连接本地PostgreSQL，需要先本地装好
PostgreSQL并跑着（见Docs/03-RUNNING.md「数据库」），也需要`pip install`
（不是标准库）。**本轮从SQLite迁移过来**：JSON字段（`official_rubric_scores`/
`score_details`/`feedback_dimensions`/`coach_plan`）改用PostgreSQL原生`JSONB`
类型，不再是TEXT里存JSON字符串，psycopg3会自动做Python dict<->JSONB的双向转换，
不需要手动`json.dumps`/`json.loads`。已经删掉了`essay_prompt_id`/`quant_score`/
`trait_scores`三个死列——这几列是已删除的自训练A/B评分模型专用的，早就没有
代码在写了，迁移到新数据库正好清掉，不是数据丢失（本地开发环境本来就没有
真实存量数据）。

**登录注册的密码存储说明（诚实标注，不要说成"生产级安全方案"）**：
用标准库`hashlib.pbkdf2_hmac`+逐用户随机salt做密码哈希，足够应付个人项目演示，
不是bcrypt/argon2这类专门为密码哈希设计的算法，也没有做登录失败限流/邮箱验证/
密码找回，如果这个项目要长期对外提供服务，这些都需要补上。
"""
from __future__ import annotations

import base64
import hashlib
import os
import secrets
from pathlib import Path
from typing import Optional
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    exam_type TEXT,
    exam_subtype TEXT,
    essay_topic TEXT,
    official_rubric_score DOUBLE PRECISION,
    official_rubric_max DOUBLE PRECISION,
    official_rubric_label TEXT,
    official_rubric_scores JSONB NOT NULL DEFAULT '{}'::jsonb,
    score_source TEXT,
    primary_score DOUBLE PRECISION,
    primary_max DOUBLE PRECISION,
    primary_label TEXT,
    secondary_score DOUBLE PRECISION,
    secondary_max DOUBLE PRECISION,
    secondary_label TEXT,
    score_details JSONB NOT NULL DEFAULT '{}'::jsonb,
    score_error TEXT,
    qualitative_feedback TEXT,
    feedback_dimensions JSONB NOT NULL DEFAULT '{}'::jsonb,
    revision_plan TEXT,
    coach_plan JSONB NOT NULL DEFAULT '{}'::jsonb,
    overall_summary TEXT,
    essay_image_path TEXT,
    image_analysis TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 表已经在旧版本（没有这两列）建过的话，CREATE TABLE IF NOT EXISTS不会补列，
-- 这两条ALTER负责把已存在的旧表补齐；新建的表这两列已经在上面CREATE TABLE里，
-- ADD COLUMN IF NOT EXISTS会直接跳过，不会报错也不会重复。
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS essay_image_path TEXT;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS image_analysis TEXT;

CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON submissions (user_id, created_at);
"""

# 图片文件存本地文件系统，数据库只存相对路径——base64图片体积大，直接塞进
# 数据库字段会拖慢这张表的查询，本轮之前雅思Task1上传的图片完全没有持久化，
# 见Docs/TODO.md"雅思Task 1上传的图片没有存进数据库"这条待决策。
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_UPLOADS_DIR = _PROJECT_ROOT / "data" / "uploads"


def _sniff_image_ext(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    return "png"


def _save_uploaded_image(essay_image_b64: str) -> str:
    """把base64图片解码写入`data/uploads/`，返回相对项目根目录的路径（存进
    数据库的是这个路径字符串，不是图片本身）。"""
    _UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    raw = base64.b64decode(essay_image_b64)
    filename = f"{uuid4().hex}.{_sniff_image_ext(raw)}"
    (_UPLOADS_DIR / filename).write_bytes(raw)
    return f"data/uploads/{filename}"

PBKDF2_ITERATIONS = 100_000


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    ).hex()


def _build_dsn() -> str:
    """从环境变量拼PostgreSQL连接串，默认对应本地`scoop install postgresql`
    装出来的实例（trust本地认证，默认超级用户`postgres`、空密码）。"""
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    dbname = os.environ.get("POSTGRES_DB", "huibi")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "")
    auth = f"{user}:{password}" if password else user
    return f"postgresql://{auth}@{host}:{port}/{dbname}"


def get_connection(dsn: Optional[str] = None) -> psycopg.Connection:
    """建连接并确保schema存在。`dsn`不传时按环境变量拼默认库；测试脚本传
    指向`huibi_test`库的dsn做隔离（见`scripts/e2e_graph_test.py`），不再像
    SQLite版那样传临时文件路径。"""
    conn = psycopg.connect(dsn or _build_dsn())
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    conn.commit()
    return conn


def create_user(username: str, password: str, dsn: Optional[str] = None) -> tuple[bool, str]:
    """注册新用户，返回(是否成功, 提示信息)。"""
    username = username.strip()
    if not username or not password:
        return False, "用户名和密码都不能为空"
    if len(password) < 6:
        return False, "密码至少需要6位"

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    conn = get_connection(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s)",
                (username, password_hash, salt),
            )
        conn.commit()
        return True, "注册成功，请登录"
    except psycopg.errors.UniqueViolation:
        conn.rollback()
        return False, "用户名已存在，请换一个用户名"
    finally:
        conn.close()


def verify_user(username: str, password: str, dsn: Optional[str] = None) -> bool:
    """校验用户名/密码是否匹配，用于登录。"""
    conn = get_connection(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash, salt FROM users WHERE username = %s", (username.strip(),)
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return False
    stored_hash, salt = row
    return secrets.compare_digest(_hash_password(password, salt), stored_hash)


_SUBMISSION_COLUMNS = [
    "user_id", "exam_type", "exam_subtype", "essay_topic",
    "official_rubric_score", "official_rubric_max", "official_rubric_label", "official_rubric_scores",
    "score_source", "primary_score", "primary_max", "primary_label",
    "secondary_score", "secondary_max", "secondary_label",
    "score_details", "score_error", "qualitative_feedback", "feedback_dimensions",
    "revision_plan", "coach_plan", "overall_summary",
    "essay_image_path", "image_analysis",
]


def save_submission(state: dict, dsn: Optional[str] = None) -> None:
    essay_image_b64 = state.get("essay_image_b64")
    essay_image_path = _save_uploaded_image(essay_image_b64) if essay_image_b64 else None
    values = (
        state.get("user_id", "anonymous"),
        state.get("exam_type"),
        state.get("exam_subtype"),
        state.get("essay_topic"),
        state.get("official_rubric_score"),
        state.get("official_rubric_max"),
        state.get("official_rubric_label"),
        Jsonb(state.get("official_rubric_scores") or {}),
        state.get("score_source"),
        state.get("primary_score"),
        state.get("primary_max"),
        state.get("primary_label"),
        state.get("secondary_score"),
        state.get("secondary_max"),
        state.get("secondary_label"),
        Jsonb(state.get("score_details") or {}),
        state.get("score_error"),
        state.get("qualitative_feedback", ""),
        Jsonb(state.get("feedback_dimensions") or {}),
        state.get("revision_plan", ""),
        Jsonb(state.get("coach_plan") or {}),
        state.get("overall_summary", ""),
        essay_image_path,
        state.get("image_analysis"),
    )
    conn = get_connection(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO submissions ({', '.join(_SUBMISSION_COLUMNS)}) "
                f"VALUES ({', '.join(['%s'] * len(_SUBMISSION_COLUMNS))})",
                values,
            )
        conn.commit()
    finally:
        conn.close()


def get_user_history(user_id: str, dsn: Optional[str] = None) -> list[dict]:
    columns = ["id", "created_at", *_SUBMISSION_COLUMNS]
    conn = get_connection(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {', '.join(columns)} FROM submissions "
                "WHERE user_id = %s ORDER BY created_at ASC",
                (user_id,),
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    history = []
    for row in rows:
        record = dict(zip(columns, row))
        record["created_at"] = record["created_at"].isoformat()
        for json_col in ("official_rubric_scores", "score_details", "feedback_dimensions", "coach_plan"):
            record[json_col] = record[json_col] or {}
        record["qualitative_feedback"] = record["qualitative_feedback"] or ""
        record["revision_plan"] = record["revision_plan"] or ""
        record["overall_summary"] = record["overall_summary"] or ""
        record["image_analysis"] = record["image_analysis"] or ""
        history.append(record)
    return history


def delete_submission(submission_id: int, user_id: str, dsn: Optional[str] = None) -> bool:
    """只允许用户删除属于自己的单条历史记录，连带清掉本地保存的图片文件
    （不清理的话，图片文件会在`data/uploads/`里一直累积成孤儿文件）。"""
    conn = get_connection(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT essay_image_path FROM submissions WHERE id = %s AND user_id = %s",
                (submission_id, user_id),
            )
            row = cur.fetchone()
            cur.execute(
                "DELETE FROM submissions WHERE id = %s AND user_id = %s", (submission_id, user_id)
            )
            deleted = cur.rowcount == 1
        conn.commit()
    finally:
        conn.close()
    if deleted and row and row[0]:
        (_PROJECT_ROOT / row[0]).unlink(missing_ok=True)
    return deleted
