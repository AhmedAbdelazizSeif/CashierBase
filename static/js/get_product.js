items = [];

// Create a function to get the item details and add it to the table
function updateTotalValue() {
    // Calculate the total value of the invoice
    let totalValue = 0;
    document.querySelectorAll('.total-price-item').forEach(element => {
        totalValue += parseFloat(element.textContent);
    });

    // Update the total value of the invoice
    document.getElementById('total-value').textContent = totalValue;
}

function onKeyDown(event) {
    console.log('here')
    const textbox = event.target;
    if (event.key === 'Enter') {
        event.preventDefault();
        // Press the button.
        const button = document.querySelector('#add-item');
        button.click();
    }
}

function findRowByBarcode(barcode) {
    const barcodeElements = document.querySelectorAll('.item-barcode');

    for (const element of barcodeElements) {
        if (element.textContent === barcode) {
            // Return the parent row element
            return element.closest('tr');
        }
    }

    return null; // Barcode not found
}


function addItem() {
    // Get the item barcode
    let barcodeGet = document.getElementById('item-barcode');
    const itemBarcode = barcodeGet.value;

    // Check if the barcode is already in the items array
    if (items.includes(itemBarcode)) {
        const existingRow = findRowByBarcode(itemBarcode);

        if (existingRow) {
            // The item is already in the table
            const quantityInput = existingRow.querySelector('.quantity-input');
            quantityInput.value = parseInt(quantityInput.value) + 1;
            updateItemTotalPrice(quantityInput);
        }
        barcodeGet.value = '';
    } else {
        items.push(itemBarcode);

        // Make an AJAX request to get the item details
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/get_item_details/${itemBarcode}/`);
        xhr.onload = function () {
            if (xhr.status === 200) {
                // Get the item details from the response
                const itemData = JSON.parse(xhr.responseText);

                // Create a new table row for the item
                const tableRow = document.createElement('tr');
                tableRow.classList.add('item-row')

                // Add the item details to the table row
                tableRow.innerHTML = `
            <td style="display: none" class="item-barcode">${itemData.ean}</td>
          <td class="item-name">${itemData.name}</td>
          <td><input type="number" min="1" value="1" class="quantity-input" onchange="updateItemTotalPrice(this)"></td>
          <td class="item-price">${itemData.price}</td>
          <td><span class="total-price-item">${itemData.price}</span></td>
            <td><a class="inline-flex items-center rounded-md px-2 text-sm font-semibold leading-5 text-white bg-red-500 hover:bg-red-700 focus:outline-none focus:shadow-outline" onclick="deleteItem(this);this.parentNode.parentNode.remove(); updateTotalValue();"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
      <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6Z"/>
      <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z"/>
    </svg></a></td>
        `;

                // Add the table row to the table
                document.getElementById('invoice-items').appendChild(tableRow);

                // Update the total value
                updateTotalValue();
            } else {
                // Handle error
                console.error(xhr.statusText);
            }
        };
        xhr.send();
        barcodeGet.value = '';
    }

}

// Add an event listener to the add item button
// document.getElementById('add-item').addEventListener('click', addItem);

function updateItemTotalPrice(element) {
    // Calculate the new total price for the item
    const newTotalPrice = parseFloat(element.value) * parseFloat(element.parentNode.parentNode.querySelector('.item-price').textContent);

    // Update the total price element for the item with the new total price
    element.parentNode.parentNode.querySelector('.total-price-item').textContent = newTotalPrice;

    // Update the total value of the invoice
    updateTotalValue();
}

function updateChange(element) {
    // Calculate the change
    const change = parseFloat(element.value) - parseFloat(document.getElementById('total-value').textContent);

    // Update the change element with the new change
    if (change) document.getElementById('change').textContent = change.toString(); else document.getElementById('change').textContent = 0;
}

// function to delete item from the items array
function deleteItem(button) {
    console.log(items)
    // Get the item barcode from the previous row (assuming it's the previous sibling)
    const row = button.parentNode.parentNode;
    const barcodeElement = row.querySelector('.item-barcode');
    const itemBarcode = barcodeElement.textContent; // or .innerText, .innerHTML, etc.

    // Delete the item from the items array
    items.splice(items.indexOf(itemBarcode), 1);
    console.log(items)
}


function printDiv(divName) {
    var printContents = document.getElementById(divName).innerHTML;
    var originalContents = document.body.innerHTML;

    document.body.innerHTML = printContents;

    window.print();

    document.body.innerHTML = originalContents;

}


// function to get the invoice details with each item quantities without sending to the server
function getInvoiceDetails() {
    let invoiceDetails = {};
    /* const table = document.querySelector('table')
    const tableRows = table.rows
    let panel_table = document.getElementById('invoice-items-panel')

    for (let i = 1; i < tableRows.length; i++) {
        const row = tableRows[i];
        const rowCells = row.cells
        let panel_row = document.createElement('tr')
        for (let j = 1; j < rowCells.length - 1; j++) {
            const cell = rowCells[j];
            let panel_cell = document.createElement('td')
            // check if the cell is a quantity input if so just take out its value
            if (cell.querySelector('.quantity-input')) {
                panel_cell.innerHTML = cell.querySelector('.quantity-input').value
                panel_row.appendChild(panel_cell)
                continue
            }
            panel_cell.innerHTML = cell.innerHTML
            panel_row.appendChild(panel_cell)
        }
        panel_table.appendChild(panel_row)
    }
    let print_panel = document.getElementById('print-panel')

    const data ={element: print_panel.outerHTML}
    jQuery.post('/print/', data, function (response) {
        console.log(response)
    });*/


    // Invoice Details filling
    for (let i = 0; i < items.length; i++) {
        const itemBarcode = items[i];
        const itemQuantity = document.querySelectorAll('.quantity-input')[i].value;
        invoiceDetails[itemBarcode] = itemQuantity;
    }
    console.log(invoiceDetails)
    // Set the value of the hidden input field
    document.getElementById('invoiceDetails').value = JSON.stringify(invoiceDetails);

    // Submit the form
    document.getElementById('invoiceForm').submit();


}

function testPdf() {
    //send the div to PDF
    html2canvas($("#print-panel"), { // DIV ID HERE
        onrendered: function (canvas) {
            var imgData = canvas.toDataURL('image/png');
            var doc = new jsPDF('portrait', 'in', [canvas.width, canvas.height], true);
            doc.addImage(imgData, 'PDF', 10, 10);
            doc.save('~/data.pdf'); //SAVE PDF FILE
        }
    });

}


document.getElementById('item-barcode').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent the default form submission behavior
        // Your custom code to handle the Enter key press goes here
        const button = document.querySelector('#add-item');
        button.click();
    }
});


// Define URL for searching customer by phone number
const customerSearchUrl = "/get_customer_details/";

// Initialize customer data object
let customerData = {};


function getCustomerDetails() {

    const mobileNumber = document.getElementById("mobile").value;

    // Clear customer data on empty input
    if (!mobileNumber) {
        customerData = {};
        $("#first-name, #last-name, #street-address, #landline").val("");
        return;
    }

    // Send AJAX request for customer data
    $.ajax({
        url: customerSearchUrl + mobileNumber,
        method: "GET",
        success: function (data) {
            if (data) {
                // Populate customer data
                customerData = data;
                $("#first-name").val(data.first_name.split(" ")[0]);
                $("#last-name").val(data.last_name.split(" ")[1]);
                $("#street-address").val(data.address);
                $("#landline").val(data.phone2);
            } else {
                // Clear customer data if not found
                customerData = {};
                $("#first-name, #last-name, #street-address, #landline").val("");
            }
        },
    });
}

// Add listener for submit event on form

$("#customer-form").submit(new_customer);

function new_customer(event) {
    event.preventDefault(); // Prevent page reload

   const formData = $(this).serialize();

    $.ajax({
        url: $(this).attr("action"),
        method: "POST",
        data: formData,
        success: function(data) {
            // Handle success response
        },
        error: function(error) {
            // Handle error response
        },
    });
}


