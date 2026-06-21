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

                document.getElementById("score").innerText =
                    data.score;


                createFloatingText("+" + data.reward);

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


function createFloatingText(text) {

    const area = document.getElementById("click-area");

    const element = document.createElement("div");

    element.className = "floating-text";

    element.textContent = text;


    element.style.left =
    (Math.random()*100) + "%";


    element.style.top =
        "50px";


    area.appendChild(element);


    setTimeout(() => {
        element.remove();
    }, 1000);

}



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

    async function prestige(){


    const response =

    await fetch(

    "/prestige/"

    );


    const data =

    await response.json();


    if(data.success){


    alert(

    `+${data.gained} crystals`

    );


    document.getElementById(

    "crystals"

    ).textContent =

    data.crystals;


    }
    }

document.getElementById("prestige-btn").addEventListener("click",prestige);



// update every second
setInterval(updateScore, 200);