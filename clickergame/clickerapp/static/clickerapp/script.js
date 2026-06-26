
function refreshUI(data) {
    try {
    console.log("Refreshing");
    console.log(data);

    if (data.score !== undefined) {
        document.getElementById("score").textContent = data.score;
}



    if (data.score !== undefined) {

    
    

        const prestigeButton = document.getElementById("prestige-button");

        if(prestigeButton){

            if(data.score < 10000){
                prestigeButton.classList.remove("prestige-active");
                prestigeButton.classList.add("locked-button");
                prestigeButton.disabled = true;

                prestigeButton.textContent =
                    `Need ${10000-data.score} more Rocks`;

            }
            else{

                            prestigeButton.classList.remove("locked-button");
                prestigeButton.classList.add("prestige-active");
                prestigeButton.disabled = false;

                prestigeButton.innerHTML =
                    `Prestige for <b>${data.next_crystals}</b>💎`;

            }
        }

    const crystalText = document.getElementById("crystals");

    if (crystalText &&data.crystals !== undefined) 
        {crystalText.textContent =   data.crystals;}

    const asteroidText =
        document.getElementById("asteroids");


    if (
        asteroidText &&
        data.asteroids !== undefined
    ) {

        asteroidText.textContent =
            data.asteroids;

    }

    }


        const asteroidButton = document.getElementById("asteroid-button");

        if (asteroidButton) {

            if (data.score !== undefined) {

                if (data.score < 1000000) {

                    asteroidButton.classList.remove("asteroid-active");
                    asteroidButton.classList.add("locked-button");

                    asteroidButton.disabled = true;

                    asteroidButton.textContent =
                        `Need ${1000000 - data.score} more Rocks`;

                }
                else {

                    asteroidButton.classList.remove("locked-button");
                    asteroidButton.classList.add("asteroid-active");

                    asteroidButton.disabled = false;

                    asteroidButton.innerHTML =
                        `Ascend for <b>${data.next_asteroids}</b>☄️`;
                }
            }
        }
   
        if (data.upgrades) {

            data.upgrades.forEach(upgrade => {

            
            const card = document.querySelector(
                `.upgrade[data-id="${upgrade.id}"]`
            );

            if (!card) {console.log("Missing card:", upgrade.id);return;}

            const level = card.querySelector(".level");
            const cost = card.querySelector(".cost");

            if (level) {level.textContent = upgrade.level;}

            if (cost) {cost.textContent = upgrade.cost;}
        });
    }

    console.log("Finished refreshing");
        }
        catch(err){

        console.error(err);

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


    
    console.log("Prestige started");

    const response = await fetch("/prestige/");

    console.log("Response received");

    const data = await response.json();

    console.log(data);

    refreshUI(data);

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



function showCatalogue(type){

    document.querySelectorAll(".upgrade").forEach(card=>{

        card.style.display =
            card.dataset.type === type
            ? "flex"
            : "none";

    });

}

showCatalogue("rock");

document.getElementById("rocks-tab")
    .onclick = () => showCatalogue("rock");

document.getElementById("crystals-tab")
    .onclick = () => showCatalogue("crystal");

document.getElementById("asteroids-tab")
    .onclick = () => showCatalogue("asteroid");

// update every second

document.addEventListener("DOMContentLoaded", () => {

    const prestigeButton =
        document.getElementById("prestige-button");

    if(prestigeButton){

        prestigeButton.addEventListener(
            "click",
            prestige
        );

        console.log("Prestige listener attached");

    }

});
setInterval(async () => {

      try{

        const response = await fetch("/auto-click/");
        const data = await response.json();

        refreshUI(data);

    }

    catch(error){

        console.log("Autoclick failed");
        console.log(error);

    }


},1000);