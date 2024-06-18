window.onload = function() {

    // Chrome 탭 쿼리
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        document.getElementById('title').textContent = localStorage.getItem('newsTitle') || 'No title available';
        document.getElementById('image').src = localStorage.getItem('newsImage') || '';


                console.log('Unable to fetch news data, loaded data from local storage.');
    });
};

