const Swal = require('sweetalert2')

export function Error(message) {
    return Swal.fire({
        position: 'center',
        title: 'Error',
        text: message,
        showConfirmButton: false,
        timer: 1000,
        backdrop: false
    })
}

export function ErrorOnClose(message) {
    return Swal.fire({
        position: 'center',
        title: 'Error',
        text: message,
        showConfirmButton: false,
        timer: 1500,
        backdrop: false,
        onClose: () => {
            window.location.reload();
        }
    })
}

export function Success(message) {
    return Swal.fire({
        position: 'center',
        title: 'Success',
        text: message,
        showConfirmButton: false,
        timer: 1000,
        backdrop: false
    })
}

export function SuccessMandatoryPressOK(message, whenClose) {
    return Swal.fire({
        position: 'center',
        title: 'Success',
        text: message,
        showConfirmButton: true,
        confirmButtonText: 'OK',
        confirmButtonColor: '#BB3333',
        backdrop: false,
        onClose: () => {
            whenClose();
        }
    })
}

export function SuccessOnClose(message) {
    return Swal.fire({
        position: 'center',
        title: 'Success',
        text: message,
        showConfirmButton: false,
        timer: 1500,
        backdrop: false,
        onClose: () => {
            window.location.reload();
        }
    })
}

export function HowTo(){
    let timerInterval
    return Swal.fire({
        imageUrl: '/demostration.gif',
        imageWidth: '100%',
        imageHeight: '80%',
        imageAlt: 'Custom image',
        showConfirmButton: false,
        timer: 12000,
        title: 'How to paste data?',
        html: '<div style="text-align: left;">\
        <p>1. Copy the data from Excel or other spreadsheet software.</p>\
        <p>2. Paste the data into the text area below.</p>\
        <p>3. Click "Calculate" button.</p>',
        footer: '<div class="row"><div class="text-danger col-8">The columns must be in the following order: vCPU, vRAM.</div>\
        <div style="text-align: end;" class="col-auto"><span>Auto close in <b id="timer"></b></span></div></div>',
        timerProgressBar: true,
        didOpen: () => {
            const b = document.getElementById('timer')
            timerInterval = setInterval(() => {
                b.innerHTML = (Swal.getTimerLeft() / 1000).toFixed(1)
            }, 100)
        },
        willClose: () => {
            clearInterval(timerInterval)
        }
    })
}