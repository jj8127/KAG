# 📚 지식 통합 기반 질의 응답에서의 RAG, AutoRAG, KAG 성능 비교 분석

본 저장소는 **RAG(Retrieval Augmented Generation), AutoRAG, KAG(Knowledge-Augmented Generation)**의 성능을 **지식 통합 기반 질의 응답 환경**에서 비교 분석한 연구를 구현한 코드와 관련 자료를 제공합니다.

> 본 연구는 동서울대학교 **컴퓨터소프트웨어과**와 **컴퓨터정보보안과** 연구팀이 수행하였으며, **2WikiMultiHopQA** 및 **HotpotQA** 데이터셋을 기반으로 다양한 평가 지표를 통해 모델 성능을 비교하였습니다.

---

## 🧠 연구 배경 및 목표

- RAG는 LLM의 **환각(hallucination)** 문제를 해결하는 핵심 기술로 주목받고 있으나, **논리적 추론**과 **복잡한 질의 처리**에 한계를 가짐
- 본 연구는 **AutoRAG**와 **KAG**의 성능을 비교함으로써 **정확한 정답 도출**과 **복잡한 논리·수치 기반 질의 처리**를 위한 새로운 해법을 모색

---

## 🛠️ 시스템 구성

### 🔁 AutoRAG 구조

- **자동 최적화 기법**을 통해 RAG 파이프라인의 **최적 검색 및 생성 구성 자동 탐색**
- GPT-4o를 활용하여 2WikiMultiHopQA와 HotpotQA 각각에 대해 **1,000개 QA 데이터**를 생성, 실험적 최적화 수행  
- 다양한 검색기법과 프롬프트 조합을 시험하여 가장 성능이 높은 파이프라인 도출

![그림1](https://github.com/user-attachments/assets/439162fd-c52b-4674-aff1-4882f84d601c)

---

### 🧭 KAG 구조

- **지식 그래프 기반 시스템**으로, 구조화된 정보와 **논리적 관계 처리**에 최적화
- 복잡한 질의에 강력한 대응이 가능하도록 아래 구성요소 포함:

| 구성 요소 | 설명 |
|-----------|------|
| **LLM Friendly Representation** | 계층적 정보를 LLM이 이해하기 쉬운 형태로 변환 |
| **Mutual Index Builder** | 원문 문서와 KG 간의 **쌍방향 인덱스**를 구성하여 검색 정확도 향상 |
| **Logical Form Solver** | 질의를 논리 형식으로 변환하여 **세 단계(계획 → 검색 및 추론 → 생성)**로 해결 |
| **Knowledge Alignment** | KG 간 불일치를 해결하고 **일관된 검색 결과** 제공 |
| **KAG-Model** | NLU, NLI, NLG 성능 향상을 위한 모듈 *(본 연구에서는 별도 fine-tuning 미수행)* |

![그림2](https://github.com/user-attachments/assets/8977e8e9-9c6b-4f0b-99d0-b2c18ba074a3)

---

## 🧪 실험 환경

- **GPU**: NVIDIA V100 32GB × 4
- **Base Model**: DeepSeek-R1-Distill-Llama-8B (Llama-3.1-8B distilled)
- **데이터셋**: 2WikiMultiHopQA (395개), HotpotQA
- **평가지표**: EM, Relaxed EM, F1, Answer Similarity (GPT-4o 기반)

---

## 📊 실험 결과 요약

### 📌 2WikiMultiHopQA 결과

- **AutoRAG**: EM 및 Bridge Comparison에서 **우수**
- **KAG**: Relaxed EM, F1, Answer Similarity 및 Comparison, Compositional 유형에서 **탁월**

![그림3](https://github.com/user-attachments/assets/86371b2e-e691-4fb2-9c7e-9647f4491520)  
![그림4](https://github.com/user-attachments/assets/ba215744-4b95-435c-bc37-e98f7c99ac68)

---

### 📌 HotpotQA 결과

- **AutoRAG**: EM 지표에서 **우세**
- **KAG**: Relaxed EM, Answer Similarity에서 **강점**

![그림5](https://github.com/user-attachments/assets/686842d4-2483-4a20-b21b-178546ed85c6)  
![그림6](https://github.com/user-attachments/assets/9e73efc8-eccc-4fd9-bc91-b7e07980d3d7)

---

## 📌 최종 결론 및 시사점

- **AutoRAG**는 **정답 표현의 정밀성**을 추구하며 EM 지표와 Bridge Comparison에서 강세  
  → GPT-4o 기반 QA 생성과 최적화된 Retriever 설정이 주요 요인
- **KAG**는 **논리적 추론 및 정보의 핵심 의미 파악**에서 탁월  
  → KG 기반의 정형화된 정보 추론이 핵심 강점

> 🔗 **AutoRAG와 KAG는 상호 보완적이며**, 향후 두 접근을 결합한 차세대 RAG 시스템 설계가 **매우 유망**함을 시사

---

## 🧑‍💻 사용 방법

본 저장소의 코드를 통해 AutoRAG 및 KAG 모델을 직접 실행하고 다음을 수행할 수 있습니다:

1. 데이터셋에 기반한 QA 생성
2. 파이프라인 구성 자동화
3. 성능 비교 평가 (EM, F1, Similarity 등)

---

