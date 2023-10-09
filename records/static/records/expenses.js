function getQuery() {
    return null
}

function loadExpensesData(action) {
    const pageNumberInput = document.getElementById("pageNumberInput")
    const url = DATA_QUERY_AJAX_URL
    const input_page = parseInt(pageNumberInput.value)
    let newPage = input_page;
    if (action === "prev") {
        newPage = input_page - 1
    } else if (action === "next") {
        newPage = input_page + 1
    } else if (action === "onload") {
        newPage = 1
    }

    const query = getQuery()
    const urlWithQueries = url + "?query=" + query + "&page=" + newPage
    callAjax(urlWithQueries, function(request) {
        // console.log(JSON.parse(request.response))
        const response = JSON.parse(request.response)
        const data = JSON.parse(response["data"])
        const columns = response["columns"]
        const numPages = response["num_pages"]
        const actualPage = response["page"]
        // update table html
        const dataTable = document.getElementById("data-table")
        // table head
        const newTableHead = document.createElement("thead")
        newTableHead.classList.add("table-head")
        const tableHeadTr = document.createElement("tr")
        for (let i = 0; i < columns.length; i ++) {
            const nextColumnName = columns[i]
            const nextTh = document.createElement("th")
            nextTh.classList.add("table-head0cell")
            nextTh.scope = "col"
            nextTh.innerText = nextColumnName
            tableHeadTr.insertAdjacentElement("beforeend", nextTh)
        }
        newTableHead.insertAdjacentElement("beforeend", tableHeadTr)
        const dataTableHead = document.getElementById("table-head")
        dataTable.replaceChild(newTableHead, dataTableHead)
        newTableHead.id = "table-head"
        // table body
        const newTableBody = document.createElement("tbody")
        if (!data || data.length === 0) {
            const emptyTr = document.createElement("tr")
            for (let j = 0; j < columns.length; k ++) {
                const emptyTd = document.createElement("td")
                emptyTd.classList.add("table-cell")
                emptyTr.insertAdjacentElement("beforeend", emptyTd)
            }
            newTableBody.insertAdjacentElement("beforeend", emptyTr)
        }
        for (let i = 0; i < data.length; i ++) {
            const nextTr = document.createElement("tr")
            const nextDataRow = data[i]
            for (let j = 0; j < columns.length; j ++) {
                const nextData = nextDataRow[j]
                const nextTd = document.createElement("td")
                nextTd.classList.add("table-cell")
                nextTd.innerText = nextData
                nextTr.insertAdjacentElement("beforeend", nextTd)
            }
            newTableBody.insertAdjacentElement("beforeend", nextTr)
        }
        const dataTableBody = document.getElementById("data-table-body")
        dataTable.replaceChild(newTableBody, dataTableBody)
        newTableBody.id = "data-table-body"
        const pageNumberInput = document.getElementById("pageNumberInput")
        pageNumberInput.value = actualPage
        const previousButton = document.getElementById("prevBtn")
        const nextButton = document.getElementById("nextBtn")
        if (actualPage === 1) {
            previousButton.classList.add("button-disabled")
        } else {
            previousButton.classList.remove("button-disabled")
        }
        if (actualPage === numPages) {
            nextButton.classList.add("button-disabled")
        } else {
            nextButton.classList.remove("button-disabled")
        }
        // update max page
        const maxPage = document.getElementById("max-pages")
        maxPage.innerText = "Max: " + numPages
        console.log("showing data for page " + actualPage)
    }, "GET", null)
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


document.addEventListener('DOMContentLoaded', function() {
   loadExpensesData("onload")
}, false);
