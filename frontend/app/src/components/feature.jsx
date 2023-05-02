import Swal from 'sweetalert2';
const Feature = () => {
    Swal.fire({
        title: 'Features',
        html:
        '<ul align="left">' +
        '<li>Make custom calculations</li>' +
        '<li>Page style improvements</li>' +
        '</ul>',
        confirmButtonText: "Don't show me this again",
        confirmButtonColor: '#BB3333',
        reverseButtons: true
    }).then((result) => {
        if (result.value) {
        localStorage.setItem('dontShow', '2');
        }
    }
    )
}

export default Feature;