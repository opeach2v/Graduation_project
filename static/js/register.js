const hypenTel = (target) => {
    target.value = target.value
        .replace(/[^0-9]/g, '')
        .replace(/^(\d{2,3})(\d{3,4})(\d{4})$/, `$1-$2-$3`);
}

// 학부모, 선생님에 따라 다르게 나타남
document.addEventListener("DOMContentLoaded", function () {
    const teacherRadio = document.getElementById("teacher");
    const parentRadio = document.getElementById("parent");
    const teacherFields = document.getElementById("teacher-field");

    function toggleFields() {
        if (teacherRadio.checked) {
            teacherFields.classList.add("active");
        } else if (parentRadio.checked) {
            teacherFields.classList.remove("active");
        }
    }

    teacherRadio.addEventListener("change", toggleFields);
    parentRadio.addEventListener("change", toggleFields);
});