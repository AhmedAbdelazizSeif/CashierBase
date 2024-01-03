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
                tableRow.classList.add('item-row');

                // Add the item details to the table row
                tableRow.innerHTML = `
                <td style="display: none" class="item-barcode">${itemData.ean}</td>
                <td class="item-name">${itemData.name}</td>
                <td><input type="number" min="1" value="1" class="no-spinner border-0 block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer " onchange="updateItemTotalPrice(this)"></td>
                <td class="item-price">${itemData.price}</td>
                <td><span class="total-price-item">${itemData.price}</span></td>
                <td>
                    <a class="inline-flex items-center rounded-md px-2 text-sm font-semibold leading-5 text-white bg-red-500 hover:bg-red-700 focus:outline-none focus:shadow-outline w-6 h-6" onclick="deleteItem(this);this.parentNode.parentNode.remove(); updateTotalValue();">
                        <object data="${deleteIconUrl}" class="mx-auto" type="image/svg+xml" width="16" height="16"></object>
                    </a>
                </td>
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
    // Update the total price element for the item with the new total price
    element.parentNode.parentNode.querySelector('.total-price-item').textContent = parseFloat(element.value) * parseFloat(element.parentNode.parentNode.querySelector('.item-price').textContent);

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


// function to get the invoice details with each item quantities without sending to the server


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
var selectedCustomerId = null; // Global variable to store the customer ID

function getCustomerDetails() {

    var mobileNumber = $('#mobile').val();

    // Clear customer data on empty input
    if (!mobileNumber) {
        customerData = {};
        selectedCustomerId = null;
        clearCustomerFields();
        return;
    }

    // Send AJAX request for customer data
    $.ajax({
        url: customerSearchUrl + mobileNumber, method: "GET", success: function (data) {
            // Populate customer data
            selectedCustomerId = data.id;
            console.log("Selected customer id updated to"+selectedCustomerId)
            $("#first_name").val(data.first_name.split(" ")[0]);
            $("#last_name").val(data.last_name.split(" ")[1]);
            $("#street_address").val(data.address);
            $("#landline").val(data.phone2);
        }, error: function (xhr, status, error) {
            if (xhr.status === 404) {
                selectedCustomerId = null;
                clearCustomerFields();
            }
        }
    });
}

function clearCustomerFields() {
    $("#first_name, #last_name, #street_address, #landline").val("");
}

function submitNewCustomer() {
    // Get the CSRF token from the hidden input field
    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

    const customerData = {
        'first_name': $('#first_name').val(),
        'last_name': $('#last_name').val(),
        'phone': $('#mobile').val(),
        'phone2': $('#landline').val(),
        'address': $('#street_address').val(),
        'change': $('#change').val(),
        'debt': $('#debt').val()
    };

    $.ajax({
        url: '/new_customer/',
        method: 'POST',
        data: customerData,
        beforeSend: function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken); // Include the CSRF token in the AJAX request
        },
        success: function(response) {
            selectedCustomerId = response.customer_id;
            console.log("New customer created with ID:", selectedCustomerId);
        },
        error: function(error) {
            console.error("Error creating new customer:", error);
        }
    });
}

$('#submit-user').on('click', function(event) {
    event.preventDefault();
    submitNewCustomer();
});



function getInvoiceDetails() {
    let invoiceDetails = {products: {}, customer: selectedCustomerId};

    // Invoice Details filling
    for (let i = 0; i < items.length; i++) {
        const itemBarcode = items[i];
        if (itemBarcode === '') {
            continue
        }
        invoiceDetails.products[itemBarcode] = document.querySelectorAll('.quantity-input')[i].value;
    }
    console.log(invoiceDetails)
    // Set the value of the hidden input field
    document.getElementById('invoiceDetails').value = JSON.stringify(invoiceDetails);

    // Submit the form
    document.getElementById('invoiceForm').submit();


}


