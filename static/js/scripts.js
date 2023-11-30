const progressBar = document.querySelector(".progress-bar"),
    progressText = document.querySelector(".progress-text");

const progress = (value, time) => {
    const percentage = (value / time) * 100;
    progressBar.style.width = `${percentage}%`;
    progressText.innerHTML = value;
};

let questions = [],
    time = 30,
    score = 0,
    currentQuestion,
    timer;

const startBtn = document.querySelector("#start"),
    numQuestions = document.querySelector("#num-questions"),
    Category = document.querySelector("#category"),
    difficulty = document.querySelector("#difficulty"),
    timePerQuestion = document.querySelector("#time"),
    quiz = document.querySelector("#quiz"),
    startScreen = document.querySelector(".start-screen");

const startQuiz = () => {
    const num = numQuestions.value;
    const cat = Category.value;
    const diff = difficulty.value;
    time = parseInt(timePerQuestion.value);
    // Reemplaza la URL de la API con la correcta
    const url = `https://api.example.com/questions?category=${cat}&difficulty=${diff}&amount=${num}`;

    fetch(url)
        .then((res) => res.json())
        .then((data) => {
            // Asegúrate de usar la propiedad correcta de la respuesta de la API
            questions = data.results;
            startScreen.classList.add("hide");
            currentQuestion = 0;
            showQuestion();
            startTimer();
        })
        .catch((error) => {
            console.error("Error fetching questions:", error);
        });
};

startBtn.addEventListener("click", startQuiz);

const showQuestion = () => {
    const questionText = document.querySelector("#question");
    const answersWrapper = document.querySelector(".answers");
    const questionNumber = document.querySelector("#question-number");

    if (currentQuestion < questions.length) {
        const question = questions[currentQuestion];
        questionText.innerHTML = question.question;

        const answers = [...question.incorrect_answers, question.correct_answer];
        answers.sort(() => Math.random() - 0.5);

        answersWrapper.innerHTML = "";
        answers.forEach((answer) => {
            const answerDiv = document.createElement("div");
            answerDiv.className = "answer";
            answerDiv.innerHTML = `
                <span class="text">${answer}</span>
                <span class="checkbox"></span>
                <span class="icon"></span>
            `;
            answerDiv.addEventListener("click", () => {
                if (!answerDiv.classList.contains("checked")) {
                    answerDiv.classList.remove("selected");
                }
                answerDiv.classList.add("selected");
            });
            answersWrapper.appendChild(answerDiv);
        });

        questionNumber.innerHTML = `Question ${currentQuestion + 1}/${questions.length}`;
    } else {
        endQuiz();
    }
};

const startTimer = () => {
    timer = setInterval(() => {
        if (time > 0) {
            time--;
            progress(time, parseInt(timePerQuestion.value));
        } else {
            endQuiz();
        }
    }, 1000);
};

const endQuiz = () => {
    clearInterval(timer);
    // Puedes agregar lógica para mostrar la puntuación final o cualquier otra funcionalidad de fin de juego
    alert(`Quiz ended. Your score: ${score}`);
};

// Agrega lógica para manejar las respuestas del usuario y actualizar la puntuación
const answersDiv = document.querySelectorAll(".answer");
answersDiv.forEach((answer) => {
    answer.addEventListener("click", () => {
        if (!answer.classList.contains("checked")) {
            answer.classList.remove("selected");
        }
        answer.classList.add("selected");
        // Agrega aquí la lógica para verificar si la respuesta es correcta
        // y actualiza la puntuación en consecuencia
        // Puedes usar la propiedad 'correct_answer' de la pregunta actual
        // para comparar con la respuesta seleccionada por el usuario.
    });
});


