그# 📝 문제 추가 가이드

TOEFL Speaking 문제를 시스템에 추가하는 방법입니다.

---

## 📍 문제 파일 위치

```
backend/app/data/questions.json
```

이 파일에 모든 문제가 JSON 형식으로 저장되어 있습니다.

---

## 📋 문제 구조

### Part 2 (Independent Speaking) 문제 형식

```json
{
  "id": "part2_q4",
  "part": 2,
  "questionNumber": 4,
  "type": "Independent Speaking",
  "title": "문제 제목 (간단히)",
  "question": "실제 문제 텍스트를 여기에 작성합니다...",
  "preparationTime": 15,
  "responseTime": 45,
  "sampleResponse": "모범 답변 예시를 작성합니다...",
  "tips": [
    "팁 1",
    "팁 2",
    "팁 3"
  ]
}
```

### Part 3 (Integrated Speaking) 문제 형식

```json
{
  "id": "part3_q4",
  "part": 3,
  "questionNumber": 4,
  "type": "Integrated Speaking",
  "title": "문제 제목 (간단히)",
  "reading": "읽기 지문을 여기에 작성합니다...",
  "conversation": "대화문을 여기에 작성합니다...",
  "lecture": "강의문을 여기에 작성합니다...",
  "audioFile": "/static/audio/part3/q4_conversation.wav",
  "question": "실제 문제 텍스트를 여기에 작성합니다...",
  "preparationTime": 30,
  "responseTime": 60,
  "sampleResponse": "모범 답변 예시를 작성합니다...",
  "tips": [
    "팁 1",
    "팁 2",
    "팁 3"
  ]
}
```

---

## 📝 필드 설명

### 필수 필드

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `id` | string | 고유 ID (part{파트번호}_q{문제번호}) | `"part2_q4"` |
| `part` | number | 파트 번호 (2 또는 3) | `2` |
| `questionNumber` | number | 문제 번호 | `4` |
| `type` | string | 문제 유형 | `"Independent Speaking"` |
| `title` | string | 문제 제목 | `"취미 선택"` |
| `question` | string | 실제 문제 내용 | `"Do you prefer..."` |
| `preparationTime` | number | 준비 시간 (초) | `15` |
| `responseTime` | number | 응답 시간 (초) | `45` |

### 선택 필드

| 필드 | 타입 | 설명 | 사용 |
|------|------|------|------|
| `reading` | string | 읽기 지문 | Part 3만 |
| `conversation` | string | 대화문 | Part 3만 |
| `lecture` | string | 강의문 | Part 3만 |
| `audioFile` | string | 오디오 파일 경로 | Part 3만 |
| `sampleResponse` | string | 모범 답변 | 선택 |
| `tips` | string[] | 팁 목록 | 선택 |

---

## 🔢 시간 설정 가이드

### Part 2 (Independent Speaking)
- **준비 시간**: `15`초
- **응답 시간**: `45`초

### Part 3 (Integrated Speaking)
- **준비 시간**: `20-30`초 (문제 유형에 따라)
- **응답 시간**: `60`초

---

## 🎵 Part 3 오디오 파일 관리

### 오디오 파일 디렉토리 구조

```
backend/app/static/audio/
└── part3/
    ├── q1_conversation.wav
    ├── q2_lecture.wav
    ├── q3_lecture.wav
    └── ...
```

### 오디오 파일 추가 방법

#### 1단계: WAV 파일 준비
- **형식**: WAV (`.wav`)
- **권장 품질**: 16-bit, 44.1kHz 이상
- **길이**: 실제 TOEFL 시험과 유사하게 (약 1-2분)

#### 2단계: 파일 명명 규칙

```
q{문제번호}_{타입}.wav

예시:
- q1_conversation.wav  (문제 1번, 대화)
- q2_lecture.wav       (문제 2번, 강의)
- q3_conversation.wav  (문제 3번, 대화)
```

#### 3단계: 파일 저장 위치

오디오 파일을 아래 경로에 저장:
```
backend/app/static/audio/part3/
```

파일 복사 예시:
```bash
# 터미널에서
cp 내파일.wav backend/app/static/audio/part3/q4_conversation.wav

# 또는 직접 디렉토리에 파일 복사
```

#### 4단계: questions.json에 경로 추가

Part 3 문제에 `audioFile` 필드 추가:

```json
{
  "id": "part3_q4",
  "part": 3,
  "questionNumber": 4,
  "type": "Integrated Speaking",
  "title": "도서관 운영 시간 변경",
  "reading": "...",
  "conversation": "...",
  "audioFile": "/static/audio/part3/q4_conversation.wav",
  "question": "...",
  "preparationTime": 30,
  "responseTime": 60
}
```

**중요**: `audioFile` 경로는 항상 `/static/audio/part3/`로 시작해야 합니다.

### 오디오 파일 테스트

#### 1. 파일이 제대로 서빙되는지 확인

브라우저에서 직접 접속:
```
http://localhost:8000/static/audio/part3/q1_conversation.wav
```

정상적으로 오디오가 재생되어야 합니다.

#### 2. 시험 페이지에서 확인

1. 프론트엔드 실행: `http://localhost:5173`
2. Part 3 문제 선택
3. "시작하기" 클릭
4. Reading 단계 완료 후 Listening 단계에서 오디오 플레이어 확인
5. 재생 버튼을 눌러 음원이 정상적으로 재생되는지 테스트

### 오디오 파일 제작 팁

#### Conversation (대화) 음원
- 2명의 화자 (보통 남학생과 여학생)
- 자연스러운 대화 속도
- 명확한 발음
- 실제 캠퍼스 상황 반영

#### Lecture (강의) 음원
- 교수 목소리로 녹음
- 학술적이지만 이해하기 쉬운 내용
- 예시와 설명 포함
- 2-3분 길이

### 오디오 녹음 도구 추천

**무료 도구**:
- **Audacity**: 오픈소스 오디오 편집 프로그램
- **GarageBand** (Mac): 고품질 녹음 가능
- **Voice Recorder** (Windows): 기본 녹음 앱

**온라인 TTS (Text-to-Speech)**:
- **Google Cloud TTS**: 자연스러운 음성
- **Amazon Polly**: 다양한 목소리 선택
- **ElevenLabs**: AI 기반 고품질 음성

### 문제 해결

#### 오디오가 재생되지 않을 때

1. **파일 경로 확인**
   ```json
   "audioFile": "/static/audio/part3/q4_conversation.wav"
   ```
   - 절대 경로 사용 (`/`로 시작)
   - 파일명 철자 확인

2. **파일 존재 확인**
   ```bash
   ls backend/app/static/audio/part3/
   ```

3. **파일 형식 확인**
   - WAV 형식인지 확인
   - 파일이 손상되지 않았는지 확인

4. **백엔드 재시작**
   ```bash
   # Ctrl+C로 종료 후
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## 💡 문제 추가 단계별 가이드

### 1단계: 파일 열기

```bash
# 터미널에서
vim backend/app/data/questions.json

# 또는 VSCode에서
code backend/app/data/questions.json
```

### 2단계: JSON 배열에 추가

기존 배열 `[...]` 안의 마지막 항목 뒤에 콤마(`,`)를 추가하고 새 문제를 작성합니다.

```json
[
  {
    "id": "part2_q1",
    ...
  },
  {
    "id": "part2_q2",
    ...
  },
  {
    "id": "part2_q3",
    ...
  },  // 여기에 콤마 추가!
  {
    "id": "part2_q4",  // 새 문제 시작
    "part": 2,
    ...
  }
]
```

### 3단계: 저장 및 확인

파일을 저장하면 백엔드가 자동으로 재로드됩니다.

브라우저에서 확인:
```
http://localhost:8000/questions/
```

---

## 📖 실전 예제

### 예제 1: Part 2 문제 추가

```json
{
  "id": "part2_q5",
  "part": 2,
  "questionNumber": 5,
  "type": "Independent Speaking",
  "title": "취미 vs 공부",
  "question": "Some people think students should spend most of their time studying, while others believe it's important to have hobbies and interests outside of school. Which view do you agree with? Use specific reasons and examples to support your answer.",
  "preparationTime": 15,
  "responseTime": 45,
  "sampleResponse": "I believe students should have hobbies outside of school. First, hobbies help reduce stress and prevent burnout from constant studying. For example, I play guitar, which helps me relax after long study sessions. Second, hobbies can teach valuable life skills like time management and discipline. Finally, having diverse interests makes students more well-rounded individuals, which can actually help in their academic and professional lives.",
  "tips": [
    "Choose a clear position and explain it",
    "Give 2-3 specific reasons with examples",
    "Connect hobbies to personal growth",
    "Conclude by summarizing your main point"
  ]
}
```

### 예제 2: Part 3 문제 추가

```json
{
  "id": "part3_q4",
  "part": 3,
  "questionNumber": 4,
  "type": "Integrated Speaking",
  "title": "도서관 운영 시간 변경",
  "reading": "Library Announces Extended Hours\n\nStarting next month, the university library will extend its operating hours to remain open 24/7 during exam periods. The administration made this decision based on student surveys indicating high demand for late-night study spaces. The library will hire additional staff and increase security to ensure student safety during overnight hours.",
  "conversation": "Male Student: Hey, did you hear about the library staying open all night during exams?\n\nFemale Student: Yeah! I think it's a great idea.\n\nMale Student: Really? Why?\n\nFemale Student: Well, first of all, I'm a night person. I study better late at night when it's quiet and there are fewer distractions. Having a proper study space available during those hours will really help me. Second, sometimes I have early morning exams and it would be great to study at the library and then go straight to my test without having to go back to my dorm. It'll save time and let me study more efficiently.",
  "question": "The woman expresses her opinion about the library's new extended hours. State her opinion and explain the reasons she gives for holding that opinion.",
  "preparationTime": 30,
  "responseTime": 60,
  "sampleResponse": "The woman supports the library's decision to stay open 24/7 during exam periods. She gives two main reasons. First, she explains that she's a night person who studies better late at night when it's quiet with fewer distractions, so having access to a proper study space during those hours will help her. Second, she mentions that sometimes she has early morning exams, and being able to study at the library all night and go straight to her test without returning to her dorm will save time and allow her to study more efficiently.",
  "tips": [
    "State the woman's opinion clearly at the start",
    "Include both reasons she mentions",
    "Use her specific examples (night person, early exams)",
    "Don't add your own opinion"
  ]
}
```

---

## ⚠️ 주의사항

### JSON 형식 오류 방지

1. **따옴표**: 모든 키와 문자열 값은 큰따옴표(`"`)를 사용
2. **콤마**:
   - 항목 사이에는 콤마 필요
   - 마지막 항목 뒤에는 콤마 없음
3. **중괄호**: 각 문제는 `{ }` 안에 작성
4. **대괄호**: 전체는 `[ ]` 배열 안에 작성

### 잘못된 예시 ❌

```json
{
  "id": 'part2_q4',  // ❌ 작은따옴표
  "part": 2,
  "title": "문제"  // ❌ 마지막에 콤마 없어야 함
  "question": "..."  // ❌ 콤마 필요
}
```

### 올바른 예시 ✅

```json
{
  "id": "part2_q4",
  "part": 2,
  "title": "문제",
  "question": "..."
}
```

---

## 🔍 JSON 유효성 검사

### 온라인 도구

1. **JSONLint**: https://jsonlint.com/
2. **JSON Formatter**: https://jsonformatter.org/

파일 내용을 복사해서 붙여넣으면 오류를 찾아줍니다.

### VSCode 확장

- **Prettier**: 자동 포맷팅
- **JSON Tools**: JSON 검증

---

## 🧪 테스트

### 1. API 테스트

```bash
# 모든 문제 확인
curl http://localhost:8000/questions/

# 특정 문제 확인
curl http://localhost:8000/questions/part2_q4
```

### 2. 프론트엔드에서 확인

1. 브라우저: `http://localhost:5173`
2. "실전 모의고사 시작" 클릭
3. Part와 문제 번호 필터로 새 문제 찾기
4. "시작하기" 클릭하여 테스트

---

## 📊 문제 번호 관리

### 권장 구조

```
Part 2 (Independent Speaking):
- 문제 1번, 2번, 3번, 4번, 5번, ...

Part 3 (Integrated Speaking):
- 문제 1번, 2번, 3번, 4번, 5번, ...
```

### ID 명명 규칙

```
part{파트번호}_q{문제번호}

예시:
- part2_q1  (Part 2, 문제 1번)
- part2_q2  (Part 2, 문제 2번)
- part3_q1  (Part 3, 문제 1번)
- part3_q2  (Part 3, 문제 2번)
```

---

## 🎯 팁 작성 가이드

### Part 2 팁 예시

```json
"tips": [
  "첫 문장에서 명확한 입장 표명하기",
  "2-3개의 구체적인 이유나 예시 제시",
  "개인적인 경험을 활용하기",
  "전환어 사용 (First, Second, Additionally)",
  "마지막에 주요 요점 요약하기"
]
```

### Part 3 팁 예시

```json
"tips": [
  "자신의 의견 X, 들은 내용만 전달",
  "화자의 의견과 이유 모두 포함",
  "구체적인 세부 사항 언급",
  "보고 표현 사용 (she states, he argues)"
]
```

---

## 🔄 백업 및 복구

### 백업

문제 추가 전 백업본 생성:

```bash
cp backend/app/data/questions.json backend/app/data/questions.backup.json
```

### 복구

문제 발생 시 복구:

```bash
cp backend/app/data/questions.backup.json backend/app/data/questions.json
```

---

## 🚀 빠른 시작

### 1분 안에 문제 추가하기

1. `backend/app/data/questions.json` 파일 열기
2. 마지막 문제 뒤에 콤마 추가
3. 아래 템플릿 복사해서 붙여넣기
4. 내용 수정
5. 저장

**Part 2 템플릿**:
```json
,
{
  "id": "part2_qX",
  "part": 2,
  "questionNumber": X,
  "type": "Independent Speaking",
  "title": "제목",
  "question": "문제 내용",
  "preparationTime": 15,
  "responseTime": 45
}
```

**Part 3 템플릿**:
```json
,
{
  "id": "part3_qX",
  "part": 3,
  "questionNumber": X,
  "type": "Integrated Speaking",
  "title": "제목",
  "reading": "읽기 지문",
  "conversation": "대화 내용 (텍스트)",
  "lecture": "강의 내용 (텍스트)",
  "audioFile": "/static/audio/part3/qX_conversation.wav",
  "question": "문제 내용",
  "preparationTime": 30,
  "responseTime": 60
}
```

**주의**: `audioFile`은 실제 WAV 파일을 `backend/app/static/audio/part3/`에 저장한 후에 추가하세요.

---

**문제 추가 후 자동으로 시스템에 반영됩니다!** 🎉

새로고침만 하면 바로 사용할 수 있습니다.
