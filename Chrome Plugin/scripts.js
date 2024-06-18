document.addEventListener('DOMContentLoaded', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: "fetchNews"}, function(response) {
            if (response) {
                document.getElementById('title_area').textContent = response.title;
                let articleContent = response.content.replace(/[\r\n]+/gm, "");
                document.getElementById('content').textContent = articleContent;
                document.getElementById('image').src = response.image;

                localStorage.setItem('newsTitle', response.title);
                localStorage.setItem('newsImage', response.image);
                localStorage.setItem('curl', tabs[0].url); // 현재 URL 저장
                //localStorage.setItem('newsContent', articleContent);
                
                document.getElementById('analyze').addEventListener('click', function() {
                    localStorage.setItem('newsTitle', response.title);
                    localStorage.setItem('newsImage', response.image);
                    localStorage.setItem('curl', tabs[0].url); // 현재 URL 저장
                    window.open('analyze.html', '_blank'); // 새 탭에서 analyze.html 열기
                });
                
            } else {
                document.getElementById('content').textContent = 'Unable to fetch news data.';
            }
        });
    });
});
