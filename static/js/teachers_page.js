let currentChildId; // 현재 열려있는 알림장의 아이 ID (나중에 알림장 내용할 때 쓸 것)

// 개인 알림장 열기
function openForm(childName, childId) {
  document.querySelector(
    "#formArea .form-content h3"
  ).innerText = `${childName}의 알림장 내용 작성`;
  currentChildId = childId; // 현재 열려있는 아이의 ID 저장
}

// 그동안 썼던 알림장 로그 form 열기
function openLogForm(teacher_id) {
  const container = document.querySelector("#formAreaLog .form-content");
  const formArea = document.getElementById("formArea");
  const formAreaLog = document.getElementById("formAreaLog");

  container.classList.add("open");
  formAreaLog.style.width = "400px";
  formAreaLog.style.padding = "1px";
  formAreaLog.style.opacity = "1";
  formAreaLog.style.pointerEvents = "auto";

  formArea.style.width = "0";
  formArea.style.padding = "0";
  formArea.style.opacity = "0";
  formArea.style.pointerEvents = "none";

  // // 알림장 내용 채우기 (AJAX)
  // fetch(`/api/notice_logs/${teacher_id}/`)
  //   .then(res => res.json())
  //   .then(data => {
  //     container.innerHTML = `
  //       <button class="x-btn" onclick="closeForm()">X</button>
  //       <h3 style="padding: 15px; padding-top: 25px;">알림장 로그</h3>
  //     `;

  //     if (data.notices.length === 0) {
  //       const empty = document.createElement("div");
  //       empty.textContent = "지금까지 작성된 알림장이 없습니다.";
  //       empty.style.padding = "10px 15px";
  //       container.appendChild(empty);
  //       return;
  //     }

  //     data.notices.forEach((notice, index) => {
  //       // 아코디언 버튼 생성
  //       const button = document.createElement("button");
  //       button.className = "accordion";
  //       button.textContent = `${notice.child_name}의 알림장&nbsp;&nbsp;${notice.date}`;
  //       container.appendChild(button);

  //       // 패널 생성
  //       const panel = document.createElement("div");
  //       panel.className = "panel";
  //       panel.style.display = "none"; // 기본은 닫힘
  //       panel.innerHTML = `<p>${notice.content}</p>`;
  //       container.appendChild(panel);

  //       // 버튼 클릭 시 토글 동작
  //       button.addEventListener("click", () => {
  //         const isOpen = panel.style.display === "block";
  //         panel.style.display = isOpen ? "none" : "block";
  //       });
  //     });
  //   })
  //   .catch(err => {
  //     alert("알림장 데이터를 불러오는 데 실패했습니다.");
  //     console.error(err);
  //   });
}

function closeForm() {
  const formArea = document.getElementById("formArea");
  const formAreaLog = document.getElementById("formAreaLog");
  const container = document.getElementById("homeworkContainer");

  formArea.style.display = "none";
  formArea.style.width = "0";
  formArea.style.padding = "0";
  formArea.style.opacity = "0";
  formArea.style.pointerEvents = "none";

  formAreaLog.style.display = "none";
  formAreaLog.style.width = "0";
  formAreaLog.style.padding = "0";
  formAreaLog.style.opacity = "0";
  formAreaLog.style.pointerEvents = "none";

  container.classList.remove("open");
}

// 개인 알림장 내용 저장 (AJAX)
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("writeNotice");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault(); // 폼 기본 동작(페이지 이동) 막기

      const content = document.getElementById("noticeContent").value;
      const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
      ).value;
      const url = form.dataset.url; // form 요소의 data-url 속성 값 읽기

      console.log(`아이 ID: ${currentChildId}, ${url}`); // 디버깅용 로그

      fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
        },
        body: new URLSearchParams({
          content: content,
          child_id: currentChildId, // 현재 열려있는 아이의 ID 전달
        }),
      })
        .then((res) => {
          if (!res.ok) {
            // 응답 상태가 200 OK가 아니면
            throw new Error(`서버 오류: ${res.status}`);
          }
          return res.json();
        })
        .then((data) => {
          if (data.error) {
            alert("데이터 에러" + data.error);
          } else {
            alert("저장되었습니다!");
            form.querySelector("textarea").value = ""; // 저장 후 textarea 초기화
          }
        })
        .catch((err) => {
          alert(`저장 중 오류 발생: ${err.message}`);
          console.error(err);
        });
    });
  }
});

// 개인 알림장 내용 삭제(textarea 비우기)
function clearForm() {
  const formArea = document.getElementById("formArea");
  formArea.querySelector("textarea").value = "";
}

// js로 뒤로가기 감지해서 막기
window.onload = function () {
  if (!'{{ request.session.username|default_if_none:"" }}') {
    window.location.href = "{% url 'login_user' %}";
  }
};

window.history.pushState(null, "", window.location.href);
window.onpopstate = function () {
  window.history.pushState(null, "", window.location.href);
};

// 도넛 그래프 동적으로 그리기 (전체 데이터)
document.addEventListener("DOMContentLoaded", function () {
  const classroom = document.getElementById("doughnut-box").dataset.classroom;

  fetch(`/chart-data/${classroom}`)
    .then((response) => response.json())
    .then((chartInfo) => {
      const totalEvents = chartInfo.data.reduce((sum, val) => sum + val, 0);
      const chartContainer = document.getElementById("doughnut-box");

      console.log("전체 데이터 Chart Info:", chartInfo); // 디버깅용 로그

      if (totalEvents === 0) {
        // 데이터가 없을 때 <p> 메시지 삽입
        chartContainer.innerHTML = `<p>해당 반에서 위험 행동은 없습니다.</p>`;
      } else {
        new Chart(document.getElementById("doughnut-chart"), {
          type: "doughnut",
          data: {
            labels: chartInfo.labels,
            datasets: [
              {
                label: "event",
                backgroundColor: [
                  "#d62827",
                  "#94d2bb",
                  "#099396",
                  "#00304e",
                  "#f58000",
                ],
                data: chartInfo.data,
              },
            ],
          },
          options: {
            title: {
              display: true,
              text: "반 전체 행동 분석 (건)",
            },
          },
        });

        const totalEvents = chartInfo.data.reduce((sum, val) => sum + val, 0);
        const fightingIndex = chartInfo.labels.indexOf("fighting");
        let countMessage = "";
        let ratioMessage = "";

        if (fightingIndex !== -1 && totalEvents > 0) {
          const fightingCount = chartInfo.data[fightingIndex];
          const fightingRatio = ((fightingCount / totalEvents) * 100).toFixed(
            1
          );

          countMessage = `위험 행동(fighting)/전체 행동: ${fightingCount}/${totalEvents}`;
          ratioMessage = `위험 행동(fighting) 비율: ${fightingRatio}%`;
        } else {
          countMessage = `위험 행동(fighting) 데이터가 없습니다.`;
          ratioMessage = "";
        }

        const chartContainer = document.getElementById("doughnut-box");

        // 부모가 flex row면 아래처럼 바꿔줘도 됨
        chartContainer.style.display = "flex";
        chartContainer.style.flexDirection = "column";
        chartContainer.style.alignItems = "center";

        const pCount = document.createElement("p");
        pCount.style.marginTop = "15px";
        pCount.style.fontWeight = "bold";
        pCount.innerText = countMessage;

        chartContainer.appendChild(pCount);

        if (ratioMessage) {
          const pRatio = document.createElement("p");
          pRatio.style.fontWeight = "bold";
          pRatio.style.textAlign = "center";
          pRatio.innerText = ratioMessage;
          chartContainer.appendChild(pRatio);
        }
      }
    })
    .catch((error) => {
      console.error("차트 데이터를 불러오는 중 오류 발생:", error);
    });
});

// 바 그래프 동적으로 그리기 (당일 데이터)
document.addEventListener("DOMContentLoaded", function () {
  const classroom = document.getElementById("bar-box").dataset.classroom;
  fetch(`/today-chart-data/${classroom}`)
    .then((response) => response.json())
    .then((chartInfo) => {
      const totalEvents = chartInfo.todayData.reduce(
        (sum, val) => sum + val,
        0
      );
      const chartContainer = document.getElementById("bar-box");

      console.log("당일 데이터 Chart Info:", chartInfo); // 디버깅용 로그

      if (totalEvents === 0) {
        // 데이터가 없을 때 <p> 메시지 삽입
        chartContainer.innerHTML = `<p>오늘 하루 위험 행동은 없습니다.</p>`;
      } else {
        new Chart(document.getElementById("bar-chart"), {
          type: "bar",
          data: {
            labels: chartInfo.todayLabels,
            datasets: [
              {
                label: "event",
                backgroundColor: [
                  "rgba(247, 46, 46, 0.2)",
                  "rgba(255, 159, 64, 0.2)",
                  "rgba(255, 205, 86, 0.2)",
                  "rgba(75, 192, 192, 0.2)",
                  "rgba(54, 162, 235, 0.2)",
                ],
                borderColor: [
                  "rgb(252, 83, 83)",
                  "rgb(255, 159, 64)",
                  "rgb(255, 205, 86)",
                  "rgb(75, 192, 192)",
                  "rgb(54, 162, 235)",
                ],
                data: chartInfo.todayData,
              },
            ],
          },
          options: {
            plugins: {
              title: {
                display: true,
                text: "오늘의 행동 분석 (건)",
              },
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  precision: 0,
                },
              },
            },
          },
        });
        const chartContainer = document.getElementById("bar-box");

        // 부모가 flex row면 아래처럼 바꿔줘도 됨
        chartContainer.style.display = "flex";
        chartContainer.style.flexDirection = "column";
        chartContainer.style.alignItems = "center";

        const pCount = document.createElement("p");
        pCount.style.marginTop = "15px";
        pCount.style.fontWeight = "bold";
        pCount.innerText = countMessage;

        chartContainer.appendChild(pCount);

        if (ratioMessage) {
          const pRatio = document.createElement("p");
          pRatio.style.fontWeight = "bold";
          pRatio.style.textAlign = "center";
          pRatio.innerText = ratioMessage;
          chartContainer.appendChild(pRatio);
        }
      }
    })
    .catch((error) => {
      console.error("차트 데이터를 불러오는 중 오류 발생:", error);
    });
});
