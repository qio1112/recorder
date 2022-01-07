function setTextValueToId(id, text) {
    let element = document.getElementById(id)
    element.textContent = text
}

// newDiv = document.createELement("div")
// divList.appendChild(newDiv)

const INVALID_LABEL_NAME_CHARS = ['|', '=', '[', ']', '{', '}', ',', '\'', '\"']
const TAROT_NAMES = ['00_the_fool', '01_the_magician', '02_the_high_priestess', '03_the_empress', '04_the_emperor',
               '05_the_hierophant', '06_the_lovers', '07_the_chariot', '08_strength', '09_the_hermit',
               '10_wheel_of_fortune', '11_justice', '12_the_hanged_man', '13_death', '14_temperance',
               '15_the_devil', '16_the_tower', '17_the_star', '18_the_moon', '19_the_sun',
               '20_judgement', '21_the_world',

               'cup_01', 'cup_02', 'cup_03', 'cup_04', 'cup_05', 'cup_06', 'cup_07', 'cup_08', 'cup_09', 'cup_10',
               'cup_11_page', 'cup_12_knight', 'cup_13_queen', 'cup_14_king',

               'pentacle_01', 'pentacle_02', 'pentacle_03', 'pentacle_04', 'pentacle_05', 'pentacle_06', 'pentacle_07',
               'pentacle_08', 'pentacle_09', 'pentacle_10', 'pentacle_11_page', 'pentacle_12_knight',
               'pentacle_13_queen', 'pentacle_14_king',

               'sword_01', 'sword_02', 'sword_03', 'sword_04', 'sword_05', 'sword_06', 'sword_07', 'sword_08',
               'sword_09', 'sword_10', 'sword_11_page', 'sword_12_knight', 'sword_13_queen', 'sword_14_king',

               'wand_01', 'wand_02', 'wand_03', 'wand_04', 'wand_05', 'wand_06', 'wand_07', 'wand_08',
               'wand_09', 'wand_10', 'wand_11_page', 'wand_12_knight', 'wand_13_queen', 'wand_14_king']

function appendNewSelectedLabel(labelName, createNew) {
    if (labelName) {
        deleteElementById("label-selection-error")
        let labelsSelectedArea = document.getElementById("labels-selected-area")
        let newLabelSelectedDivId = "selected-" + labelName
        let errorMessage = ""
        if (INVALID_LABEL_NAME_CHARS.some(c => labelName.includes(c))) {
            errorMessage = "Label name cannot contain |, =, [, ], {, }, comma, quote"
        }
        else if (!createNew && !existing_labels.includes(labelName)) {
            errorMessage = "Invalid label: " + labelName
        }
        else if (elementContainsChildId(labelsSelectedArea, newLabelSelectedDivId)) {
            errorMessage = "Label " + labelName + " already selected"
        }

        if (errorMessage) {
            let errorP = document.createElement("div")
            errorP.textContent = errorMessage
            errorP.classList.add("error-message")
            errorP.id = "label-selection-error"
            document.getElementById("filter-label-selections").appendChild(errorP)
            return
        } else {
            deleteElementById("label-selection-error")
        }
        let labelSelectedDiv = document.createElement("div")
        if (existing_labels.includes(labelName)) {
            labelSelectedDiv.classList.add("label-selected")
            if (TAROT_NAMES.includes(labelName)) {
                labelSelectedDiv.classList.add("label-selected-tarot")
            }
        }
        else {
            labelSelectedDiv.classList.add("label-selected-new")
        }
        labelSelectedDiv.id = newLabelSelectedDivId
        let labelNameDiv = document.createElement("div")
        labelNameDiv.textContent = labelName
        let labelDeleteButton = document.createElement("a")
        labelDeleteButton.classList.add("delete-selected-label")
        labelDeleteButton.href = "#"
        labelDeleteButton.onclick = function() {
            deleteElementById(newLabelSelectedDivId)
        }
        labelSelectedDiv.insertAdjacentElement("beforeend", labelNameDiv)
        labelSelectedDiv.insertAdjacentElement("beforeend", labelDeleteButton)
        labelsSelectedArea.appendChild(labelSelectedDiv)
    }
}

function deleteElementById(id) {
    let element = document.getElementById(id)
    if (element) {
        element.parentElement.removeChild(element)
    }
}

function elementContainsChildId(parentElement, childId) {
    if (parentElement) {
        return parentElement.querySelector('#' + childId) != null
    }
    return false
}

function addSelectedLabelByOption() {
    let labelName = document.getElementById("select-label-select").value
    appendNewSelectedLabel(labelName, false)
}

function addSelectedLabelByText() {
    let labelName = document.getElementById("select-label-text").value
    document.getElementById("select-label-text").value = ""
    appendNewSelectedLabel(labelName, false)
}

function addSelectedLabelByTextForNewRecord() {
    let labelName = document.getElementById("select-label-text").value
    document.getElementById("select-label-text").value = ""
    appendNewSelectedLabel(labelName, true)
}

function submitFilterForm(url) {
    let selectedLabelNames = getSelectedLabels()
    const query = "?labels=" + JSON.stringify(selectedLabelNames)
    const filter_url = url + query
    window.location.replace(filter_url)
}

function getSelectedLabels() {
    let selectedLabelDivs = document.getElementById("labels-selected-area").children
    let selectedLabelNames = []
    if (selectedLabelDivs) {
        for (let i = 0; i < selectedLabelDivs.length; i ++) {
            let selectedLabelDiv = selectedLabelDivs.item(i)
            selectedLabelNames.push(selectedLabelDiv.querySelector("div").textContent)
        }
    }
    return selectedLabelNames
}

function callAjax(url, callback, method, formData){
    let request = new XMLHttpRequest();
    request.onreadystatechange = function(){
        if (request.readyState == 4 && request.status == 200){
            callback(request);
        }
    }
    request.open(method, url, true);
    request.setRequestHeader('X-CSRFToken', csrftoken)
    request.send(formData);
}

function submitAddRecordForm(url) {
    let addRecordForm = new FormData(document.getElementById("add-edit-record-form"))
    let selectedLabelNames = getSelectedLabels()
    addRecordForm.set("labels", JSON.stringify(selectedLabelNames))
    callAjax(url, function(request) {
        window.location.replace(request.responseURL)
    }, 'POST', addRecordForm)
}



function submitEditRecordForm(url) {

}
