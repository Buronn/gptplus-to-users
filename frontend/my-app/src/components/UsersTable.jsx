import Form from "react-bootstrap/Form";
import Spinner from "react-bootstrap/Spinner";
import Alert from "react-bootstrap/Alert";
import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import { useEffect, useState, useRef } from "react";
import * as api from "../utils/api.js";
import moment from "moment";
import Swal from "sweetalert2";

const UsersTable = (props) => {
  const { startDate, endDate, filters, checkBoxFilters, handleClose, show } =
    props;
  const formRef = useRef(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [users, setUsers] = useState({
    loading: false,
    error: false,
    data: [],
  });
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setUsers({ loading: true, error: false, data: [] });
      const res = await api.users();
      const resdata = await res.json();
      setUsers({ loading: false, error: false, data: resdata.users });
    } catch (error) {
      setUsers((prev) => ({ ...prev, loading: false, error: true }));
      console.log(error.message);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    const username = formRef.current.username.value;
    const password = formRef.current.password.value;
    const res = await api.register(username, password);
    const data = await res.json();

    if (res.status === 200) {
      formRef.current.reset();
      setErrorMessage("");
    } else {
      setErrorMessage(data.error);
    }
    fetchData();
    handleClose();
  };

  const deleteUser = async (id) => {
    Swal.fire({
      title: "Are you sure?",
      text: "You will not be able to recover this user!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes, delete it!",
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          const res = await api.deleteUser(id);
          const data = await res.json();
          if (res.status === 200) {
            setUsers((prev) => ({
              ...prev,
              data: prev.data.filter((el) => el._id !== id),
            }));
            Swal.fire("Deleted!", "User has been deleted.", "success");
            fetchData();
          } else {
            Swal.fire("Error!", data.error, "error");
          }
        } catch (error) {
          console.log(error.message);
        }
      }
    });
  };

  const filterData = (data) => {
    if (
      (!filters.hasOwnProperty("search") || filters.search === "") &&
      (!filters.hasOwnProperty("userName") || filters.userName === "") &&
      (!checkBoxFilters || checkBoxFilters.length === 0) &&
      (!startDate || !endDate)
    )
      return data;
    let temp = [];
    if (filters.hasOwnProperty("userName") && filters.userName)
      temp = [
        ...temp,
        ...data.filter((el) =>
          el.userName.toLowerCase().includes(filters.userName.toLowerCase())
        ),
      ];

    if (filters.hasOwnProperty("search") && filters.search)
      temp = [
        ...temp,
        ...data.filter(
          (el) =>
            el.email.toLowerCase().includes(filters.search.toLowerCase()) ||
            el.userName.toLowerCase().includes(filters.search.toLowerCase()) ||
            el.group.toLowerCase().includes(filters.search.toLowerCase()) ||
            el.status.toLowerCase().includes(filters.search.toLowerCase())
        ),
      ];

    if (checkBoxFilters && checkBoxFilters.length > 0) {
      console.log(data[0].status);
      temp = [
        ...temp,
        ...data.filter((el) =>
          checkBoxFilters.includes(el.status.toLowerCase())
        ),
      ];
      console.log("after check box", temp);
    }

    if (startDate && endDate)
      temp = [
        ...temp,
        ...data.filter((el) =>
          moment(el.createdOn).isBetween(moment(startDate), moment(endDate))
        ),
      ];

    console.log(temp);
    return temp;
  };
  return (
    <>
      {users.loading ? (
        <Spinner animation="grow" variant="dark" />
      ) : users.error ? (
        <Alert variant="danger"> Error while loading data </Alert>
      ) : (
        <>
          <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
              <Modal.Title>Add New User</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <Form onSubmit={handleAddUser} ref={formRef}>
                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold"> Name</Form.Label>
                  <Form.Control
                    required
                    placeholder="Enter username"
                    type="text"
                    name="username"
                    variant="success"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label className="fw-bold"> Password</Form.Label>
                  <Form.Control
                    required
                    placeholder="Enter Password"
                    type="password"
                    name="password"
                  />
                </Form.Group>

                {errorMessage && (
                  <Alert
                    variant="danger"
                    dismissible
                    onClose={() => setErrorMessage("")}
                  >
                    {errorMessage}
                  </Alert>
                )}
              </Form>
            </Modal.Body>
            <Modal.Footer>
              <Button
                variant="outline-secondary"
                className="me-auto"
                onClick={(e) => {
                  formRef.current.reset();
                  setErrorMessage("");
                }}
              >
                Reset feilds
              </Button>
              <Button variant="danger" onClick={handleClose}>
                Cancel
              </Button>
              <Button variant="success" onClick={handleAddUser}>
                Add User
              </Button>
            </Modal.Footer>
          </Modal>

          <Table striped bordered hover responsive variant="dark" className="mb-0">
            <thead>
              <tr>
                <th>ID</th>
                <th>User Name</th>
                <th>Rol</th>
                <th>
                  Preguntas
                </th>
                <th>Borrar</th>
              </tr>
            </thead>
            <tbody>
              {users.data &&
                filterData(users.data).map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.username}</td>
                    <td>{user.id === 1 ? "Admin" : "User"}</td>
                    <td>{user.questions}</td>
                    <td>
                      {user.id === 1 ? (
                        <i class="fa-solid fa-ban"></i>
                      ) : (
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={(e) => deleteUser(user.id)}
                        >
                          <i className="fas fa-trash-alt"></i>
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
            </tbody>
          </Table>
        </>
      )}
    </>
  );
};

export default UsersTable;
