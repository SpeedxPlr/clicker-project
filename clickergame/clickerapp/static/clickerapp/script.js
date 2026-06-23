
function refreshUI(data) {

    console.log("Refreshing");
    console.log(data);


    if (data.score !== undefined) {

        document.getElementById("score").textContent =
            data.score;

        const button =
            document.getElementById(
                "prestige-button"
            );

        if (button) {

            if (data.score < 10000) {

                button.textContent =
                    `Need ${10000-data.score} more rocks`;

            }

            else {

                button.innerHTML =
                    `Prestige for <b>${data.next_crystals}</b>💎`;

            }

        }

    }


    if (data.crystals !== undefined) {

        document.getElementById("crystals")
            .textContent =
            data.crystals;

    }

    if(data.asteroids !== undefined){

    document.getElementById("asteroids")
        .textContent =
        data.asteroids;

    }


    if (data.ppc !== undefined) {

        document.getElementById("ppc")
            .textContent =
            data.ppc;

    }

    if(data.asteroids !== undefined){

    document.getElementById("asteroids")
        .textContent =
        data.asteroids;

    }

    const asteroidButton = document.getElementById(
    "asteroid-button"
);


    if(

        asteroidButton &&

        data.next_asteroids !== undefined

    ){

        asteroidButton.innerHTML =

            `Ascend for <b>${data.next_asteroids}</b>☄️`;

    }

    if (data.upgrades) {

        data.upgrades.forEach(upgrade => {

            const card =
                document.querySelector(

                    `.upgrade[data-id="${upgrade.id}"]`

                );

            if (!card) return;

            card.querySelector(".level")
                .textContent =
                upgrade.level;


            card.querySelector(".cost")
                .textContent =
                upgrade.cost;

        });

    }

}

document.addEventListener("DOMContentLoaded", function () {
const button = document.getElementById("click-button");

if (button) {

    button.addEventListener("click", function () {

        fetch("/add/")
            .then(res => res.json())
            .then(data => {

                refreshUI(data);



                createFloatingText("+" + data.reward);

            });
    });

}
});


document.addEventListener("DOMContentLoaded", () => {

    const buttons = document.querySelectorAll(".buy-btn");

    buttons.forEach(button => {

        button.addEventListener("click", () => {

            const upgradeId =
                button.closest(".upgrade").dataset.id;

            console.log("Clicked", upgradeId);

            buyUpgrade(upgradeId, button);

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

        refreshUI(data);

    }

    else {

        alert(data.error);

    }

}

async function prestige(){


    const response = await fetch("/prestige/");


    const data = await response.json();

    if(data.success){refreshUI(data);}
    };


document.addEventListener("DOMContentLoaded", ()=>{
document.querySelectorAll(".buy-max-btn").forEach(button=>{

    button.addEventListener("click",()=>{

        const id = button.closest(".upgrade").dataset.id;

                console.log("BUY MAX CLICKED");

        buyMax(id);

    });

});
});



document.getElementById("asteroid-button")
    ?.addEventListener("click", asteroidReset);

async function asteroidReset(){

     if(

        !confirm(

            "Ascend? This will reset Rocks, Crystals and their upgrades."

        )

    ){

        return;

    }

    const response = await fetch(

        "/asteroid-reset/"

    );


    const data = await response.json();


    if(data.success){

        refreshUI(data);

    }

    else{

        alert(data.error);

    }

}


async function buyMax(id){

    const response = await fetch(

        `/buy-max/${id}/`

    );

    const data = await response.json();

    if(data.success){

        refreshUI(data);

    }
}

// update every second


document.getElementById("prestige-button").addEventListener("click",prestige);
setInterval(async () => {

    const response = await fetch("/auto-click/");
    const data = await response.json();

        refreshUI(data);
    

}, 1000);