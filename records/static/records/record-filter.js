const INVALID_LABEL_NAME_CHARS = ['|', '=', '[', ']', '{', '}', ',', '\'', '\"']
const INVALID_LABEL_NAMES = ['NULL']

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
            newTarotImageLi.classList.add("draggable")
            newTarotImageLi.draggable = true
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
            addListenersToDraggable(newTarotImageLi)
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

function addSelectedLabelByText(create_new) {
    let labelName = document.getElementById("select-label-text").value
    if (labelName && !EXISTING_LABELS.includes(labelName)) {
        // update EXISTING_LABELS by AJAX
        callAjax(LABEL_AJAX_URL + labelName, function(request) {
            console.log(JSON.parse(request.response))
            let label_info = JSON.parse(request.response)
            if (label_info) {
                if (label_info["label_name"]) {
                    EXISTING_LABELS.push(label_info["label_name"])
                    if (label_info["type"] === "TAROT") {
                        TAROT_LABELS.push(label_info["type"])
                    }
                }
            }
            document.getElementById("select-label-text").value = ""
            appendNewSelectedLabel(labelName, create_new)
        }, "GET", {})
    } else if (labelName && EXISTING_LABELS.includes(labelName)) {
        document.getElementById("select-label-text").value = ""
        appendNewSelectedLabel(labelName, create_new)
    }
}

function submitFilterForm(url) {
    let selectedLabelNames = getSelectedLabels()
    let selectedRecordTitleFraction = document.getElementById("select-record-title").value;
    const query = "?labels=" + JSON.stringify(selectedLabelNames) + "&record-title=" + selectedRecordTitleFraction
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
    addRecordForm.set("metadata", JSON.stringify({"tarot_card_order": getTarotImageList()}))
    callAjax(url, function(request) {
        window.location.replace(request.responseURL)
    }, 'POST', addRecordForm)
}

function getTarotImageList() {
    let tarotImagesUl = document.getElementById("tarot-images")
    let tarotOrder = []
    if (tarotImagesUl) {
        let tarotImages = tarotImagesUl.children
        for (let i = 0; i < tarotImages.length; i ++) {
            let tarotImageLi = tarotImages[i]
            tarotOrder.push(tarotImageLi.querySelector('p').textContent)
        }
    }
    return tarotOrder
}

function searchLabelLike() {
    let fragment = document.getElementById("label-like-filter-input").value
    console.log("fragment: " + fragment)
    if (!fragment) {
        fragment = "NULL"
    }
    if (fragment) {
        callAjax(LABEL_LIST_AJAX_URL + fragment, function(request) {
            console.log(JSON.parse(request.response))
            let labels_response = JSON.parse(request.response)['labels']
            if (labels_response) {
                let label_selection = document.getElementById("select-label-select")
                removeAllChildNodes(label_selection)
                let placeholderOption = document.createElement("option")
                placeholderOption.disabled = true
                placeholderOption.selected = true
                placeholderOption.value = ""
                placeholderOption.textContent = "Select Label"
                label_selection.insertAdjacentElement("beforeend", placeholderOption)
                for (let i = 0; i < labels_response.length; i ++) {
                    let label = labels_response[i]
                    // generate new select options
                    let labelOption = document.createElement("option")
                    labelOption.value = label["name"]
                    labelOption.textContent = label["name"]
                    label_selection.insertAdjacentElement("beforeend", labelOption)
                    // update EXISTING_LABELS and TAROT_LABELS (and more) lists
                    if (!EXISTING_LABELS.includes(label["name"])) {
                        EXISTING_LABELS.push(label["name"])
                    }
                    if (label["type"] === "TAROT" && !TAROT_LABELS.includes(label["name"])) {
                        TAROT_LABELS.push(label["name"])
                    }
                }
            }
        }, 'GET', {})
    }
}

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

function redirectToPage(pageNum) {
    let href = window.location.href;
    let newQueries = [];
    let url = href.split("?")[0]
    if (href.includes("?")) {
        let queries = href.split("?")[1].split("&");
        queries.forEach(query => {
            if (!query.startsWith("page=")) {
                newQueries.push(query);
            }
        });
    }
    newQueries.push("page=" + pageNum);
    let newQueryStr = "?" + newQueries.join("&");
    window.location.href = url + newQueryStr;
}