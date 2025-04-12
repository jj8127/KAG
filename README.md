# 지식 통합 기반 질의 응답에서의 RAG, AutoRAG, KAG 성능 비교 분석

## 📌 개요

본 저장소는 **RAG(Retrieval Augmented Generation)**, **AutoRAG**, **KAG(Knowledge-Augmented Generation)**의 성능을 지식 통합 기반 질의 응답 환경에서 비교 분석한 연구를 구현한 코드와 관련 자료를 제공합니다.  
동서울대학교 컴퓨터소프트웨어과와 컴퓨터정보보안과 연구팀에서 수행한 이 연구는 특히 **2WikiMultiHopQA와 HotpotQA 데이터셋**을 활용하여 다양한 평가 지표를 기준으로 각 모델의 특성을 비교 분석하였습니다.

---

## 🎯 연구 배경 및 목표

RAG 기법은 LLM의 환각 현상을 해결하기 위해 주목받고 있으나, 논리적 추론 및 복잡한 질의 유형에 한계가 있습니다.  
이에 본 연구는 AutoRAG와 KAG의 성능을 비교 분석하여, **엄격한 정답 요구와 복잡한 논리·수치적 추론을 요구하는 질의에 대한 해결 방안**을 제시하고자 합니다.

---

## ⚙ 시스템 구성

### 🔹 AutoRAG 구조

AutoRAG는 **자동 최적화 기법**을 사용하여 RAG 파이프라인의 최적 구성을 자동으로 탐색하는 시스템입니다.

- 원본 문서를 파싱하여 생성된 QA 데이터를 기반으로 다양한 **검색 기법 및 프롬프트 조합을 평가**합니다.
- 최적의 파이프라인 구성을 자동 선택합니다.
- 본 연구에서는 2WikiMultiHopQA와 HotpotQA 각각에 대해 **GPT-4o로 1,000개의 최적화용 QA 데이터를 생성**하여 파이프라인 최적화를 수행했습니다.

![그림1](https://github.com/user-attachments/assets/439162fd-c52b-4674-aff1-4882f84d601c)

---

### 🔹 KAG 구조

KAG는 **지식 그래프(KG)를 기반**으로 구조화된 정보와 논리적 관계를 명확하게 표현하여 **복잡한 질의에 효과적으로 대응**할 수 있도록 설계된 시스템입니다.

**주요 구성요소:**

- **LLM Friendly Representation**: 계층적으로 구성된 정보를 LLM이 처리하기 쉬운 형태로 변환
- **Mutual Index Builder**: 원본 문서와 KG 간의 쌍방향 인덱스 구축
- **Logical Form Solver**: 질의를 논리형식으로 변환 후 문제 해결 수행 (Planning → Retrieval & Reasoning → Generation)
- **Knowledge Alignment**: KG 내 불일치 해소 및 결과 일관성 유지
- **KAG-Model**: NLU/NLI/NLG 향상을 위한 추가 훈련 (본 연구에서는 미적용)

![그림2](https://github.com/user-attachments/assets/8977e8e9-9c6b-4f0b-99d0-b2c18ba074a3)

---

## 🧪 실험 환경

- **GPU**: NVIDIA V100 32GB × 4  
- **Base Model**: DeepSeek-R1-Distill-Llama-8B (Llama-3.1-8B Distilled)  
- **평가 데이터셋**: 2WikiMultiHopQA (395개), HotpotQA  
- **평가 지표**: EM, Relaxed EM, F1, Answer Similarity (GPT-4o 기반)

---

## 📊 결과 요약

### 🔸 2WikiMultiHopQA 평가 결과

- **AutoRAG**: EM 지표 및 **Bridge Comparison** 유형에서 우수
- **KAG**: Relaxed EM, F1, Answer Similarity 및 **Comparison, Compositional** 유형에서 탁월

![그림3](https://github.com/user-attachments/assets/86371b2e-e691-4fb2-9c7e-9647f4491520)  
![그림4](https://github.com/user-attachments/assets/ba215744-4b95-435c-bc37-e98f7c99ac68)

---

### 🔸 HotpotQA 평가 결과

- **AutoRAG**: EM 지표에서 우세
- **KAG**: Relaxed EM, Answer Similarity에서 강점

![그림5](https://github.com/user-attachments/assets/686842d4-2483-4a20-b21b-178546ed85c6)  
![그림6](https://github.com/user-attachments/assets/9e73efc8-eccc-4fd9-bc91-b7e07980d3d7)

---

## ✅ 최종 결과 및 시사점

- **AutoRAG**는 최적화 기반 정답 표현의 정확성에서 우수하며 **EM 지표와 Bridge Comparison** 유형에 특히 강력
  - GPT-4o 기반 대규모 최적화 데이터를 바탕으로 **가장 효과적인 Retriever 구성**을 선택
  - **중개 정보**의 단계적 검색을 통해 우수한 성능 달성
- **KAG**는 **논리·수치적 추론** 능력 덕분에 Relaxed EM, F1, Answer Similarity에서 뛰어남
  - KG 기반의 **명확한 논리적 정보 처리 능력**이 강점
  - **Comparison 및 Compositional 질의 유형**에 특화된 성능

> 두 접근법은 **상호 보완적**이며, 향후에는 **AutoRAG와 KAG의 장점을 결합한 차세대 RAG 시스템 설계**가 매우 유망함을 시사합니다.

---

## 🛠 사용 방법

본 저장소의 코드와 설정을 통해 **AutoRAG와 KAG 모델을 직접 테스트하고 성능 비교**를 수행할 수 있습니다.
