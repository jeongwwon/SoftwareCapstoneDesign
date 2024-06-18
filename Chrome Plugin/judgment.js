// judgment.js

document.addEventListener('DOMContentLoaded', function () {
    fetchAndUpdateData().then(data => {
        if (!data) {
            console.error('No data received or data is invalid');
            return;
        }

        // 받은 데이터를 HTML 요소에 채워 넣기
        document.getElementById('prediction').innerText = data.prediction;
        document.getElementById('sentence').innerText = data.sentence;

        // 판결 데이터 처리
        let judgeText = 'X';
        if (data.judge) {
            const formatMonthsToYearsAndMonths = (months) => {
                if (isNaN(months) || months === 0) {
                    return '';
                }
                const years = Math.floor(months / 12);
                const remainingMonths = months % 12;
                let result = '';
                if (years > 0) {
                    result += `${years}년 `;
                }
                if (remainingMonths > 0) {
                    result += `${remainingMonths}개월`;
                }
                return result.trim();
            };

            const parseSentence = (sentence) => {
                const years = (sentence.match(/(\d+)년/) || [0, 0])[1];
                const months = (sentence.match(/(\d+)개월/) || [0, 0])[1];
                return parseInt(years) * 12 + parseInt(months);
            };

            const formatSentence = (months) => {
                const years = Math.floor(months / 12);
                const remainingMonths = months % 12;
                let result = '';
                if (years > 0) {
                    result += `${years}년 `;
                }
                if (remainingMonths > 0) {
                    result += `${remainingMonths}개월`;
                }
                return result.trim();
            };

            const newsartJail = data.newsart['징역'] || 0;
            const newsartProbation = data.newsart['집행유예'] || 0;

            const newsartJailFormatted = formatMonthsToYearsAndMonths(newsartJail);
            const newsartProbationFormatted = formatMonthsToYearsAndMonths(newsartProbation);

            judgeText = '';
            if (newsartJailFormatted) {
                judgeText += `징역: ${newsartJailFormatted}`;
            }
            if (newsartProbationFormatted) {
                if (judgeText) {
                    judgeText += ', ';
                }
                judgeText += `집행유예: ${newsartProbationFormatted}`;
            }
            judgeText = judgeText || 'X';

            document.getElementById('judge').innerText = judgeText;

            // 결론 문장 생성 및 업데이트
            const highestSentence = data.highestSentence;
            const resultString = data.resultString;
            const highestPercentage = data.maxper;
            let conclusionText = `유사 사건 법정 최고형은 ${highestSentence}이고<br>`;

            // 형량 비교
            const judgeSentence = parseSentence(judgeText);
            const predictedSentence = parseSentence(resultString);

            const formattedJudgeSentence = formatSentence(judgeSentence);
            const formattedPredictedSentence = formatSentence(predictedSentence);

            if (judgeSentence > predictedSentence) {
                conclusionText += `${highestPercentage}% 비중으로 예측된 형량(${formattedPredictedSentence})보다 <span style="color: red;">가중된 처벌</span>을 받았습니다.`;
            } else if (judgeSentence < predictedSentence) {
                conclusionText += `${highestPercentage}% 비중으로 예측된 형량(${formattedPredictedSentence})보다 <span style="color: red;">감량된 처벌</span>을 받았습니다.`;
            } else {
                conclusionText += `${highestPercentage}% 비중으로 예측된 형량(${formattedPredictedSentence})과 <span style="color: red;">동일</span>합니다.`;
            }

            document.getElementById('conclusion').innerHTML = conclusionText;
        } else {
            const highestSentence = data.highestSentence;
            const what=data.what;
            const resultString = data.resultString;
            const highestPercentage = data.maxper;
            let conclusionText = `유사 사건 중 법정 최고형은 ${highestSentence}이고 <br> ${highestPercentage}% 확률로 <span style="color: red;">${what} ${resultString}형</span>이 예상됩니다.`;
            document.getElementById('judge').innerText = "500만원";
            document.getElementById('conclusion').innerHTML = conclusionText;
        }
        // 로딩 상태를 숨기고 콘텐츠를 표시
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('content').classList.remove('hidden');

        const total = data.total;

        // Highcharts 차트를 생성하고 데이터를 적용
        Highcharts.chart('container1', {
            chart: {
                type: 'pie'
            },
            title: {
                text: '판결 분포'
            },
            tooltip: {
                valueSuffix: '%'
            },
            subtitle: {
                text: `총사건수: ${total}`,
                align: 'right',
                verticalAlign: 'top',
                x: 0,
                y: 60,
                style: {
                    fontSize: '1.5em',
                    fontWeight: 'bold'
                }
            },
            plotOptions: {
                series: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: [{
                        enabled: true,
                        distance: 20
                    }, {
                        enabled: true,
                        distance: -40,
                        format: '{point.percentage:.1f}%',
                        style: {
                            fontSize: '1.2em',
                            textOutline: 'none',
                            opacity: 0.7
                        },
                        filter: {
                            operator: '>',
                            property: 'percentage',
                            value: 10
                        }
                    }]
                }
            },
            series: [
                {
                    name: 'Percentage',
                    colorByPoint: true,
                    data: [
                        {
                            name: '징역',
                            y: data.jailPercentage
                        },
                        {
                            name: '벌금',
                            y: data.finePercentage
                        },
                        {
                            name: '집행유예',
                            y: data.probationPercentage
                        }
                    ]
                }
            ]
        });
    }).catch(error => {
        console.error('Error in fetchAndUpdateData:', error);
    });
});
