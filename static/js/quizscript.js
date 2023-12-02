const starBtn = document.querySelector(".start-btn");
const continueBtn = document.querySelector(".continue-btn");
const quizSection = document.querySelector(".quiz-section");
const quizBox = document.querySelector(".quiz-box");

continueBtn.onclick = () => {
  quizSection.classList.add("active");
  quizBox.classList.add("active");
  showQuestions(0);
};

let questionCount = 0;

const nextBtn = document.querySelector(".next-btn");

nextBtn.onclick = () => {
  questionCount++;
  showQuestions(questionCount);
};

const optionList = document.querySelector(".option-list");

function showQuestions(index) {
  const questionText = document.querySelector(".question-text");
  questionText.textContent = `${questions[index].numb}. ${questions[index].questions}`;

  let optionTag = `<div class="option"><span>${questions[index].options[0]}</span></div>
    <div class="option"><span>${questions[index].options[1]}</span></div>
    <div class="option"><span>${questions[index].options[2]}</span></div>
    <div class="option"><span>${questions[index].options[3]}</span></div>`;

  optionList.innerHTML = optionTag;
}
