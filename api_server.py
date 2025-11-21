"""
TOEFL 스피킹 평가 API 서버
Clova STT + 발음평가 → 파인튜닝된 OpenAI GPT
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
import tempfile
from toefl_evaluator import TOEFLEvaluator

app = Flask(__name__)
CORS(app)

# 평가 시스템 초기화 (서버 시작 시 한 번만)
evaluator = None


def init_evaluator():
    """평가 시스템 초기화"""
    global evaluator

    if evaluator is not None:
        return

    clova_key = os.getenv('NAVER_CLOVA_SECRET_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    finetuned_model = os.getenv('OPENAI_FINETUNED_MODEL', 'gpt-3.5-turbo')

    if not clova_key:
        raise ValueError("NAVER_CLOVA_SECRET_KEY 환경변수가 필요합니다")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY 환경변수가 필요합니다")

    evaluator = TOEFLEvaluator(
        clova_secret_key=clova_key,
        openai_api_key=openai_key,
        finetuned_model=finetuned_model
    )

    print("✅ API 서버 초기화 완료")


@app.route('/')
def home():
    """API 정보"""
    return jsonify({
        "service": "TOEFL Speaking Evaluation API",
        "version": "2.0",
        "system": "Clova STT + OpenAI GPT",
        "endpoints": {
            "/evaluate": "POST - 음성 파일 평가 (multipart/form-data)",
            "/evaluate_text": "POST - 텍스트만 평가 (JSON)",
            "/health": "GET - 서버 상태 확인"
        }
    })


@app.route('/health')
def health():
    """서버 상태 체크"""
    return jsonify({
        "status": "healthy",
        "clova_api": "configured" if os.getenv('NAVER_CLOVA_SECRET_KEY') else "not configured",
        "openai_api": "configured" if os.getenv('OPENAI_API_KEY') else "not configured",
        "model": os.getenv('OPENAI_FINETUNED_MODEL', 'gpt-3.5-turbo')
    })


@app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    음성 파일 전체 평가

    Request:
        multipart/form-data
        - file: 음성 파일 (WAV, MP3 등)

    Response:
        {
            "speech_recognition": {...},
            "pronunciation": {...},
            "fluency": {...},
            "gpt_evaluation": "..."
        }
    """

    try:
        # 파일 확인
        if 'file' not in request.files:
            return jsonify({"error": "파일이 필요합니다"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "파일을 선택하세요"}), 400

        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name

        # 평가 실행
        result = evaluator.evaluate_complete(temp_path, save_result=False)

        # 임시 파일 삭제
        os.unlink(temp_path)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/evaluate_text', methods=['POST'])
def evaluate_text():
    """
    텍스트만 평가 (음성인식 결과가 이미 있는 경우)

    Request:
        {
            "text": "학생 답변 텍스트",
            "pronunciation_score": 75.5,  // 선택
            "fluency_score": 80.0          // 선택
        }

    Response:
        {
            "evaluation": "..."
        }
    """

    try:
        data = request.json

        if not data or 'text' not in data:
            return jsonify({"error": "텍스트가 필요합니다"}), 400

        transcript = data['text']
        pronunciation_score = data.get('pronunciation_score', 70.0)
        fluency_score = data.get('fluency_score', 70.0)

        # GPT 평가만 실행
        result = evaluator.evaluate_with_gpt(
            transcript=transcript,
            pronunciation_score=pronunciation_score,
            fluency_score=fluency_score
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='TOEFL 평가 API 서버')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='서버 호스트')
    parser.add_argument('--port', type=int, default=5000,
                        help='서버 포트')
    parser.add_argument('--debug', action='store_true',
                        help='디버그 모드')

    args = parser.parse_args()

    print("=" * 60)
    print("🎓 TOEFL 스피킹 평가 API 서버")
    print("=" * 60)
    print()

    # 평가 시스템 초기화
    init_evaluator()

    print()
    print("=" * 60)
    print(f"🚀 서버 시작: http://{args.host}:{args.port}")
    print("=" * 60)
    print()
    print("API 엔드포인트:")
    print(f"  - POST /evaluate       : 음성 파일 평가")
    print(f"  - POST /evaluate_text  : 텍스트만 평가")
    print(f"  - GET  /health         : 상태 체크")
    print()
    print("예시:")
    print(f"""  # 음성 파일 평가
  curl -X POST http://localhost:{args.port}/evaluate \\
    -F "file=@student.wav"

  # 텍스트만 평가
  curl -X POST http://localhost:{args.port}/evaluate_text \\
    -H "Content-Type: application/json" \\
    -d '{{"text": "I prefer studying..."}}'
""")
    print("종료: Ctrl+C")
    print()

    # 서버 시작
    app.run(host=args.host, port=args.port, debug=args.debug)
