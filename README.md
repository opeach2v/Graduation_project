# 🚨 어린이가 위험해요!
2025.01.01 ~ ing <br><br>


5인으로 이루어진 **사공사(404)** 팀이 진행한 졸업작품입니다.
어린이집 내부에서 일어나는 어린이들의 위험 행동을 감지 후 분석하고, 분석된 내용을 표나 그래프로 학부모와 선생님에게 보여줄 수 있도록 하는 프로젝트입니다.

⚠해당 깃허브에는 **서버**와 **프론트/백엔드**만 존재하는 코드라는 점을 유의해주세요! 따라서 따로 설치 방법은 첨부하지 않았습니다.
<br><br><br>


## 목차
- [사용 프로그램](#사용-프로그램)
- [주요 기능](#주요-기능)
- [시스템 구조도](#시스템-구조도)
- [UI 소개](#ui-소개)
- [사용 예시](#사용-예시)
<br><br><br>


## 사용 프로그램
[ 서버 ]  AWS ES2 <br>
[ 웹 프레임워크 ]  Django (+ Nginx, uWSGI) <br>
[ 데이터베이스 ]  MongoDB
<br><br><br>


## 주요 기능
웹 서버로서 클라이언트(선생님, 학부모)의 요청을 처리하고, 각 사용자에게 맞는 홈페이지를 제공하며, 데이터 관리 및 로그인 기능을 담당합니다.<br><br>
학부모는 자녀를 등록한 후, 자녀의 당일 위험 행동 결과와 선생님이 작성한 알림장을 확인할 수 있어 자녀의 생활을 빠르게 파악할 수 있습니다.<br>
선생님은 자신이 맡은 반의 모든 아이들의 위험 행동 결과를 확인할 수 있으며, 위험 행동이 증가하지 않도록 예방적인 조치를 취할 수 있습니다. 또한, 각 아이의 알림장에 특이 사항이나 준비물을 전달하는 메시지를 작성할 수 있어 학부모와의 원활한 소통이 가능합니다.
<br><br><br>


## 시스템 구조도
<img src="https://github.com/user-attachments/assets/62e57e4e-2b23-4c06-bffd-fd9f2753989e" width="600"><br>
빨간 테두리 부분이 해당 깃허브에 저장되어 있습니다
<br><br><br>


## UI 소개
<table>
  <thead>
    <tr>
      <th>1. 로그인 페이지</th>
      <th>2. 회원가입 페이지</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/24c643b7-8eae-4e81-9d84-c7c41f78f596" width="300"></td>
      <td><img src="https://github.com/user-attachments/assets/73ede6cf-aa3a-4db8-be78-803c615bd5fd" width="300"></td>
    </tr>
  </tbody>
</table>
<table>
  <thead>
    <tr>
      <th>3. 학부모 페이지</th>
      <th>4. 선생님 페이지</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><img src="https://github.com/user-attachments/assets/2c64c8c4-3c69-4d44-9177-bd2b4cc9807c" width="300"></td>
      <td>(미완)</td>
    </tr>
  </tbody>
</table>
<br><br><br>




## 사용 예시

<br>

