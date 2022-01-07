function setTextValueToId(id, text) {
    let element = document.getElementById(id)
    element.textContent = text
}

// newDiv = document.createELement("div")
// divList.appendChild(newDiv)

const INVALID_LABEL_NAME_CHARS = ['|', '=', '[', ']', '{', '}', ',', '\'', '\"']

function appendNewSelectedLabel(labelName, createNew) {
    if (labelName) {
        deleteElementById("label-selection-error")
        let labelsSelectedArea = document.getElementById("labels-selected-area")
        let newLabelSelectedDivId = "selected-" + labelName
        let errorMessage = ""
        if (INVALID_LABEL_NAME_CHARS.some(c => labelName.includes(c))) {
            errorMessage = "Label name cannot contain |, =, [, ], {, }, comma, quote"
        }
        else if (!createNew && !EXISTING_LABELS.includes(labelName)) {
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
        if (EXISTING_LABELS.includes(labelName)) {
            labelSelectedDiv.classList.add("label-selected")
            if (TAROT_LABELS.includes(labelName)) {
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
    request.setRequestHeader('X-CSRFToken', CSRF_TOKEN)
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
