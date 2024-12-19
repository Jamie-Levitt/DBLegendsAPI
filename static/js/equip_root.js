/*#region DATABASE*/
async function syncDBTime() {
    fetch('/API/localtime')
    .then((response) => response.json)
    .then((r) => {
        localStorage.setItem("EquipsLastUpdated", r.localtime);
        return;
    })
}

async function overrideEquipData() {
    console.log('syncing')
    fetch('/API/equipment')
    .then((response) => response.json())
    .then((data) => {
        console.log(data)
        localStorage.setItem("EquipmentData", JSON.stringify(data));
        syncDBTime();
        return;
    })
}

function affirmSyncDate() {
    const equipData = JSON.parse(localStorage.getItem("EquipmentData") || "[]");
    console.log(equipData)
    fetch('/API/lastsync')
    .then((response) => response.json)
    .then((r) => {
        var lastSync = new Date(parseInt(localStorage.getItem("EquipsLastUpdated"), 10));
        if (lastSync <= Date.parse(r.lastsync) || equipData == null || equipData.length == 0) {overrideEquipData();}
        return;
    })
}

function genEquipListItem(equipID, equipName, equipRarity, equipImgPath, is_ToP, conditions, effects) {
    const ref = document.querySelector("#equipment-list-item");
    const clone = ref.content.cloneNode(true);
    clone.querySelector(".equip-list-item").href = "/equipment/" + equipID.toString();
    clone.querySelector(".equip-list-item-main").id = equipID.toString();
    if (is_ToP == true) { clone.querySelector(".equip-list-item-main").classList.add('ToP') }
    clone.querySelector(".equip-name").textContent = equipName;
    clone.querySelector(".equip-img-div").classList.add(equipRarity.toString());
    clone.querySelector(".equip-img").src = "static/assets/" + equipImgPath;
    const conBox = clone.querySelector(".equip-conditions")
    for (const con of conditions) {
        if (Array.isArray(con)) {
            const subBox = document.createElement("div");
            subBox.classList.add("trait-andbox");
            for (const c of con) {
                const conElement = document.createElement("a")
                conElement.classList.add(c.rarity);
                conElement.href = "/trait/" + c.id;
                conElement.textContent = c.name;
                subBox.append(conElement);
            }
            conBox.append(subBox);
        } else {
            const conElement = document.createElement("a")
            conElement.classList.add(c.rarity);
            conElement.href = "/trait/" + c.id;
            conElement.textContent = c.name;
            conBox.append(subBox);
        }
    }
    const effectBox = clone.querySelector(".equip-stats")
    for (const effect in effects) {
        const effectEl = document.createElement("a");
        effectEl.classList.add("effect");
        effectEl.textContent = effect;
        effectBox.append(effectEl);
    }
    return clone;
}

function updateEquipDisplay() {
    //localStorage.removeItem("EquipmentData")
    affirmSyncDate();
    const equipData = JSON.parse(localStorage.getItem("EquipmentData") || "[]");
    const equipListBox = document.querySelector("#equipment-list");
    equipListBox.innerHTML = '';
    for (var equip of equipData) {
        console.log(equip['id'], equip['name'], equip['rarity'], equip['img_path'], equip['is_ToP'], equip['conditions'], equip['effects'])
        const equipItem = genEquipListItem(equip['id'], equip['name'], equip['rarity'], equip['img_path'], equip['is_ToP'], equip['conditions'], equip['effects']);
        equipListBox.append(equipItem);
    }
}

/*#endregion*/