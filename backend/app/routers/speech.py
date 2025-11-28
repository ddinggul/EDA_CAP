# backend/app/routers/speech.py
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import SpeechAnalyzeResponse, ErrorResponse
from app.services.clova_stt import transcribe_with_pronunciation_eval
from app.services.openai_eval import evaluate_speaking
from app.utils.audio import convert_to_wav, validate_audio_file

router = APIRouter(prefix="/speech", tags=["speech"])

@router.post("/analyze", response_model=SpeechAnalyzeResponse)
async def analyze_speech(
    file: UploadFile = File(...),
    task_id: int = Form(..., ge=1, le=4)
):
    """
    Analyze uploaded speech audio file.

    Process flow:
    1. Save uploaded file to temp directory
    2. Convert to WAV if needed
    3. Call Naver STT API for transcription
    4. Call Naver Pronunciation API for evaluation
    5. Call OpenAI API for comprehensive evaluation
    6. Return combined results
    """

    temp_file_path = None
    wav_file_path = None

    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        temp_file_path = settings.TEMP_DIR / unique_filename

        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Validate file size
        if not validate_audio_file(temp_file_path, settings.MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )

        # Convert to WAV if necessary
        wav_file_path = convert_to_wav(temp_file_path)

        # Step 1 & 2: CLOVA Speech 단문 인식 API로 STT + 발음 평가 동시 수행
        # - nbestScoreLangEval 파라미터로 발음 점수 함께 반환
        # - 60초 이내 음성에 최적화
        stt_result, pron_result = await transcribe_with_pronunciation_eval(
            wav_file_path,
            language="Eng"  # 영어 음성 인식
        )

        # Step 3: OpenAI Comprehensive Evaluation
        pron_scores = {
            "overall": pron_result.overall,
            "fluency": pron_result.fluency
        }
        eval_result = await evaluate_speaking(task_id, stt_result.text, pron_scores)

        # Combine all results
        response = SpeechAnalyzeResponse(
            task_id=task_id,
            stt=stt_result,
            pronunciation=pron_result,
            evaluation=eval_result
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing speech analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Cleanup temporary files
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as e:
                print(f"Error deleting temp file {temp_file_path}: {e}")

        if wav_file_path and wav_file_path != temp_file_path and wav_file_path.exists():
            try:
                wav_file_path.unlink()
            except Exception as e:
                print(f"Error deleting wav file {wav_file_path}: {e}")

@router.post("/evaluate")
async def evaluate_speech(file: UploadFile = File(...)):
    """
    Evaluate uploaded speech audio file for TOEFL Speaking.

    This endpoint is simpler than /analyze and returns results in a format
    compatible with the frontend ResultsPage.
    """
    temp_file_path = None
    wav_file_path = None

    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        temp_file_path = settings.TEMP_DIR / unique_filename

        # Save uploaded file
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Validate file size
        if not validate_audio_file(temp_file_path, settings.MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes"
            )

        # Convert to WAV if necessary
        wav_file_path = convert_to_wav(temp_file_path)

        # STT + Pronunciation Evaluation
        stt_result, pron_result = await transcribe_with_pronunciation_eval(
            wav_file_path,
            language="Eng"
        )

        # OpenAI Evaluation (using task_id=1 as default)
        pron_scores = {
            "overall": pron_result.overall,
            "fluency": pron_result.fluency
        }
        eval_result = await evaluate_speaking(1, stt_result.text, pron_scores)

        # Return results in frontend-compatible format
        return JSONResponse({
            "speech_recognition": {
                "text": stt_result.text,
                "confidence": stt_result.confidence
            },
            "pronunciation": {
                "score": pron_result.overall,
                "score_4point": pron_result.overall / 25.0  # Convert 0-100 to 0-4
            },
            "fluency": {
                "score": pron_result.fluency,
                "score_4point": pron_result.fluency / 25.0  # Convert 0-100 to 0-4
            },
            "content": {
                "score": eval_result.scores.content,
                "feedback": eval_result.feedback
            },
            "grammar": {
                "score": eval_result.scores.grammar,
                "feedback": eval_result.feedback
            },
            "overall": {
                "score": eval_result.scores.total,
                "feedback": eval_result.feedback
            },
            "gpt_evaluation": eval_result.feedback,
            "tips": eval_result.tips
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing speech evaluation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Cleanup temporary files
        if temp_file_path and temp_file_path.exists():
            try:
                temp_file_path.unlink()
            except Exception as e:
                print(f"Error deleting temp file {temp_file_path}: {e}")

        if wav_file_path and wav_file_path != temp_file_path and wav_file_path.exists():
            try:
                wav_file_path.unlink()
            except Exception as e:
                print(f"Error deleting wav file {wav_file_path}: {e}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "TOEFL Speaking Analysis"}
