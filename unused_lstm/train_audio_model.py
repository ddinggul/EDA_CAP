"""
음성 특징 기반 발음/유창성 평가 모델
LSTM을 사용한 회귀 모델
"""

import numpy as np
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path
from typing import Dict, Tuple


class AudioFeaturesDataset(Dataset):
    """음성 특징 데이터셋"""

    def __init__(self, features, labels, scaler=None):
        self.features = features
        self.labels = labels

        # 특징 정규화
        if scaler is None:
            self.scaler = StandardScaler()
            self.features = self.scaler.fit_transform(features)
        else:
            self.scaler = scaler
            self.features = self.scaler.transform(features)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return (
            torch.FloatTensor(self.features[idx]),
            torch.FloatTensor(self.labels[idx])
        )


class AudioEvaluationModel(nn.Module):
    """
    음성 특징 기반 평가 모델
    발음, 유창성 점수 예측
    """

    def __init__(self, input_dim: int, hidden_dim: int = 128, num_layers: int = 2):
        super().__init__()

        # LSTM 레이어
        self.lstm = nn.LSTM(
            input_dim,
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=0.3 if num_layers > 1 else 0
        )

        # Fully connected layers
        self.fc_layers = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 2)  # 발음, 유창성 점수 (0-4)
        )

    def forward(self, x):
        # x shape: (batch, features)
        # LSTM 입력을 위해 차원 추가: (batch, seq_len=1, features)
        x = x.unsqueeze(1)

        # LSTM
        lstm_out, (hidden, cell) = self.lstm(x)

        # 마지막 hidden state 사용
        output = self.fc_layers(hidden[-1])

        return output


def prepare_dataset_from_jsonl(jsonl_path: str) -> Tuple:
    """
    JSONL에서 데이터 로드 및 전처리

    Returns:
        features: numpy array of audio features
        labels: numpy array of [pronunciation_score, fluency_score]
    """

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]

    features_list = []
    labels_list = []

    for item in data:
        # 음성 특징 추출 (숫자형만)
        audio_features = item['audio_features']

        feature_vector = []
        for key, value in audio_features.items():
            if isinstance(value, list):
                feature_vector.extend(value)
            elif isinstance(value, (int, float)):
                feature_vector.append(value)

        # 레이블: 발음, 유창성 점수
        # 텍스트 점수를 숫자로 변환 (필요시)
        try:
            pronunciation = float(item['ground_truth'].get('total_score', 0))
            fluency = float(item['ground_truth'].get('total_score', 0))
            # TODO: 실제로는 발음/유창성 점수가 별도로 있어야 함
        except:
            continue

        features_list.append(feature_vector)
        labels_list.append([pronunciation, fluency])

    features = np.array(features_list)
    labels = np.array(labels_list)

    print(f"✅ 데이터 로드 완료")
    print(f"   특징 차원: {features.shape}")
    print(f"   레이블 차원: {labels.shape}")

    return features, labels


def train_audio_model(
    jsonl_path: str,
    output_dir: str = "./audio_model",
    epochs: int = 100,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
):
    """
    음성 평가 모델 학습

    Args:
        jsonl_path: 음성 특징 JSONL 파일
        output_dir: 모델 저장 디렉토리
        epochs: 학습 에포크
        batch_size: 배치 크기
        learning_rate: 학습률
        device: cuda or cpu
    """

    Path(output_dir).mkdir(exist_ok=True)

    print("=" * 60)
    print("음성 평가 모델 학습")
    print("=" * 60)
    print(f"디바이스: {device}")
    print()

    # 데이터 로드
    features, labels = prepare_dataset_from_jsonl(jsonl_path)

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, random_state=42
    )

    # 데이터셋 생성
    train_dataset = AudioFeaturesDataset(X_train, y_train)
    test_dataset = AudioFeaturesDataset(X_test, y_test, scaler=train_dataset.scaler)

    # DataLoader
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    # 모델 초기화
    input_dim = features.shape[1]
    model = AudioEvaluationModel(input_dim=input_dim, hidden_dim=128, num_layers=2)
    model = model.to(device)

    # Loss & Optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=10
    )

    print(f"모델 아키텍처:")
    print(model)
    print()

    # 학습
    best_loss = float('inf')

    for epoch in range(epochs):
        # Train
        model.train()
        train_loss = 0.0

        for features_batch, labels_batch in train_loader:
            features_batch = features_batch.to(device)
            labels_batch = labels_batch.to(device)

            # Forward
            outputs = model(features_batch)
            loss = criterion(outputs, labels_batch)

            # Backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        train_loss /= len(train_loader)

        # Validation
        model.eval()
        test_loss = 0.0

        with torch.no_grad():
            for features_batch, labels_batch in test_loader:
                features_batch = features_batch.to(device)
                labels_batch = labels_batch.to(device)

                outputs = model(features_batch)
                loss = criterion(outputs, labels_batch)
                test_loss += loss.item()

        test_loss /= len(test_loader)

        # Learning rate scheduling
        scheduler.step(test_loss)

        # 출력
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] "
                  f"Train Loss: {train_loss:.4f} | "
                  f"Test Loss: {test_loss:.4f}")

        # 최고 모델 저장
        if test_loss < best_loss:
            best_loss = test_loss
            torch.save(model.state_dict(), f"{output_dir}/best_model.pth")

    print()
    print(f"✅ 학습 완료!")
    print(f"   최고 Test Loss: {best_loss:.4f}")

    # Scaler 저장
    with open(f"{output_dir}/scaler.pkl", 'wb') as f:
        pickle.dump(train_dataset.scaler, f)

    # 모델 메타정보 저장
    metadata = {
        'input_dim': input_dim,
        'hidden_dim': 128,
        'num_layers': 2,
        'best_loss': best_loss
    }

    with open(f"{output_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"💾 모델 저장: {output_dir}/")

    return model, train_dataset.scaler


def predict_audio_scores(
    audio_features: np.ndarray,
    model_dir: str = "./audio_model",
    device: str = "cpu"
) -> Dict:
    """
    학습된 모델로 발음/유창성 점수 예측

    Args:
        audio_features: 음성 특징 벡터
        model_dir: 모델 디렉토리
        device: cuda or cpu

    Returns:
        {'pronunciation': float, 'fluency': float}
    """

    # 메타데이터 로드
    with open(f"{model_dir}/metadata.json", 'r') as f:
        metadata = json.load(f)

    # 모델 로드
    model = AudioEvaluationModel(
        input_dim=metadata['input_dim'],
        hidden_dim=metadata['hidden_dim'],
        num_layers=metadata['num_layers']
    )
    model.load_state_dict(torch.load(f"{model_dir}/best_model.pth", map_location=device))
    model = model.to(device)
    model.eval()

    # Scaler 로드
    with open(f"{model_dir}/scaler.pkl", 'rb') as f:
        scaler = pickle.load(f)

    # 특징 정규화
    features_scaled = scaler.transform(audio_features.reshape(1, -1))
    features_tensor = torch.FloatTensor(features_scaled).to(device)

    # 예측
    with torch.no_grad():
        scores = model(features_tensor)
        scores = scores.cpu().numpy()[0]

    return {
        'pronunciation': float(scores[0]),
        'fluency': float(scores[1])
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='음성 평가 모델 학습')
    parser.add_argument('--data', type=str, required=True,
                        help='음성 특징 JSONL 파일')
    parser.add_argument('--output', type=str, default='./audio_model',
                        help='모델 저장 디렉토리')
    parser.add_argument('--epochs', type=int, default=100,
                        help='학습 에포크')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='배치 크기')
    parser.add_argument('--lr', type=float, default=0.001,
                        help='학습률')

    args = parser.parse_args()

    if Path(args.data).exists():
        train_audio_model(
            jsonl_path=args.data,
            output_dir=args.output,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr
        )
    else:
        print(f"❌ 파일을 찾을 수 없습니다: {args.data}")
        print("먼저 audio_feature_extraction.py를 실행하세요.")
