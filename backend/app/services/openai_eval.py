# backend/app/services/openai_eval.py
import json
from openai import AsyncOpenAI
from app.config import settings
from app.schemas import EvalResult, EvaluationScores

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# TOEFL Speaking Task prompts
TASK_PROMPTS = {
    1: "Independent Task: Personal Preference",
    2: "Independent Task: Choice",
    3: "Integrated Task: Campus Situation",
    4: "Integrated Task: Academic Course"
}

async def evaluate_speaking(task_id: int, stt_text: str, pron_scores: dict) -> EvalResult:
    """
    Evaluate speaking performance using OpenAI Fine-tuned model.

    Args:
        task_id: TOEFL Speaking task number (1-4)
        stt_text: Transcribed text from STT
        pron_scores: Dictionary containing pronunciation scores

    Returns:
        EvalResult with scores, feedback, and tips
    """

    task_description = TASK_PROMPTS.get(task_id, "Speaking Task")

    system_message = """당신은 따뜻하고 격려적인 TOEFL Speaking 전문 평가자입니다. 학생들이 자신의 강점을 인식하고 개선점을 긍정적으로 받아들일 수 있도록 돕는 것이 목표입니다.

당신의 임무는 학생의 답변을 전사된 텍스트 기반으로 평가하고 다음을 제공하는 것입니다:
1. 점수 (0-4 척도, 소수점 1자리): Fluency(유창성), Pronunciation(발음), Content(내용), Grammar(문법)
2. 총점 (0-4 척도, 소수점 1자리): 네 카테고리의 평균
3. 따뜻하고 격려적인 피드백 (한국어로 작성)
   - 먼저 학생이 잘한 점을 구체적으로 언급
   - 개선이 필요한 부분을 부드럽고 건설적으로 제시
   - 격려와 긍정적인 메시지로 마무리
4. 실천 가능한 개선 팁 2-3개 (한국어로 작성)

평가 기준 (소수점 1자리까지 세밀하게 평가):
- Fluency (0.0-4.0): 자연스러운 말의 흐름, 적절한 속도, 망설임 최소화
  * 3.5-4.0 = 매우 유창하고 자연스러운 흐름
  * 3.0-3.4 = 대체로 유창하나 약간의 망설임
  * 2.5-2.9 = 기본적 유창성은 있으나 자주 멈춤
  * 2.0-2.4 = 유창성에 눈에 띄는 문제
  * 1.0-1.9 = 매우 제한적인 유창성
  * 0.0-0.9 = 거의 발화 없음

- Pronunciation (0.0-4.0): 어휘 수준과 표현력 기반 추정
  * 3.5-4.0 = 고급 어휘와 자연스러운 표현
  * 3.0-3.4 = 좋은 어휘 범위
  * 2.5-2.9 = 적절한 기본 어휘
  * 2.0-2.4 = 제한적 어휘
  * 1.0-1.9 = 매우 기본적인 어휘
  * 0.0-0.9 = 의미 전달 어려움

- Content (0.0-4.0): 과제 관련성, 아이디어 전개, 논리성
  * 3.5-4.0 = 탁월한 내용 전개와 예시
  * 3.0-3.4 = 좋은 내용 전개
  * 2.5-2.9 = 적절한 내용이나 전개 부족
  * 2.0-2.4 = 기본 아이디어만 제시
  * 1.0-1.9 = 관련성 부족
  * 0.0-0.9 = 거의 관련 내용 없음

- Grammar (0.0-4.0): 문법 정확성과 구조 다양성
  * 3.5-4.0 = 높은 정확도와 다양한 구조
  * 3.0-3.4 = 좋은 문법 사용, 사소한 오류
  * 2.5-2.9 = 기본 문법은 정확하나 단순한 구조
  * 2.0-2.4 = 일부 문법 오류
  * 1.0-1.9 = 잦은 문법 오류
  * 0.0-0.9 = 심각한 문법 문제

총점 계산:
- 네 카테고리의 평균 = 총점 (0.0-4.0)
- 소수점 첫째 자리까지 표시
- 예시: (Fluency(3.5) + Pronunciation(3.0) + Content(3.5) + Grammar(3.0)) / 4 = 3.3

**중요 지침:**
1. feedback과 tips는 반드시 한국어로 작성
2. 피드백은 따뜻하고 격려적인 톤 유지
3. 비판보다는 구체적인 개선 방향 제시
4. 학생의 노력을 인정하고 긍정적으로 동기부여

다음 형식의 JSON 객체로만 응답하세요:
{
  "fluency": <0.0-4.0, 소수점 1자리>,
  "pronunciation": <0.0-4.0, 소수점 1자리>,
  "content": <0.0-4.0, 소수점 1자리>,
  "grammar": <0.0-4.0, 소수점 1자리>,
  "total": <0.0-4.0, 소수점 1자리, 네 항목의 평균>,
  "feedback": "<따뜻하고 격려적인 한국어 피드백 (150-250자)>",
  "tips": ["<구체적인 한국어 팁 1>", "<구체적인 한국어 팁 2>", "<구체적인 한국어 팁 3>"]
}"""

    user_message = f"""Task: {task_description} (Task {task_id})

전사된 답변:
{stt_text}

추정된 발음 지표 (참고용):
- 전체 발음: {pron_scores.get('overall', 0):.1f}/100
- 유창성 추정: {pron_scores.get('fluency', 0):.1f}/100

참고: 이는 대략적인 추정치입니다. 전사된 텍스트를 기반으로 자체 평가를 제공해주세요.

이 TOEFL Speaking 답변을 평가해주세요.
**중요:**
- 점수는 소수점 1자리까지 (예: 3.5, 2.8)
- 총점은 네 카테고리의 평균값
- 피드백은 따뜻하고 격려적인 톤으로 한국어로 작성
- 먼저 잘한 점을 언급하고, 개선점을 부드럽게 제시"""

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        # Extract scores as floats and round to 1 decimal place
        fluency = round(min(4.0, max(0.0, float(result.get("fluency", 2.5)))), 1)
        pronunciation = round(min(4.0, max(0.0, float(result.get("pronunciation", 2.5)))), 1)
        content = round(min(4.0, max(0.0, float(result.get("content", 2.5)))), 1)
        grammar = round(min(4.0, max(0.0, float(result.get("grammar", 2.5)))), 1)
        # Calculate total as average of 4 categories
        total = round((fluency + pronunciation + content + grammar) / 4, 1)

        scores = EvaluationScores(
            fluency=fluency,
            pronunciation=pronunciation,
            content=content,
            grammar=grammar,
            total=total
        )

        feedback = result.get("feedback", "No feedback available.")
        tips = result.get("tips", [])

        # Ensure we have at least 2 tips (in Korean)
        if len(tips) < 2:
            tips.extend([
                "유창성 향상을 위해 규칙적으로 말하기 연습을 하세요.",
                "자신의 답변을 녹음하고 원어민 발화와 비교해보세요."
            ])
        tips = tips[:3]  # Limit to 3 tips

        return EvalResult(
            scores=scores,
            feedback=feedback,
            tips=tips
        )

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        # Fallback: return default evaluation
        return EvalResult(
            scores=EvaluationScores(
                fluency=2.5,
                pronunciation=2.5,
                content=2.5,
                grammar=2.5,
                total=2.5
            ),
            feedback="현재 상세한 피드백을 생성할 수 없습니다. 하지만 걱정하지 마세요! 이미 좋은 첫 걸음을 내디뎠습니다. 다시 시도하면 더 구체적인 피드백을 받을 수 있을 거예요.",
            tips=[
                "편안한 마음으로 규칙적으로 말하기 연습을 해보세요. 매일 5분씩이라도 꾸준히 하는 것이 중요합니다.",
                "답변하기 전에 간단하게 핵심 아이디어 2-3개를 떠올려보세요. 이렇게 하면 더 자신감 있게 말할 수 있어요.",
                "자신이 말한 내용을 녹음해서 들어보세요. 스스로 개선점을 찾는 것도 훌륭한 학습 방법입니다."
            ]
        )
