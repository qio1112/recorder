let dragTarget = null
let dragSource = null

let draggables = document.querySelectorAll(".draggable")
let dragContainer = document.querySelector(".draggable-container")

draggables.forEach(draggable => {
    addListenersToDraggable(draggable)
})

function addListenersToDraggable(draggable) {
    if (draggable) {
        draggable.addEventListener('dragstart', () => {
        console.log('dragstart')
        dragSource = draggable
        draggable.classList.add('dragging')
    })

    draggable.addEventListener('dragover', (e) => {
        e.preventDefault()
    })

    draggable.addEventListener('dragenter', (e) => {
        console.log('dragenter')
        if (draggable.id !== e.target.id) {
            draggable.classList.add('dragover')
            dragTarget = draggable
        }
    })

    draggable.addEventListener('dragleave', (e) => {
        console.log('dragleave')
        if (draggable.id !== e.target.id) {
            draggable.classList.remove('dragover')
            dragTarget = null
        }
    })

    draggable.addEventListener('drop', (e) => {
        e.preventDefault()
        console.log('drop')
        if (dragTarget != null && dragSource != null && dragTarget.id !== dragSource.id) {
            swapDraggable(dragSource, dragTarget)
        }
        endDragging(dragSource)
        endDragging(dragTarget)
    })

    draggable.addEventListener('dragend', () => {
        endDragging(dragSource)
        endDragging(dragTarget)
    })
    }
}

function endDragging(node) {
    if (node) {
        node.classList.remove('dragging')
        node.classList.remove('dragover')
    }
    node = null
}

function swapDraggable(d1, d2) {
    console.log("swapping")
    const parentNode = d1.parentNode
    let clonedD1 = d1.cloneNode(true);
    let clonedD2 = d2.cloneNode(true);
    addListenersToDraggable(clonedD1)
    addListenersToDraggable(clonedD2)
    parentNode.replaceChild(clonedD1, d2);
    parentNode.replaceChild(clonedD2, d1);
    endDragging(clonedD1)
    endDragging(clonedD2)
}