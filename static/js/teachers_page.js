// 개인 알림장 열기
function openForm() {
    const container = document.getElementById('homeworkContainer');
    const formArea = document.getElementById('formArea');
    const formAreaAll = document.getElementById('formAreaAll');

    container.classList.add('open');
    formArea.style.width = '400px';
    formArea.style.padding = '1px';      // 보여줄 때만 padding 추가
    formArea.style.opacity = '1';
    formArea.style.pointerEvents = 'auto';

    formAreaAll.style.width = '0';
    formAreaAll.style.padding = '0';      // 안 보이게 padding 제거
    formAreaAll.style.opacity = '0';
    formAreaAll.style.pointerEvents = 'none';
};

// 공통 내용 알림장 열기
function openFormAll() {
    const container = document.getElementById('homeworkContainer');
    const formArea = document.getElementById('formArea');
    const formAreaAll = document.getElementById('formAreaAll');

    container.classList.add('open');
    container.classList.add('open');
    formAreaAll.style.width = '400px';
    formAreaAll.style.padding = '1px';
    formAreaAll.style.opacity = '1';
    formAreaAll.style.pointerEvents = 'auto';

    formArea.style.width = '0';
    formArea.style.padding = '0';
    formArea.style.opacity = '0';
    formArea.style.pointerEvents = 'none';
};

function closeForm() {
    const formArea = document.getElementById('formArea');
    const formAreaAll = document.getElementById('formAreaAll');
    const container = document.getElementById('homeworkContainer');

    formArea.style.width = '0';
    formArea.style.padding = '0';
    formArea.style.opacity = '0';
    formArea.style.pointerEvents = 'none';

    formAreaAll.style.width = '0';
    formAreaAll.style.padding = '0';
    formAreaAll.style.opacity = '0';
    formAreaAll.style.pointerEvents = 'none';

    container.classList.remove('open');
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