// 알림장 팝업 띄우기
function openPop(childName) {
    document.getElementById("popup_layer").style.display = "block";
    document.querySelector("#popup_layer h3").innerText = `${childName}의 알림장`;
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