# 📰사건·사고 뉴스 분석

## 🚫문제 정의
온라인 뉴스에서 사건·사고 기사를 읽는 상당수 독자들은 범죄자의 형량에 대해 솜방망이 처벌을 받는다고 느낀다. 솜방망이 처벌이란 저지른 잘못에 합당한 처벌을 내리지 않고 약하게 처벌하는 것이다. 실제 뉴스 독자들은 주관적이고 편향된 시각과 법률 분야의 어려운 진입장벽으로 인해 합당한 처벌 수위를 알지 못한 채 범죄자의 판결에 대해 단순히 낮은 처벌을 받았다고 치부한다.

판결은 여론의 영향이 일부 반영될 수 있기 때문에 수사·기소 단계에서 해당 사건이 기사화된다면 범죄자의 혐의에 대해 극단적인 형량과 무조건적인 비난이 아닌 안정적인 사법체계 구축을 위해 법률로써 정의된 데이터와 올바른 법의식에 기반한 의견 표출이 필요하다.

## 🌎수행 방법
뉴스 기사와 유사한 판결문을 가져오기 위해 검색(필터링) 과정을 거친다. 
#### 1. 사건 대분류
선행 되어야 할 것은 분류 모델 훈련을 위한 뉴스 제목 데이터와 Label값 준비 과정이 필요하다. 
#### 2. 혐의 및 형량 추출
혐의를 대표하는 대표 문장을 추출한 다음 판결문 데이터에서 상세 검색을 통해 혐의를 나타내는 단어 리스트를 생성한다. 
#### 3. 데이터 시각화 및 결론 도출
모든 혐의와 일치하는 사건명을 가진 판결문을 가져온 다음 시각화 및 형량 비교 분석을 수행한다. 

## 데모 영상


## 결론
+ 뉴스 기사의 혐의와 정확히 일치한 판결문 도출
+ 판결 분포와 자세한 형량 데이터 시각화
+ 높은 비율을 차지하는 판결의 형량 단위 최빈값 도출  

## 향후 연구
+ 뉴스 대분류 모델 성능 향상 필요
+ 처벌 수위에 대한 다변수 통계학적 알고리즘 연구 필요
+ 사건의 발단,문맥에 대한 유사성 알고리즘 추가 
