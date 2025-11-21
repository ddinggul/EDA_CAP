"""
Flask API 서버 - MLX 파인튜닝된 TOEFL 평가 모델
M2 Mac에서 실행 가능한 REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from pathlib import Path

try:
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # CORS 활성화

# 전역 변수로 모델 저장 (한 번만 로드)
model = None
tokenizer = None
model_loaded = False


def load_model_once(
    model_name: str = "mlx-community/Mistral-7B-Instruct-v0.2-4bit",
    adapter_path: str = "./toefl_finetuned_mlx"
):
    """모델을 한 번만 로드 (서버 시작 시)"""
    global model, tokenizer, model_loaded

    if model_loaded:
        return

    if not MLX_AVAILABLE:
        raise ImportError("MLX가 설치되지 않았습니다: pip install mlx mlx-lm")

    print(f"📥 모델 로딩 중...")
    print(f"   베이스 모델: {model_name}")
    print(f"   어댑터: {adapter_path}")

    start = time.time()

    if Path(adapter_path).exists():
        model, tokenizer = load(model_name, adapter_path=adapter_path)
        print(f"   ✅ 파인튜닝 모델 로드 완료 ({time.time()-start:.1f}초)")
    else:
        print(f"   ⚠️  어댑터를 찾을 수 없습니다. 베이스 모델만 사용합니다.")
        model, tokenizer = load(model_name)
        print(f"   ✅ 베이스 모델 로드 완료 ({time.time()-start:.1f}초)")

    model_loaded = True


def evaluate_toefl_speaking(text: str, max_tokens: int = 500, temp: float = 0.7) -> dict:
    """TOEFL 스피킹 답변 평가"""

    if not model_loaded:
        return {"error": "모델이 로드되지 않았습니다."}

    prompt = f"""<|system|>
당신은 TOEFL 스피킹 평가 전문가입니다. 학생의 답변을 다음 기준으로 평가하세요:

1. 발음 (Pronunciation): 개별 음소의 정확성, R/L 구분, 장단모음
2. 유창성 (Fluency): 말하기 속도, 톤 조절, 자연스러움
3. 내용 (Content): 질문 적합성, 논리적 구조, 구체적 예시
4. 문법/표현 (Grammar): 문법 정확성, 어휘 다양성

각 항목에 대한 구체적 피드백과 총점(0-4점)을 제공하세요.
<|user|>
다음 학생의 답변을 평가해주세요:

{text}
<|assistant|>
"""

    start = time.time()
    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        temp=temp
    )
    inference_time = time.time() - start

    return {
        "evaluation": response,
        "inference_time": f"{inference_time:.2f}초",
        "model_type": "MLX Fine-tuned"
    }


@app.route('/', methods=['GET'])
def home():
    """API 정보"""
    return jsonify({
        "service": "TOEFL Speaking Evaluation API",
        "version": "1.0",
        "model": "MLX on M2 Mac",
        "status": "running" if model_loaded else "loading",
        "endpoints": {
            "/evaluate": "POST - 스피킹 답변 평가",
            "/health": "GET - 서버 상태 확인",
            "/batch": "POST - 여러 답변 일괄 평가"
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """서버 상태 체크"""
    return jsonify({
        "status": "healthy" if model_loaded else "loading",
        "model_loaded": model_loaded,
        "timestamp": time.time()
    })


@app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    단일 답변 평가

    Request:
        {
            "text": "학생의 답변 텍스트",
            "max_tokens": 500,  // 선택
            "temperature": 0.7   // 선택
        }

    Response:
        {
            "evaluation": "평가 결과...",
            "inference_time": "1.23초",
            "model_type": "MLX Fine-tuned"
        }
    """

    try:
        data = request.json

        if not data or 'text' not in data:
            return jsonify({"error": "텍스트가 필요합니다."}), 400

        text = data['text']
        max_tokens = data.get('max_tokens', 500)
        temperature = data.get('temperature', 0.7)

        result = evaluate_toefl_speaking(text, max_tokens, temperature)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/batch', methods=['POST'])
def batch_evaluate():
    """
    여러 답변 일괄 평가

    Request:
        {
            "texts": ["답변1", "답변2", "답변3"],
            "max_tokens": 500,
            "temperature": 0.7
        }

    Response:
        {
            "results": [
                {"text": "답변1", "evaluation": "..."},
                ...
            ],
            "total_time": "5.67초",
            "count": 3
        }
    """

    try:
        data = request.json

        if not data or 'texts' not in data:
            return jsonify({"error": "texts 배열이 필요합니다."}), 400

        texts = data['texts']
        max_tokens = data.get('max_tokens', 500)
        temperature = data.get('temperature', 0.7)

        start = time.time()
        results = []

        for text in texts:
            result = evaluate_toefl_speaking(text, max_tokens, temperature)
            results.append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "evaluation": result["evaluation"]
            })

        total_time = time.time() - start

        return jsonify({
            "results": results,
            "total_time": f"{total_time:.2f}초",
            "count": len(texts),
            "avg_time": f"{total_time/len(texts):.2f}초/개"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reload', methods=['POST'])
def reload_model():
    """모델 재로드 (디버깅용)"""
    global model_loaded
    model_loaded = False

    data = request.json or {}
    model_name = data.get('model_name', "mlx-community/Mistral-7B-Instruct-v0.2-4bit")
    adapter_path = data.get('adapter_path', "./toefl_finetuned_mlx")

    try:
        load_model_once(model_name, adapter_path)
        return jsonify({"status": "모델 재로드 완료"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='TOEFL 평가 API 서버')
    parser.add_argument('--model', type=str,
                        default='mlx-community/Mistral-7B-Instruct-v0.2-4bit',
                        help='베이스 모델 이름')
    parser.add_argument('--adapter', type=str,
                        default='./toefl_finetuned_mlx',
                        help='어댑터 경로')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='서버 호스트')
    parser.add_argument('--port', type=int, default=5000,
                        help='서버 포트')

    args = parser.parse_args()

    print("=" * 60)
    print("🎓 TOEFL 스피킹 평가 API 서버 (MLX on M2)")
    print("=" * 60)
    print()

    # 모델 로드
    load_model_once(args.model, args.adapter)

    print()
    print("=" * 60)
    print(f"🚀 서버 시작: http://{args.host}:{args.port}")
    print("=" * 60)
    print()
    print("API 엔드포인트:")
    print(f"  - POST /evaluate      : 단일 평가")
    print(f"  - POST /batch         : 일괄 평가")
    print(f"  - GET  /health        : 상태 체크")
    print()
    print("예시:")
    print(f"""  curl -X POST http://localhost:{args.port}/evaluate \\
    -H "Content-Type: application/json" \\
    -d '{{"text": "I like reading books..."}}'
""")
    print("종료: Ctrl+C")
    print()

    # 서버 시작
    app.run(host=args.host, port=args.port, debug=False)
