// fetchAndUpdateData.js

// 데이터를 요청하고 JSON 데이터를 반환하는 함수
function fetchAndUpdateData() {
    const url = 'http://15.164.119.80:8000/hello/';
    const storedUrl = localStorage.getItem('curl');
    const data = { url: storedUrl };

    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Network response was not ok.');
        }
    })
    .then(data => {
        const extractedData = {
            total: data.data.total,
            jailPercentage: data.data.jail_percentage,
            probationPercentage: data.data.probation_percentage,
            finePercentage: data.data.fine_percentage,
            prediction: data.data.prediction,
            maxper:data.data.max_bin_percentage,
            sentence: data.data.sentence,
            judge: data.data.judge,
            newsart: data.data.newsart,
            highestSentence: data.data.highest_sentence,
            resultString: data.data.result_string,
            what: data.data.highest_percentage,
            jailcount:data.data.jail_count,
            probationcount:data.data.probation_count,
            finecount:data.data.fine_count,
            drilldown:data.data.drilldown_data,
            json:data.json
            
        };

        // 데이터를 반환
        return extractedData;
    })
    .catch(error => {
        console.error('Fetch error:', error);
        document.getElementById('loading').innerText = 'Error';
        return null;
    });
}
