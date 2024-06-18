// 메시지 리스너 설정
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === "fetchNews") {
        const title = document.querySelector('#title_area').textContent.trim();
        const articleContent = document.getElementById('dic_area').textContent.trim();
        var imgElement = document.getElementById('img1').src;
        // document.getElementById('title_area').textContent = title;
        // document.getElementById('content').textContent = articleContent;
        // document.getElementById('image').src = imgElement;  // 이미지 URL 설정

        sendResponse({ title: title,content:articleContent  ,image: imgElement });
        }
        return true; // 비동기 응답을 위해 true 반환
    });
    