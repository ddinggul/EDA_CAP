"""
HuggingFace 모델 파인튜닝 스크립트
Llama, Mistral, Gemma 등의 오픈소스 모델을 파인튜닝
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
import json


def load_and_prepare_data(jsonl_path: str, tokenizer):
    """학습 데이터 로드 및 전처리"""
    print(f"📂 데이터 로딩: {jsonl_path}")

    # JSONL 파일 로드
    dataset = load_dataset('json', data_files=jsonl_path, split='train')

    def tokenize_function(examples):
        # 텍스트를 토큰화
        return tokenizer(
            examples['text'],
            truncation=True,
            max_length=1024,
            padding='max_length'
        )

    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )

    return tokenized_dataset


def setup_lora_config():
    """LoRA 설정 (효율적인 파인튜닝)"""
    return LoraConfig(
        r=16,  # LoRA rank
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Llama/Mistral 기준
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )


def fine_tune_model(
    model_name: str = "meta-llama/Llama-2-7b-chat-hf",
    training_data_path: str = "training_data_huggingface.jsonl",
    output_dir: str = "./toefl_finetuned_model"
):
    """
    HuggingFace 모델 파인튜닝

    Args:
        model_name: 베이스 모델 이름
            - "meta-llama/Llama-2-7b-chat-hf" (권장)
            - "mistralai/Mistral-7B-Instruct-v0.2"
            - "google/gemma-7b-it"
        training_data_path: 학습 데이터 경로
        output_dir: 모델 저장 경로
    """

    print("=" * 60)
    print(f"HuggingFace 모델 파인튜닝: {model_name}")
    print("=" * 60)

    # 1. 토크나이저 로드
    print("\n📥 토크나이저 로딩...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # 2. 모델 로드 (4bit 양자화로 메모리 절약)
    print("\n📥 모델 로딩...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        load_in_4bit=True,  # 4bit 양자화 (메모리 절약)
        torch_dtype=torch.float16,
        device_map="auto"
    )

    # 3. LoRA 설정 적용
    print("\n⚙️  LoRA 설정 적용...")
    model = prepare_model_for_kbit_training(model)
    lora_config = setup_lora_config()
    model = get_peft_model(model, lora_config)

    model.print_trainable_parameters()

    # 4. 데이터 로드
    train_dataset = load_and_prepare_data(training_data_path, tokenizer)

    # 5. 학습 설정
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_strategy="epoch",
        warmup_steps=100,
        report_to="none"
    )

    # 6. Trainer 설정
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )

    # 7. 학습 시작
    print("\n🚀 파인튜닝 시작...")
    trainer.train()

    # 8. 모델 저장
    print(f"\n💾 모델 저장: {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("\n✅ 파인튜닝 완료!")
    return model, tokenizer


def test_model(model_path: str, test_text: str):
    """파인튜닝된 모델 테스트"""
    print("\n🧪 모델 테스트 중...")

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        load_in_4bit=True,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    prompt = f"""<|system|>
당신은 TOEFL 스피킹 평가 전문가입니다.
<|user|>
다음 학생의 답변을 평가해주세요:

{test_text}
<|assistant|>
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("\n평가 결과:")
    print(result)
    return result


if __name__ == "__main__":
    # 파인튜닝 실행
    # 주의: GPU 필요 (Google Colab 무료 GPU 사용 가능)

    model, tokenizer = fine_tune_model(
        model_name="meta-llama/Llama-2-7b-chat-hf",  # 또는 다른 모델
        training_data_path="training_data_huggingface.jsonl",
        output_dir="./toefl_finetuned_model"
    )

    # 테스트
    test_text = """University announce new policy of energy saving plan.
In the listening conversation, woman disagree..."""

    test_model("./toefl_finetuned_model", test_text)
