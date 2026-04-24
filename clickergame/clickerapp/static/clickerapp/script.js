document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById("click-button");
    const scoreDisplay = document.getElementById("score");

    button.addEventListener("click", function () {
            fetch("/add/")
                .then(res => res.json())
                .then(data => {
                    document.getElementById("score").innerText = data.score;
            });
    });
});

function updateScore() {
    fetch("/get-score/")
        .then(response => response.json())
        .then(data => {
            document.getElementById("score").innerText = data.score;
        });
}

// update every second
setInterval(updateScore, 16);