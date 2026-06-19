document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll(".buy-btn");

    console.log("Buttons found:", buttons.length);

});



document.addEventListener("DOMContentLoaded", function () {
const button = document.getElementById("click-button");

if (button) {

    button.addEventListener("click", function () {

        fetch("/add/")
            .then(res => res.json())
            .then(data => {
                document.getElementById("score").innerText = data.score;
            });

    });

}
});

document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll(".buy-btn");

    document.querySelectorAll(".buy-btn").forEach(button => {

    button.addEventListener("click", () => {

        const card = button.closest(".upgrade");

        buyUpgrade(card.dataset.id, button);

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

async function buyUpgrade(upgradeId, button) {

    console.log("Buying", upgradeId);

    const response = await fetch(
        `/buy-upgrade/${upgradeId}/`
    );

    if (!response.ok) {
        console.error(
            "Request failed:",
            response.status
        );
        return;
    }

    const data = await response.json();

    console.log(data);

    if (data.success) {

        document.getElementById("score").textContent = data.score;
        
        document.getElementById("ppc").textContent = data.ppc;

        const card = button.closest(".upgrade");


        card.querySelector(".level").textContent = data.level;


        card.querySelector(".cost").textContent = data.new_cost;
    }

    else {
        alert(data.error);
    }

}

// update every second
setInterval(updateScore, 200);