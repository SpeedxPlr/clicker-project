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

document.querySelectorAll(".buy-btn").forEach(button => {
    button.addEventListener("click", () => {
        buyUpgrade(button.dataset.id);
    });
});

function updateScore() {
    fetch("/get-score/")
        .then(response => response.json())
        .then(data => {
            document.getElementById("score").innerText = data.score;
        });
}

async function buyUpgrade(upgradeId) {
    const response = await fetch(`/buy-upgrade/${id}/`);

    if (!response.ok) {
        console.error("Request failed:", response.status);
        return;
    }

    const data = await response.json();

    console.log(data);

    if (data.success) {
        document.getElementById("score").textContent =
            data.score;
    } else {
        alert(data.error);
    }
}


// update every second
setInterval(updateScore, 16);