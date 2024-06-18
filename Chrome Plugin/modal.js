document.addEventListener('DOMContentLoaded', function () {
    // 데이터 로드 및 모달 열기
    document.getElementById('similarCasesButton').addEventListener('click', function () {
        fetchAndUpdateData().then(data => {
           
                const modal = document.getElementById('myModal');
                const tbody = document.getElementById('modalTableBody');
                tbody.innerHTML = ''; // 기존 내용을 지웁니다.

                // 데이터를 테이블에 추가합니다.
                data.json.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.판례정보일련번호}</td>
                        <td>${item.사건명}</td>
                        <td>${item.사건번호}</td>
                        <td>${item.선고일자}</td>
                        <td>${item.선고}</td>
                        <td>${item.법원명}</td>
                        <td>${item.사건종류명}</td>
                        <td>${item.판결유형}</td>
                        <td>${item.전문.replace(/\n/g, '<br>')}</td>
                        <td>${item.판결}</td>
                        <td>${item.분류}</td>
                        <td>${item['징역(개월)']}</td>
                        <td>${item['집행유예(개월)']}</td>
                        <td>${item.벌금}</td>
                    `;
                    tbody.appendChild(row);
                });

                modal.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    });

    // 모달 닫기 이벤트
    var span = document.getElementsByClassName('close')[0];
    span.onclick = function () {
        var modal = document.getElementById('myModal');
        modal.style.display = 'none';
    }

    window.onclick = function (event) {
        var modal = document.getElementById('myModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
});
