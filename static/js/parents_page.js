// 알림장 팝업 띄우기
function openPop(childName, childId) {
    // 콘솔에서 보이기 
    console.log("name: ", childName)
    console.log("ID: ", childId)

    
    document.getElementById("popup_layer").style.display = "block";
    document.querySelector("#popup_layer h2").innerText = `${childName}의 알림장`;
    fetch(`/api/showNotice_cont/${childId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.content) { // 값이 있을 때만
                document.querySelector(".popup_cont p").innerText = data.content;
            }
            if (data.total_res) {   // 값이 있을 때면 
                document.querySelector(".popup_cont h3").innerText = `* 오늘의 행동 감지: ${data.total_res}건`;
            }

            const rows = document.querySelectorAll("#eventTable tbody tr");

            for(const [event, count] of Object.entries(data.event_counts)) {
                for(const row of rows) {
                    const th = row.querySelector("th");
                    const td = row.querySelector("td");
                    if(th && th.innerText.trim() === event) { // 이벤트 이름과 일치하면
                        td.innerText = `${count}건`;    // 같은 인덱스 td에 값 넣기
                        break;  // 다음 이벤트로 넘어가기 
                    }
                }
            }
        })
        .catch(error => console.error('Error: ', error));
}
// 알림장 팝업 닫기
function closePop() {
    document.getElementById("popup_layer").style.display = "none";
}

// 오늘의 하루 팝업 띄우기
function openTodayPop(childName) {
    document.getElementById("today_popup_layer").style.display = "block";
    document.querySelector("#popup_layer h3 .child-name").innerText = `-------${childName} 어린이-------`;
}
// 오늘의 하루 팝업 닫기
function closeTodayPop() {
    document.getElementById("today_popup_layer").style.display = "none";
}

// 사진/영상 슬라이드1
document.addEventListener('DOMContentLoaded', function () {
    const prev = document.querySelector('.prev'); // 이전 이미지
    const next = document.querySelector('.next'); // 다음 이미지
    const slideBox = document.querySelector('.slide_box');
    const slideItems = document.querySelectorAll('.slide_item');
    const slideLength = slideItems.length;
    let currentIndex = 0;

    const moveSlide = function (num) {
        slideBox.style.transition = 'transform 0.4s ease'; // 부드럽게
        slideBox.style.transform = `translateX(${-num * 280}px)`;
        currentIndex = num;
    };

    // 이미지에 클릭 이벤트 연결
    prev.addEventListener('click', () => {
        if (currentIndex > 0) {
            moveSlide(currentIndex - 1);
        }
    });

    next.addEventListener('click', () => {
        if (currentIndex < slideLength - 1) {
            moveSlide(currentIndex + 1);
        }
    });
});

// 사진/영상 슬라이드2
document.addEventListener('DOMContentLoaded', function () {
    const prev = document.querySelector('.prev1'); // 이전 이미지
    const next = document.querySelector('.next1'); // 다음 이미지
    const slideBox = document.querySelector('.slide_box1');
    const slideItems = document.querySelectorAll('.slide_item1');
    const slideLength = slideItems.length;
    let currentIndex = 0;

    const moveSlide = function (num) {
        slideBox.style.transition = 'transform 0.4s ease'; // 부드럽게
        slideBox.style.transform = `translateX(${-num * 280}px)`;
        currentIndex = num;
    };

    // 이미지에 클릭 이벤트 연결
    prev.addEventListener('click', () => {
        if (currentIndex > 0) {
            moveSlide(currentIndex - 1);
        }
    });

    next.addEventListener('click', () => {
        if (currentIndex < slideLength - 1) {
            moveSlide(currentIndex + 1);
        }
    });
});

function toggleAddForm(parentId) {
    const form = document.getElementById('add-form-' + parentId);
    if (form.style.display === 'none') {
        form.style.display = 'block';
    } else {
        form.style.display = 'none';
    }
}

// js로 뒤로가기 감지해서 막기
window.onload = function() {
    if (!'{{ request.session.username|default_if_none:"" }}') {
        window.location.href = "{% url 'login_user' %}";
    }
    };

    window.history.pushState(null, "", window.location.href);
    window.onpopstate = function () {
    window.history.pushState(null, "", window.location.href);
};