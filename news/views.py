from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import joblib
import numpy as np
import io
from django.http import HttpResponse

class HelloAPI(APIView):
    def post(self, request):
        # POST 요청에서 URL을 가져옴
        url = request.data.get('url')
        
        if not url:
            return Response({"error": "URL이 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # CSV 파일 경로 설정
        file_path = '/home/ubuntu/filtered_dataset.csv'
        filtered_dataset_df = pd.read_csv(file_path)
        
        # 웹 페이지 가져오기
        response = requests.get(url)
        if response.status_code != 200:
            return Response({"error": "웹 페이지를 가져오는 데 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # id가 'title_area'인 h2 요소 추출
        article_title = soup.find('h2', {'id': 'title_area'})
        if article_title:
            span_text = article_title.find('span').text
        else:
            span_text = "제목을 찾을 수 없습니다."
        
        # id가 'newsct_article'인 div 요소 추출
        article = soup.find('div', {'id': 'newsct_article'})
        if article is None:
            return Response({"error": "기사 내용을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 기사 본문 텍스트 추출
        article_text = article.get_text(separator='\n', strip=True)
        
        # 혐의가 들어간 문장 추출
        sentences = article_text.split('.')

        tfidf_vectorizer_path = '/home/ubuntu/tfidf_vectorizer.pkl'
        tfidf_vectorizer = joblib.load(tfidf_vectorizer_path)

        svm_model_path = '/home/ubuntu/svm_model.joblib'
        svm_model = joblib.load(svm_model_path)

        vectorized_sentence = tfidf_vectorizer.transform([span_text])

        prediction = svm_model.predict(vectorized_sentence)
        
        charges = []
        charges2=[]
        tvalue=0
        tindex=[]

        for sentence in sentences:
            if '혐의' in sentence:
                charges2.append(sentence)
                sentence = sentence.strip()
                if re.search(r'(에게|[은는이가])', sentence):
                    end_idx = sentence.index('혐의')
                    charges.append(sentence[:end_idx])

         # 혐의가 들어간 문장에서 '혐의'가 나오기 전 문장으로 추출
        charges_before = []
        original_sentences = []
        for sentence in charges:
            tvalue+=1
            words = re.split(r'\s+', sentence)
            extract = False
            extracted_sentence = ""
            last_josa_idx = -1

            # '은/는/이/가/에게'의 마지막 위치를 찾음
            for i, word in enumerate(words):
                if re.search(r'(은|는|이|가|에게)$', word):
                    last_josa_idx = i

            # 마지막 조사 이후부터 '혐의'가 나오기 전까지 추출
            if last_josa_idx != -1:
                for word in words[last_josa_idx + 1:]:
                    extracted_sentence += word + " "
                    if '혐의' in word:
                        extracted_sentence = extracted_sentence.replace('혐의', '')
                        break
            else:
                for word in words:
                    extracted_sentence += word + " "
                    if '혐의' in word:
                        extracted_sentence = extracted_sentence.replace('혐의', '')
                        break
            if extracted_sentence:
                tindex.append(tvalue-1)
                charges_before.append(extracted_sentence)
                original_sentences.append(sentence)

        corrected_charges_before = []
        for original, extracted in zip(original_sentences, charges_before):
            start_idx = original.find(extracted[:2])  # charges_before의 처음 두 글자 찾기
            if start_idx != -1:
                corrected_sentence = original[start_idx:]  # 일치하는 위치에서부터 자르기
                corrected_charges_before.append(corrected_sentence.strip())
            else:
                corrected_charges_before.append(extracted.strip())
        corrected_charges_before = [sentence.replace(",", " ") for sentence in corrected_charges_before]
        split_sentences = []
        for sentence in corrected_charges_before:
            words = re.split(r'[ ,\(\)·]', sentence)
            split_sentences.append([word for word in words if word])

        # 1글자 단어를 제외한 리스트 생성
        filtered_split_sentences = [[word for word in sentence if len(word) > 1] for sentence in split_sentences]

        filtered_nouns_sentences = []
        for sentence in filtered_split_sentences:
            nouns = []
            for word in sentence:
                nouns += [noun for noun in okt.nouns(word)]
            filtered_nouns_sentences.append(nouns)
        filtered_nouns_sentences = [[word for word in sentence if len(word) > 1] for sentence in filtered_nouns_sentences]

        matche=[]
        for lis in filtered_nouns_sentences:
            a=0
            for words in lis:
                if filtered_dataset_df['사건명'].str.contains(words).any():
                    a+=1
            matche.append(a)
        max_match_index=matche.index(max(matche))

        corrected_sentence = charges2[tindex[max_match_index]].replace('\n', '')

        matching_cases = filtered_dataset_df[
            filtered_dataset_df['사건명'].apply(lambda x: any(word in x for sentence in filtered_split_sentences for word in sentence)) &
            (filtered_dataset_df['분류'] == prediction[0])
        ]

        def convert_sentence_to_numeric(value):
            if value == '무기징역':
                return -1
            elif value == '사형':
                return -2
            elif value == 'None' or value == 'NaN':
                return 0
            else:
                return pd.to_numeric(value, errors='coerce')
        
        matching_cases['징역(개월)'] = matching_cases['징역(개월)'].apply(convert_sentence_to_numeric).fillna(0)
        matching_cases['집행유예(개월)'] = matching_cases['집행유예(개월)'].apply(convert_sentence_to_numeric).fillna(0)
        matching_cases['벌금'] = matching_cases['벌금'].fillna(0)

        matching_cases = matching_cases[~((matching_cases['징역(개월)'] == 0) & (matching_cases['집행유예(개월)'] == 0) & (matching_cases['벌금'] == 0))]

        # 판결 유형 존재 여부 열 추가
        matching_cases['징역'] = matching_cases['징역(개월)'].apply(lambda x: 1 if float(x) > 0 else 0)
        matching_cases['집행유예'] = matching_cases['집행유예(개월)'].apply(lambda x: 1 if float(x) > 0 else 0)
        matching_cases['벌금1'] =matching_cases['벌금'].apply(lambda x: 1 if float(x) > 0 else 0)

        total=len(matching_cases)
        # 판결 유형별 빈도 계산
        total_count = len(matching_cases)
        jail_count = matching_cases['징역'].sum()
        probation_count = matching_cases['집행유예'].sum()
        fine_count = matching_cases['벌금1'].sum()

        # 백분율 계산
        jail_percentage = (jail_count / total_count) * 100
        probation_percentage = (probation_count / total_count) * 100
        fine_percentage = (fine_count / total_count) * 100

        matching_cases['징역(년)'] = matching_cases['징역(개월)'] / 12
        if -2 in matching_cases['징역(개월)'].values:
            highest_sentence = "사형"
        elif -1 in matching_cases['징역(개월)'].values:
            highest_sentence = "무기징역"
        else:
            highest_sentence_years = matching_cases['징역(년)'].max()
            highest_sentence = f"{int(highest_sentence_years)}년"

        bins = np.arange(0, matching_cases['징역(년)'].max() + 1, 1)
        hist, bin_edges = np.histogram(matching_cases['징역(년)'], bins=bins)

        # 가장 높은 빈도의 년도 구간 찾기
        max_bin_index = np.argmax(hist)
        max_bin_start = bin_edges[max_bin_index]
        max_bin_end = bin_edges[max_bin_index + 1]
        max_bin_count = hist[max_bin_index]

        total_count = len(matching_cases)
        max_bin_percentage = int((max_bin_count / total_count) * 100)
        result_string = f"{int(max_bin_start)}~{int(max_bin_end)}년"


        jail_mean = matching_cases['징역(개월)'].mean()
        probation_mean = matching_cases['집행유예(개월)'].mean()
        fine_mean = matching_cases['벌금'].mean()


        # 응답 데이터 구성
        response_data = {
            "prediction": prediction[0],
            "article_title": span_text,
            "total": total,
            "jail_percentage": jail_percentage,
            "probation_percentage": probation_percentage,
            "fine_percentage": fine_percentage,
            "max_bin_percentage": max_bin_percentage,
            "result_string": result_string,
            "jail_mean": jail_mean,
            "probation_mean": probation_mean,
            "fine_mean": fine_mean
        }
        csv_buffer = io.StringIO()
        matching_cases.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        response = HttpResponse(csv_buffer, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=matching_cases.csv'
        response.write(csv_buffer.getvalue())

        return Response({
            "data": response_data,
            "csv": response.content
        }, status=status.HTTP_200_OK)


            






        
       