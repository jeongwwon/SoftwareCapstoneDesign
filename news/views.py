from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import re
import joblib
import numpy as np
import io
from django.http import HttpResponse


# 전역 변수로 파일 로드
file_path = '/home/ubuntu/filtered_dataset.csv'
tfidf_vectorizer_path = '/home/ubuntu/tfidf_vectorizer.pkl'
svm_model_path = '/home/ubuntu/svm_model.joblib'

try:
    if os.path.exists(file_path):
        filtered_dataset_df = pd.read_csv(file_path)
    else:
        filtered_dataset_df = None

    if os.path.exists(tfidf_vectorizer_path):
        tfidf_vectorizer = joblib.load(tfidf_vectorizer_path)
    else:
        tfidf_vectorizer = None

    if os.path.exists(svm_model_path):
        svm_model = joblib.load(svm_model_path)
    else:
        svm_model = None
except Exception as e:
    print(f"Error loading files: {e}")
    filtered_dataset_df = None
    tfidf_vectorizer = None
    svm_model = None

class HelloAPI(APIView):
    def post(self, request):
        url = request.data.get('url')
        
        if not url:
            return Response({"error": "URL이 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return Response({"error": "웹 페이지를 가져오는 데 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            article_title = soup.find('h2', {'id': 'title_area'})
            if article_title:
                span_text = article_title.find('span').text
            else:
                span_text = "제목을 찾을 수 없습니다."
            
            article = soup.find('div', {'id': 'newsct_article'})
            if article is None:
                return Response({"error": "기사 내용을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            article_text = article.get_text(separator='\n', strip=True)
        except Exception as e:
            return Response({"error": f"웹 페이지를 처리하는 중 오류가 발생했습니다: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        sentences = article_text.split('.')
        
        def extract_sentence_length(sentence):
            result = {}
            try:
                if '무기징역' in sentence:
                    result['징역'] = '무기징역'
                    return result
                match = re.search(r'징역\s*(\d+)\s*년\s*(\d+)?\s*(월|개월)?', sentence)
                if match:
                    years = int(match.group(1)) if match.group(1) else 0
                    months = int(match.group(2)) if match.group(2) else 0
                    result['징역'] = years * 12 + months
                else:
                    match = re.search(r'징역\s*(\d+)\s*(월|개월)', sentence)
                    if match:
                        result['징역'] = int(match.group(1))
                    match = re.search(r'징역\s*(\d+)\s*년', sentence)
                    if match:
                        result['징역'] = int(match.group(1)) * 12
                match = re.search(r'집행유예\s*(\d+)\s*년\s*(\d+)?\s*(월|개월)?', sentence)
                if match:
                    years = int(match.group(1)) if match.group(1) else 0
                    months = int(match.group(2)) if match.group(2) else 0
                    result['집행유예'] = years * 12 + months
                else:
                    match = re.search(r'집행유예\s*(\d+)\s*(월|개월)', sentence)
                    if match:
                        result['집행유예'] = int(match.group(1))
                    match = re.search(r'집행유예\s*(\d+)\s*년', sentence)
                    if match:
                        result['집행유예'] = int(match.group(1)) * 12
                return result if result else None
            except Exception as e:
                return None

        judge = True
        newsart = {}
        try:
            if re.search(r'징역', article_text):
                for sentence in sentences:
                    newsart = extract_sentence_length(sentence)
                    if newsart:
                        break
            else:
                judge = False
                newsart = None
        except Exception as e:
            return Response({"error": f"혐의 추출 중 오류가 발생했습니다: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            if tfidf_vectorizer is None or svm_model is None:
                raise ValueError("필요한 모델 또는 벡터라이저가 로드되지 않았습니다.")
            vectorized_sentence = tfidf_vectorizer.transform([span_text])
            prediction = svm_model.predict(vectorized_sentence)
            if prediction[0] == '마약':
                prediction[0] = '마약류관리에관한법률'
            if prediction[0]=='뇌물수수':
                prediction[0]='횡령'
        except Exception as e:
            return Response({"error": f"모델 예측 중 오류가 발생했습니다: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        charges = []
        charges2 = []
        tvalue = 0
        tindex = []

        for sentence in sentences:
            if '혐의' in sentence:
                real=""
                charges2.append(sentence)
                sentence = sentence.strip()
                혐의_idx = sentence.find('혐의')
                if len(sentence) > 혐의_idx + 1 and sentence[혐의_idx + 2] == '(':
                    start = sentence.find('(', 혐의_idx)
                    end = sentence.find(')', start)
                    real=sentence[start+1:end].strip()

                if re.search(r'(에게|[은는이가])', sentence):
                    end_idx = sentence.index('혐의')
                    if real:
                        charges.append(sentence[:end_idx] + ' ' + real)
                        real=False
                    else:
                        charges.append(sentence[:end_idx])

        charges_before = []
        original_sentences = []
        for sentence in charges:
            tvalue += 1
            words = re.split(r'\s+', sentence)
            extract = False
            extracted_sentence = ""
            last_josa_idx = -1
            for i, word in enumerate(words):
                if re.search(r'(은|는|이|가|에게)$', word):
                    last_josa_idx = i
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
                tindex.append(tvalue - 1)
                charges_before.append(extracted_sentence)
                original_sentences.append(sentence)
            keywords = {
                "살인":{"살인"},
                "절도":{"절도","불법사용","침입절도"},
                "장물":{"장물"},
                "사기":{"사기","컴퓨터등사용사기","부당이득","편의시설부정이용","전기통신금융사기","보험사기"},
                "횡령":{"횡령"},
                "배임":{"배임"},
                "도로교통법":{"운전","도로","도주치상","위험운전치상"},
                "손괴":{"손괴"},
                "강도":{"강도"},
                "방화":{"방화"},
                "성폭력":{"성폭력","강간","특수강도강간","카메라등이용촬영","공중밀집에서의추행","음란물"},
                "폭행":{"폭행","폭력행위"},
                "상해":{"상해"},
                "협박":{"협박"},
                "공갈":{"공갈"},
                "약취/유인":{"약취","유인","부녀매매","국외이송"},
                "체포/감금":{"체포","감금"},
                "위조범죄":{"통화","유가","인지","우표","문서","인장"},
                "공무원범죄":{"직무","직권","수뢰","증뢰"},
                "도박":{"도박","복표"},
                "과실범죄":{"과실","실화"},
                "명예":{"명예"},
                "권리행사방해":{"권리행사방해"},
                "주거침입":{"주거침입"},
                "비밀침해":{"비밀침해"},
                "유기":{"유기"},
                "교통방해":{"교통방해"},
                "도주/범죄은닉":{"도주","은닉"},
                "위증과증거인멸":{"위증","증거인멸"},
                "무고":{"무고"},
                "가정폭력":{"가정폭력"},
                "개인정보보호법":{"개인정보"},
                "건설":{"건설","건축"},
                "게임산업진흥법":{"게임"},
                "고용보험법":{"고용보험"},
                "공유수면관리":{"공유수면"},
                "공인중개사법":{"공인중개"},
                "공중위생법":{"공중위생"},
                "공직선거법":{"공직선거"},
                "관세법":{"관세"},
                "교통사고처리특례법":{"교통사고"},
                "국가기술자격법":{"국가기술자격"},
                "국가보안법":{"국가보안"},
                "국민체육진흥법":{"국민체육"},
                "근로기준법":{"근로","퇴직","급여"},
                "노동조합":{"노동"},
                "농수산물":{"농수산물"},
                "도시및주거환경":{"도시","주거환경"},
                "공정거래법":{"독점","공정거래"},
                "마약류관리에관한법률":{"마약"},
                "변호사법":{"변호사"},
                "병역법":{"병역"},
                "부동산":{"부동산"},
                "부정경쟁방지및영업비밀보호":{"부정경쟁","영업비밀"},
                "부정수표":{"부정수표"},
                "사해행위":{"사해행위"},
                "산업안전보건법":{"산업안전"},
                "산지관리법":{"산지"},
                "상표법":{"상표"},
                "선박":{"선박"},
                "성매매알선":{"성매매"},
                "식품위생법":{"식품위생"},
                "아동˙청소년":{"아동·청소년의성보호","아동"},
                "약사법":{"약사법"},
                "외국환거래법":{"외국환"},
                "의료법":{"의료"},
                "자동차":{"자동차"},
                "자본시장과금융투자업":{"자본시장","금융투자"},
                "저작권법":{"저작권"},
                "전자금융거래법":{"전자금융"},
                "정보통신망":{"정보통신망"},
                "조세범처벌법":{"조세범"},
                "주민등록법":{"주민등록법"},
                "주택법":{"주택"},
                "집회및시위":{"집회","시위"},
                "총포·도검·화약류단속":{"총포","도검","화약류"},
                "특허법":{"특허"},
                "폐기물관리법":{"폐기물"}
            }
        corrected_charges_before = []
        for original, extracted in zip(original_sentences, charges_before):
            start_idx = original.find(extracted[:2])
            if start_idx != -1:
                corrected_sentence = original[start_idx:]
                corrected_charges_before.append(corrected_sentence.strip())
            else:
                corrected_charges_before.append(extracted.strip())
        corrected_charges_before = [sentence.replace(",", " ") for sentence in corrected_charges_before]
        split_sentences = []
        for sentence in corrected_charges_before:
            words = re.split(r'[ ,\(\)·]', sentence)
            split_sentences.append([word for word in words if word])

        

        matche = []
        for lis in split_sentences:
            a = 0
            for words in lis:
                for words2 in keywords[prediction[0]]:
                    if words==words2:
                        a += 1
            matche.append(a)
        max_match_index = matche.index(max(matche))

        corrected_sentence = charges2[max_match_index].replace('\n','')

        def extract_text_between_markers(text):
            matches = list(re.finditer(r'(은|는|이|가|에게)', text))
            if matches:
                last_match = matches[0]
                start_idx = last_match.end()
                end_idx = text.find('혐의', start_idx)
                혐의_idx = text.find('혐의', start_idx)
                real=""
                if 혐의_idx != -1 and len(text) > 혐의_idx + 1 and text[혐의_idx + 2] == '(':
                    start = text.find('(', 혐의_idx)
                    end = text.find(')', start)
                    if end != -1:
                        real = text[start + 1:end].strip()
                end_idx = text.find('혐의', start_idx)
                if end_idx == -1:
                    end_idx = len(text)
                if real:
                    extracted_text = text[start_idx:end_idx].strip() + ' ' + real
                else:
                    extracted_text = text[start_idx:end_idx].strip()
                return extracted_text
            return ""

        correct_charge = extract_text_between_markers(corrected_sentence)
        charges_before = correct_charge
        phrases = charges_before.split(',')
        
        results = []
        for phrase in phrases:
            if "(" in phrase and ")" in phrase:
                start = phrase.find('(') + 1
                end = phrase.find(')')
                phrase=phrase[start:end]
                results.append(phrase)
                continue
            words = [word.strip() for word in phrase.split() if word.strip()]
            conv = ""
            for i, word in enumerate(words):
                origin=conv
                conv += word
                if filtered_dataset_df['사건명'].str.contains(conv).any():
                    if i== len(words)-1:
                        results.append(conv)
                        conv=""
                        break
                    continue
                else:
                    results.append(origin)
                    conv=""
                    break
        filtered_cases = filtered_dataset_df[filtered_dataset_df['분류'] == prediction[0]]
        len_results = len(results)
        final_filtered_cases = filtered_cases[
                filtered_cases['사건명'].apply(lambda x: any(word in x for word in results)) &
                (filtered_cases['사건개수'] <= len_results)
                ]
        matching_cases=final_filtered_cases

        def convert_sentence_to_numeric(value):
            if value == '무기징역':
                return -1
            elif value == '사형':
                return -2
            elif value == 'None' or value == 'NaN':
                return 0
            else:
                return pd.to_numeric(value, errors='coerce')

        try:
            matching_cases['징역(개월)'] = matching_cases['징역(개월)'].apply(convert_sentence_to_numeric).fillna(0)
            matching_cases['집행유예(개월)'] = matching_cases['집행유예(개월)'].apply(convert_sentence_to_numeric).fillna(0)
            matching_cases['벌금'] = matching_cases['벌금'].fillna(0)

            matching_cases = matching_cases[~((matching_cases['징역(개월)'] == 0) & (matching_cases['집행유예(개월)'] == 0) & (matching_cases['벌금'] == 0))]

            matching_cases['징역'] = matching_cases['징역(개월)'].apply(lambda x: 1 if float(x) > 0 else 0)
            matching_cases['집행유예'] = matching_cases['집행유예(개월)'].apply(lambda x: 1 if float(x) > 0 else 0)
            matching_cases['벌금1'] = matching_cases['벌금'].apply(lambda x: 1 if float(x) > 0 else 0)

            total = len(matching_cases)
            jail_count = matching_cases['징역'].sum()
            probation_count = matching_cases['집행유예'].sum()
            fine_count = matching_cases['벌금1'].sum()
            total_count = jail_count + probation_count + fine_count

            jail_percentage = (jail_count / total_count) * 100
            probation_percentage = (probation_count / total_count) * 100
            fine_percentage = (fine_count / total_count) * 100

            percentages = {
                '징역': jail_percentage,
                '집행유예': probation_percentage,
                '벌금': fine_percentage
            }
            highest_percentage = max(percentages, key=percentages.get)

            matching_cases['징역(년)'] = matching_cases['징역(개월)'] / 12
            if highest_percentage == '징역':
                if -2 in matching_cases['징역(개월)'].values:
                    highest_sentence = "사형"
                elif -1 in matching_cases['징역(개월)'].values:
                    highest_sentence = "무기징역"
                else:
                    highest_sentence_years = matching_cases['징역(년)'].max()
                    highest_sentence = f"{int(highest_sentence_years)}년"
                bins = np.arange(0, matching_cases['징역(년)'].max() + 1, 1)
                hist, bin_edges = np.histogram(matching_cases['징역(년)'], bins=bins)
                max_bin_index = np.argmax(hist)
                max_bin_start = bin_edges[max_bin_index]
                max_bin_end = bin_edges[max_bin_index + 1]
                max_bin_count = hist[max_bin_index]
                max_bin_percentage = int((max_bin_count / total_count) * 100)
                #result_string = f"{int(max_bin_start)}~{int(max_bin_end)}년"
            elif highest_percentage == '집행유예':
                highest_probation_months = matching_cases['집행유예(개월)'].max()
                highest_sentence = f"{int(highest_probation_months)}개월"
                bins = np.arange(0, matching_cases['집행유예(개월)'].max() + 1, 1)
                hist, bin_edges = np.histogram(matching_cases['집행유예(개월)'], bins=bins)
                max_bin_index = np.argmax(hist)
                max_bin_start = bin_edges[max_bin_index]
                max_bin_end = bin_edges[max_bin_index + 1]
                max_bin_count = hist[max_bin_index]
                max_bin_percentage = int((max_bin_count / total_count) * 100)
                #result_string = f"{int(max_bin_start)}~{int(max_bin_end)}개월"
            else:
                highest_fine = matching_cases['벌금'].max()
                highest_sentence = f"{highest_fine}원"
                bins = np.arange(0, matching_cases['벌금'].max() + 500000, 500000)
                hist, bin_edges = np.histogram(matching_cases['벌금'], bins=bins)
                max_bin_index = np.argmax(hist)
                max_bin_start = bin_edges[max_bin_index]
                max_bin_end = bin_edges[max_bin_index + 1]
                max_bin_count = hist[max_bin_index]
                max_bin_percentage = int((max_bin_count / total_count) * 100)
                #result_string = f"{int(max_bin_start)}~{int(max_bin_end)}원"
        except Exception as e:
            return Response({"error": f"판결 유형 처리 중 오류가 발생했습니다: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if highest_sentence=="0년":
            highest_sentence=str(max(matching_cases['징역(개월)']))+"개월"

        drilldown_data = {
                'series': []
                }
        # 징역(년) 데이터 생성
        jail_bins = np.arange(0, matching_cases['징역(개월)'].max() / 12 + 1, 1)
        jail_hist, jail_bin_edges = np.histogram(matching_cases[matching_cases['징역'] == 1]['징역(년)'], bins=jail_bins)
        drilldown_data['series'].append({
            'name': '징역(년)',
            'id': '징역(년)',
            'data': [[f"{int(jail_bin_edges[i])}~{int(jail_bin_edges[i + 1])}년", int(jail_hist[i])] for i in range(len(jail_hist))]
            })
        # 집행유예(년) 데이터 생성
        probation_bins = np.arange(0, matching_cases['집행유예(개월)'].max() / 12 + 1, 1)  # 년 단위로 그룹화
        probation_hist, probation_bin_edges = np.histogram(matching_cases[matching_cases['집행유예'] == 1]['집행유예(개월)'] / 12, bins=probation_bins)
        drilldown_data['series'].append({
            'name': '집행유예(년)',
            'id': '집행유예(년)',
            'data': [[f"{int(probation_bin_edges[i])}~{int(probation_bin_edges[i + 1])}년", int(probation_hist[i])] for i in range(len(probation_hist))]
            })
        # 벌금 데이터 생성
        fine_bins = np.arange(0, matching_cases['벌금'].max() + 500000, 500000)
        fine_hist, fine_bin_edges = np.histogram(matching_cases[matching_cases['벌금1'] == 1]['벌금'], bins=fine_bins)
        drilldown_data['series'].append({
            'name': '벌금',
            'id': '벌금',
            'data': [[f"{int(fine_bin_edges[i])}~{int(fine_bin_edges[i + 1])}원", int(fine_hist[i])] for i in range(len(fine_hist))]
            })
        if highest_percentage == '징역':
            max_bin_index = np.argmax(jail_hist)
            result_string = f"{int(jail_bin_edges[max_bin_index])}~{int(jail_bin_edges[max_bin_index + 1])}년"
        elif highest_percentage == '집행유예':
            max_bin_index = np.argmax(probation_hist)
            result_string = f"{int(probation_bin_edges[max_bin_index])}~{int(probation_bin_edges[max_bin_index + 1])}년"
        else:
            max_bin_index = np.argmax(fine_hist)
            result_string = f"{int(fine_bin_edges[max_bin_index])}~{int(fine_bin_edges[max_bin_index + 1])}원"

        try:
            if judge:
                response_data = {
                    "prediction": prediction[0],
                    "sentence": results,
                    "judge": judge,
                    "newsart": newsart,
                    "total": total,
                    "jail_percentage": jail_percentage,
                    "probation_percentage": probation_percentage,
                    "fine_percentage": fine_percentage,
                    "highest_percentage": highest_percentage,
                    "highest_sentence": highest_sentence,
                    "max_bin_percentage": max_bin_percentage,
                    "result_string": result_string,
                    "jail_count": jail_count,
                    "probation_count": probation_count,
                    "fine_count": fine_count,
                    "drilldown_data":drilldown_data
                }
            else:
                response_data = {
                    "prediction": prediction[0],
                    "sentence": results,
                    "judge": judge,
                    "total": total,
                    "jail_percentage": jail_percentage,
                    "probation_percentage": probation_percentage,
                    "fine_percentage": fine_percentage,
                    "highest_percentage": highest_percentage,
                    "highest_sentence": highest_sentence,
                    "max_bin_percentage": max_bin_percentage,
                    "result_string": result_string,
                    "jail_count": jail_count,
                    "probation_count": probation_count,
                    "fine_count": fine_count,
                    "drilldown_data":drilldown_data
                }

            import json
            from django.http import JsonResponse
            selected_columns = matching_cases[['판례정보일련번호', '사건명', '사건번호', '선고일자', '선고', '법원명', '사건종류명', '판결유형', '전문', '판결', '분류','징역(개월)','집행유예(개월)','벌금']]            
            def truncate_text(text, length=300):
                if isinstance(text, str):
                    text = text.replace('\n', '')
                    return text[:length]
                return text
            selected_columns['전문'] = selected_columns['전문'].apply(truncate_text)
            response_data2 = selected_columns.to_dict(orient='records')
            
            return Response({
                "data": response_data,
                "json":response_data2
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"응답 처리 중 오류가 발생했습니다: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

