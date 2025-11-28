# backend/app/routers/questions.py
from fastapi import APIRouter, HTTPException
from typing import List
import json
import os
from pathlib import Path

router = APIRouter(prefix="/questions", tags=["questions"])

# 문제 데이터 파일 경로
QUESTIONS_FILE = Path(__file__).parent.parent / "data" / "questions.json"


def load_questions():
    """문제 데이터 로드"""
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse questions data")


@router.get("/")
async def get_all_questions():
    """모든 문제 조회"""
    questions = load_questions()
    return {
        "total": len(questions),
        "questions": questions
    }


@router.get("/categories")
async def get_categories():
    """문제 카테고리 목록 조회"""
    questions = load_questions()
    categories = {}

    for q in questions:
        category = q.get("category", "Unknown")
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "id": q["id"],
            "title": q["title"],
            "type": q["type"],
            "difficulty": q.get("difficulty", "medium")
        })

    return categories


@router.get("/{question_id}")
async def get_question(question_id: str):
    """특정 문제 조회"""
    questions = load_questions()

    for q in questions:
        if q["id"] == question_id:
            return q

    raise HTTPException(status_code=404, detail="Question not found")


@router.get("/type/{question_type}")
async def get_questions_by_type(question_type: str):
    """타입별 문제 조회 (Independent, Integrated)"""
    questions = load_questions()
    filtered = [q for q in questions if q.get("category", "").lower() == question_type.lower()]

    if not filtered:
        raise HTTPException(status_code=404, detail=f"No questions found for type: {question_type}")

    return {
        "type": question_type,
        "count": len(filtered),
        "questions": filtered
    }


@router.get("/difficulty/{level}")
async def get_questions_by_difficulty(level: str):
    """난이도별 문제 조회"""
    questions = load_questions()
    filtered = [q for q in questions if q.get("difficulty", "").lower() == level.lower()]

    if not filtered:
        raise HTTPException(status_code=404, detail=f"No questions found for difficulty: {level}")

    return {
        "difficulty": level,
        "count": len(filtered),
        "questions": filtered
    }
