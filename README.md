# 📰사건·사고 뉴스 분석

## 🚫문제 정의
온라인에서 특정 범죄에 대한 구형 및 판결에 대한 뉴스를 자주 접하게 된다. 일반인은 뉴스에서 다루는 범죄와 해당 범죄에 대한 구형 및 판결이 적절한지 알기 어렵다. 본 연구는 일반인도 특정 범죄에 대한 구형 및 판결이 적절한지 알기 쉽도록 뉴스 기사 텍스트를 기반으로 유사 판례를 검색하고, 그 결과를 시각화하여 사용자의 이해를 돕는 크롬 플러그인 서비스를 개발했다. 이 서비스는 자동화된 유사 판례 검색 기능과 형량 분포 시각화, 빈도 기반 통계적 해석을 제공하여 데이터에 기반한 객관적인 형량 평가를 가능하게 한다. 이를 통해 사용자는 특정 조건의 범죄에 따른 판결 분포를 쉽게 이해하고 법적 일관성을 쉽게 확인할 수 있다.

## 🌎수행 방법
  
#### 1. 판례 데이터 수집 및 전처리
Hugging Face에 공개된 85,659개의 판결문 데이터 를 수집했다. 해당 데이터는 각 판례에 대한 범죄 유형 데이터가 없기 때문에 검찰청 범죄통계표 를 기준으로, 해당 판결문 데이터의 판례의 사건명과 범죄 유형별 핵심 키워드를 매칭해서 78개의 범죄 유형 정보를 추가했다. 판결문의 형량 정보를 정량적으로 분석하기 위해, 정규표현식을 사용하여 판결문의 징역 및 집행유예 정보는 년/월 단위의 숫자로 추출하고 벌금은 원 단위로 추출했다.
#### 2. 범죄 유형 예측 
사전에 구현한 범죄 유형 예측 BERT 모델을 활용해서 사용자가 전송한 뉴스 기사가 어떤 범죄 유형을 다루고 있는지 분류한다. 범죄 유형은 검찰청 범죄통계표에서 분류하고 있는 78개 범죄 유형을 활용했다. 
#### 3. 유사 판례 필터링
한국어 GPT2 모델  을 활용해 뉴스 기사 본문 텍스트를 1500자 이내의 요약문을 생성한다. 그 다음, S-BERT 기반으로 사전 구축한 임베딩을 활용해서 뉴스 기사의 요약문과 코사인 유사도가 0.7 이상인 판례만 필터링한다.
#### 4.분포 시각화 및 결과 텍스트 제공
Highchart.js 라이브러리 를 활용하여 형벌 종류(징역, 집행유예, 벌금)의 분포를 파이 차트로 표현해 전체적인 분포를 파악할 수 있다. 사용자가 형벌 종류 중 하나를 클릭하면, 해당 형벌에 대한 세부 형량을 히스토그램으로 시각화해서 그 분포를 확인할 수 있다. 형량은 징역, 집행유예, 벌금으로 분류된다. 징역과 집행 유예는 연 단위로 분류하고, 벌금은 100만원 단위로 분류해서 히스토그램으로 나타냈다.

## 데모 영상
![1](https://github.com/jeongwwon/SoftwareCapstoneDesign/assets/104192273/767afeda-ec6d-4dc4-b0e7-e16c952103f7)
