import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import Nav from "react-bootstrap/Nav";
import { default as BootstrapNavbar } from "react-bootstrap/Navbar";
import NavDropdown from "react-bootstrap/NavDropdown";
import { BsRobot } from "react-icons/bs";
import { MdOutlineMonitorHeart } from "react-icons/md";
import { useState } from "react";
import Modal from "react-bootstrap/Modal";
import * as api from "../utils/api.jsx";
import * as Swal from 'sweetalert2' 

function Navbar() {
  const [fullscreen, setFullscreen] = useState(true);
  const [show, setShow] = useState(false);
  const [iframe, setIframe] = useState('https://dashboard.fburon.cl/public/dashboard/44ca336a-7977-4909-a07b-ad53eb18d9b6');

  function handleShow(breakpoint) {
    setFullscreen(breakpoint);
    const getiFrame = async () => {
      const res = await api.iframeUrl();
      const data = await res.json();
      setIframe(data.url);
    }
    getiFrame();
    setShow(true);
  }
  const handleLogout = async () => {
    const res = await api.logout();
    const data = await res.json();
    if (res.status === 200) {
      console.log(data.message);
      window.location.href = "/";
    } else {
      console.log(data.error);
    }
  };

  const changePassword = async () => {
    Swal.fire({
      title: "Change Password",
      html: `
			<input id="swal-input1" class="swal2-input" type="password" placeholder="Current Password">
			<input id="swal-input2" class="swal2-input" type="password" placeholder="New Password">
			<input id="swal-input3" class="swal2-input" type="password" placeholder="Confirm New Password">
		`,
      focusConfirm: false,
      preConfirm: () => {
        const currentPassword = document.getElementById("swal-input1").value;
        const newPassword = document.getElementById("swal-input2").value;
        const confirmNewPassword = document.getElementById("swal-input3").value;

        // Validar que los campos no estén vacíos
        if (!currentPassword || !newPassword || !confirmNewPassword) {
          Swal.showValidationMessage("All fields are required");
        }

        // Validar que la nueva contraseña y la confirmación coincidan
        if (newPassword !== confirmNewPassword) {
          Swal.showValidationMessage(
            "New password and confirmation do not match"
          );
        }

        return api
          .changePassword(currentPassword, newPassword)
          .then((res) => {
            if (res.status === 200) {
              Swal.fire({
                icon: "success",
                title: "Password changed successfully",
                showConfirmButton: false,
                timer: 1500,
              });
            } else {
              Swal.showValidationMessage("Current password is incorrect");
            }
          })
          .catch((error) => {
            console.log(error);
          });
      },
    });
  };

  return (
    <BootstrapNavbar
      collapseOnSelect
      expand="md"
      variant="dark"
      sticky="top"
      className="mb-3 w-100 "
    >
      <BootstrapNavbar.Brand className="d-flex align-items-center justify-content-center">
        <span
          style={{ cursor: "pointer" }}
          onClick={(e) => (window.location.href = "/home")}
        >
          <BsRobot fontSize="large" />
          <span className="ms-4 fw-bold ">ChatGPT Plus</span>
        </span>
      </BootstrapNavbar.Brand>

      <BootstrapNavbar.Toggle aria-controls="responsive-BootstrapNavbar-nav" />
      <BootstrapNavbar.Collapse id="responsive-BootstrapNavbar-nav">
        <Nav className="ms-auto">
          <Nav.Link className="position-relative me-3">
            <MdOutlineMonitorHeart onClick={() => handleShow(true)} />
            <Modal
              show={show}
              fullscreen={fullscreen}
              onHide={() => setShow(false)}
            >
              <Modal.Header closeButton>
                <Modal.Title>ChatGPT Usage</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <iframe
                  src={iframe}
                  width="100%"
                  height="100%"
                  allowTransparency
                />
              </Modal.Body>
            </Modal>
          </Nav.Link>
          <NavDropdown
            title={localStorage.getItem("username")}
            id="Admin-nav-dropdown"
          >
            <NavDropdown.Item onClick={() => changePassword()}>
              Change Password
            </NavDropdown.Item>
            <NavDropdown.Divider />
            <NavDropdown.Item onClick={handleLogout}>Log out</NavDropdown.Item>
          </NavDropdown>
        </Nav>
      </BootstrapNavbar.Collapse>
    </BootstrapNavbar>
  );
}

export default Navbar;
