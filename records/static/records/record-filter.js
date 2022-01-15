const INVALID_LABEL_NAME_CHARS = ['|', '=', '[', ']', '{', '}', ',', '\'', '\"']

function appendNewSelectedLabel(labelName, createNew) {
    if (labelName) {
        deleteElementByID("label-selection-error")
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
            deleteElementByID("label-selection-error")
        }
        let labelSelectedDiv = document.createElement("div")
        if (EXISTING_LABELS.includes(labelName)) {
            labelSelectedDiv.classList.add("label-selected")
            if (TAROT_LABELS.includes(labelName)) {
                labelSelectedDiv.classList.add("label-selected-tarot")
                if (typeof LABEL_AJAX_URL !== 'undefined') {
                    appendTarotImageByLabel(labelName)
                }
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
            deleteSelectedLabel(labelName)
        }
        labelSelectedDiv.insertAdjacentElement("beforeend", labelNameDiv)
        labelSelectedDiv.insertAdjacentElement("beforeend", labelDeleteButton)
        labelsSelectedArea.appendChild(labelSelectedDiv)
    }
}

function appendTarotImageByLabel(labelName) {
    callAjax(LABEL_AJAX_URL + labelName, function(request) {
        console.log(JSON.parse(request.response))
        let tarot_image_url = JSON.parse(request.response)['tarot_image_url']
        if(tarot_image_url) {
            let newTarotLiID = "tarot-image-wrapping-" + labelName
            let tarotImageListDiv = document.getElementById('tarot-images')
            let newTarotImageLi = document.createElement("li")
            newTarotImageLi.id = newTarotLiID
            newTarotImageLi.classList.add("tarot-image-cell")
            let newTarotImageNameP = document.createElement("p")
            newTarotImageNameP.textContent = labelName
            let newTarotImg = document.createElement("img")
            newTarotImg.src = tarot_image_url
            newTarotImg.classList.add("tarot-image")
            if(labelName.endsWith('_R')) {
                newTarotImg.classList.add('tarot-image-reversed')
            }
            newTarotImageLi.insertAdjacentElement("beforeend", newTarotImageNameP)
            newTarotImageLi.insertAdjacentElement("beforeend", newTarotImg)
            tarotImageListDiv.appendChild(newTarotImageLi)
        }
    }, 'GET', {})
}

function deleteElementByID(id) {
    let element = document.getElementById(id)
    if (element) {
        element.parentElement.removeChild(element)
    }
}

function deleteSelectedLabel(labelName) {
    let selectedLabelDivID = "selected-" + labelName
    deleteElementByID(selectedLabelDivID)
    if(TAROT_LABELS.includes(labelName)) {
        let selectedTarotImageLiID = "tarot-image-wrapping-" + labelName
        deleteElementByID(selectedTarotImageLiID)
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
    console.log("Ajax call to " + url + " method " + method)
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
