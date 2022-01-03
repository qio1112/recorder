function setTextValueToId(id, text) {
    let element = document.getElementById(id)
    element.textContent = text
}

// newDiv = document.createELement("div")
// divList.appendChild(newDiv)

function appendNewSelectedLabel(labelName) {
    if (labelName) {
        deleteElementById("label-selection-error")
        let labelsSelectedArea = document.getElementById("labels-selected-area")
        let newLabelSelectedDivId = labelName + "-selected"
        let errorMessage = ""
        if (!labels.includes(labelName)) {
            errorMessage = "Invalid label: " + labelName
        }
        else if (elementContainsChildId(labelsSelectedArea, newLabelSelectedDivId)) {
            errorMessage = "Label " + labelName + " already selected"
        }
        if (errorMessage) {
            let errorP = document.createElement("p")
            errorP.textContent = errorMessage
            errorP.classList.add("error-message")
            errorP.id = "label-selection-error"
            document.getElementById("filter-label-selections").appendChild(errorP)
            return
        } else {
            deleteElementById("label-selection-error")
        }
        let labelSelectedDiv = document.createElement("div")
        labelSelectedDiv.classList.add("label-selected")
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
    appendNewSelectedLabel(labelName)
}

function addSelectedLabelByText() {
    let labelName = document.getElementById("select-label-text").value
    document.getElementById("select-label-text").value = ""
    appendNewSelectedLabel(labelName)
}

function submitFilterForm(url) {
    let formData = new FormData()
    let selectedLabelDivs = document.getElementById("labels-selected-area").children
    let selectedLabelNames = []
    if (selectedLabelDivs) {
        for (let i = 0; i < selectedLabelDivs.length; i ++) {
            let selectedLabelDiv = selectedLabelDivs.item(i)
            selectedLabelNames.push(selectedLabelDiv.querySelector("div").textContent)
        }
    }
    const query = "?labels=" + JSON.stringify(selectedLabelNames)
    const filter_url = url + query
    window.location.replace(filter_url)
}
