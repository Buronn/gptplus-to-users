import React, { useState, useEffect, useRef } from "react";
import * as api from "../utils/api.jsx";
import "./home.css";
import ReactMarkdown from "react-markdown";
import remarkCodeFrontmatter from "remark-code-frontmatter";
import hljs from "highlight.js";
import Swal from "sweetalert2";

const Home = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [chatList, setChatList] = useState([]);
  const [messages, setMessages] = useState([]);
  const [title, setTitle] = useState("Escoge una conversación");
  const [conversationID, setConversationId] = useState("");
  const [user, setUser] = useState(localStorage.getItem("username"));

  useEffect(() => {
    const checkLogin = async () => {
      const res = await api.checkLogin();
      if (res.status === 200) {
        setLoggedIn(true);
        const res = await api.getConversations();
        const data = await res.json();
        if (data.items) {
          for (let i = 0; i < data.items.length; i++) {
            if (data.items[i].title === null) {
              data.items[i].title = "Untitled";
            }
          }
          setChatList(data.items);
        }
      } else {
        window.location.href = "/";
      }
    };

    checkLogin();
  }, []);

  const getMessages = async (conversationId) => {
    const res = await api.getMessages(conversationId);
    const data = await res.json();
    // Obtener todos los objetos con "d-flex align-items-center"
    const elements = document.getElementsByClassName(
      "d-flex align-items-center"
    );
    // Recorrer todos los elementos y cambiar el color de fondo a blanco
    for (let i = 0; i < elements.length; i++) {
      elements[i].style.backgroundColor = "#444654";
    }
    if (data) {
      const temp_messages = [];
      const temp = data.messages;
      setConversationId(conversationId);

      for (const key in temp) {
        try {
          if (temp[key].date) {
            if (temp[key].content.length > 0) {
              temp_messages.push(temp[key]);
            }
          }
        } catch (e) {
          continue;
        }
      }

      // Define una función de comparación para usar en la función sort()
      function compare(a, b) {
        // Si a y b no tienen date, retornar 0 para mantener el orden original
        if (!a.date && !b.date) {
          return 0;
        } else if (!a.date) {
          // Si a no tiene date, ponerlo al final
          return 1;
        } else if (!b.date) {
          // Si b no tiene date, ponerlo al final
          return -1;
        } else {
          // Comparar por date
          const dateA = new Date(a.date);
          const dateB = new Date(b.date);
          return dateA - dateB;
        }
      }

      // Ordena el array
      temp_messages.sort(compare);

      setMessages(temp_messages);
      setTitle(data.title);
      document.getElementById(conversationId).style.backgroundColor = "#272830";
      hljs.highlightAll();
      // Highlight code dark mode
      const codeBlocks = document.querySelectorAll("pre code");
      codeBlocks.forEach((block) => {
        hljs.highlightBlock(block);
      });
    }
  };

  const handleClick = async (event) => {
    event.preventDefault();

    const inputElement = event.target.form.elements[0];
    const messageContent = inputElement.value;

    const textarea = document.getElementById("send_message");
    const buttonElement = document.getElementById("send_button");
    buttonElement.disabled = true;
    textarea.disabled = true;
    textarea.style.backgroundColor = "#202127";
    textarea.placeholder = "Sending...";

    buttonElement.innerHTML = `
        <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Sending...
        `;

    const lastMessage = messages[messages.length - 1];
    const lastMessageId = lastMessage ? lastMessage.id : null;

    const res = await api.sendMessage(
      conversationID,
      lastMessageId,
      messageContent
    );
    if (res.status === 200) {
      inputElement.value = "";
      getMessages(conversationID);

      // Desbloquear el botón de enviar
      buttonElement.disabled = false;
      buttonElement.innerHTML = `
            <span class="fa fa-paper-plane" role="status" aria-hidden="true"></span>
            
            `;

      // Desbloquear el textarea
      textarea.disabled = false;
      textarea.style.backgroundColor = "#40414f";
      textarea.placeholder = "Type your message here...";
    } else {
      Swal.fire({
        icon: "error",
        title: "Oops...",
        text: "Something went wrong!",
      });
    }
    // Scroll at the bottom
  };

  const newConversation = (event) => {
    Swal.fire({
      title: "Create a new conversation",
      input: "text",
      inputAttributes: {
        autocapitalize: "off",
      },
      showCancelButton: true,
      confirmButtonText: "Create",
      showLoaderOnConfirm: true,
      preConfirm: async (conversationName) => {
        const res = await api.createConversation(conversationName);
        if (res.status === 200) {
          lastConversation();
        }
      },
      allowOutsideClick: () => !Swal.isLoading(),
    });
  };

  const DeleteConversation = async () => {
    Swal.fire({
      title: "¿Estás seguro?",
      text: "No podrás revertir esto!",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Sí, bórralo!",
    }).then(async (result) => {
      if (result.isConfirmed) {
        const res = await api.deleteConversation(conversationID);
        if (res.status === 200) {
          lastConversation();
        }
      }
    });
  };

  const ChangeTitle = async () => {
    Swal.fire({
      title: "Cambiar título de la conversación",
      input: "text",
      inputAttributes: {
        autocapitalize: "off",
      },
      showCancelButton: true,
      confirmButtonText: "Cambiar",
      showLoaderOnConfirm: true,
      preConfirm: async (conversationName) => {
        const res = await api.changeTitle(conversationID, conversationName);
        if (res.status === 200) {
          const res2 = await api.getConversations();
          const data2 = await res2.json();
          if (data2.items) {
            setChatList(data2.items);
            getMessages(conversationID);
          }
        }
      },
      allowOutsideClick: () => !Swal.isLoading(),
    });
  };

  const lastConversation = async () => {
    const res2 = await api.getConversations();
    const data2 = await res2.json();
    if (data2.items) {
      for (let i = 0; i < data2.items.length; i++) {
        if (data2.items[i].title === null) {
          data2.items[i].title = "Untitled";
        }
      }
      setChatList(data2.items);
      getMessages(data2.items[0].id);
    }
  };

  return (
    <div>
      {loggedIn ? (
        // Si loggedIn es verdadero, mostrar el chat
        <section className="message-area">
          <div className="container">
            <div className="row">
              <div className="col-12">
                <div className="chat-area">
                  <div className="chatlist">
                    <div className="modal-dialog-scrollable">
                      <div className="modal-content">
                        <div className="chat-header">
                          <div className="msg-search">
                            <input
                              type="text"
                              className="form-control"
                              id="inlineFormInputGroup"
                              placeholder="Search"
                              aria-label="search"
                            ></input>
                            <a
                              className="add"
                              href="#"
                              onClick={() => {
                                newConversation();
                              }}
                            >
                              <i class="fa-solid fa-square-plus"></i>
                            </a>
                          </div>

                          <ul
                            className="nav nav-tabs"
                            id="myTab"
                            role="tablist"
                          >
                            <li className="nav-item" role="presentation">
                              <button
                                className="nav-link active"
                                id="Open-tab"
                                data-bs-toggle="tab"
                                data-bs-target="#Open"
                                type="button"
                                role="tab"
                                aria-controls="Open"
                                aria-selected="true"
                              >
                                Chats
                              </button>
                            </li>
                          </ul>
                        </div>

                        <div className="modal-body">
                          <div className="chat-lists">
                            <div className="tab-content" id="myTabContent">
                              <div
                                className="tab-pane fade show active"
                                id="Open"
                                role="tabpanel"
                                aria-labelledby="Open-tab"
                              >
                                <div className="chat-list">
                                  {chatList.map((chat) => (
                                    <a
                                      id={chat.id}
                                      href="#"
                                      className="d-flex align-items-center"
                                      onClick={() => {
                                        getMessages(chat.id);
                                        getMessages(chat.id);
                                      }}
                                    >
                                      <div className="flex-shrink-0"></div>
                                      <div className="flex-grow-1 ms-3">
                                        <h3>{chat.title}</h3>
                                      </div>
                                    </a>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="logout">
                          <a
                            href="#"
                            onClick={() => {
                              api.logout();
                              setLoggedIn(false);
                              window.location.reload();
                            }}
                          >
                            <i class="fa-solid fa-sign-out"></i> &nbsp;Logout
                          </a>
                          <div>&nbsp;&nbsp;&nbsp;</div>
                          <a
                            href="#"
                            onClick={() => {
                              if (user === "admin") {
                                window.location.href = "/admin";
                              } else {
                                Swal.fire({
                                  title: "Change Password",
                                  html: `
                                                                                        <input id="swal-input1" class="swal2-input" type="password" placeholder="Current Password">
                                                                                        <input id="swal-input2" class="swal2-input" type="password" placeholder="New Password">
                                                                                        <input id="swal-input3" class="swal2-input" type="password" placeholder="Confirm New Password">
                                                                                    `,
                                  focusConfirm: false,
                                  preConfirm: () => {
                                    const currentPassword =
                                      document.getElementById(
                                        "swal-input1"
                                      ).value;
                                    const newPassword =
                                      document.getElementById(
                                        "swal-input2"
                                      ).value;
                                    const confirmNewPassword =
                                      document.getElementById(
                                        "swal-input3"
                                      ).value;

                                    // Validar que los campos no estén vacíos
                                    if (
                                      !currentPassword ||
                                      !newPassword ||
                                      !confirmNewPassword
                                    ) {
                                      Swal.showValidationMessage(
                                        "All fields are required"
                                      );
                                    }

                                    // Validar que la nueva contraseña y la confirmación coincidan
                                    if (newPassword !== confirmNewPassword) {
                                      Swal.showValidationMessage(
                                        "New password and confirmation do not match"
                                      );
                                    }

                                    return api
                                      .changePassword(
                                        currentPassword,
                                        newPassword
                                      )
                                      .then((res) => {
                                        if (res.status === 200) {
                                          Swal.fire({
                                            icon: "success",
                                            title:
                                              "Password changed successfully",
                                            showConfirmButton: false,
                                            timer: 1500,
                                          });
                                        } else {
                                          Swal.showValidationMessage(
                                            "Current password is incorrect"
                                          );
                                        }
                                      })
                                      .catch((error) => {
                                        console.log(error);
                                      });
                                  },
                                });
                              }
                            }}
                          >
                            <i class="fa-solid fa-key"></i> &nbsp;{user}
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>

                  {conversationID !== "" ? (
                    <div className="chatbox">
                      <div className="modal-dialog-scrollable">
                        <div className="modal-content">
                          <div className="msg-head">
                            <div className="row">
                              <div className="col-8">
                                <div className="d-flex align-items-center">
                                  <span className="chat-icon">
                                    <img
                                      className="img-fluid"
                                      src="https://mehedihtml.com/chatbox/assets/img/arroleftt.svg"
                                      alt="image title"
                                    ></img>
                                  </span>
                                  <div className="flex-shrink-0"></div>
                                  <div className="flex-grow-1 ms-3">
                                    <h3>
                                      &nbsp; &nbsp; &nbsp; {title}{" "}
                                      <a
                                        href="#"
                                        onClick={() => {
                                          ChangeTitle();
                                        }}
                                      >
                                        <i
                                          className="fa fa-pencil"
                                          aria-hidden="true"
                                        ></i>
                                      </a>
                                    </h3>
                                  </div>
                                </div>
                              </div>
                              <div className="col-4">
                                <ul className="moreoption">
                                  <li className="navbar nav-item dropdown">
                                    <a
                                      className="nav-link dropdown-toggle"
                                      href="#"
                                      role="button"
                                      data-bs-toggle="dropdown"
                                      aria-expanded="false"
                                      onClick={() => {
                                        DeleteConversation();
                                      }}
                                    >
                                      <i
                                        className="fa fa-trash"
                                        aria-hidden="true"
                                      ></i>
                                    </a>
                                  </li>
                                </ul>
                              </div>
                            </div>
                          </div>
                          <div className="modal-body">
                            <div className="msg-body">
                              <ul>
                                {messages &&
                                  messages.map((item) => {
                                    try {
                                      const role = item.role;
                                      const content = item.content.replace(
                                        /\n- /g,
                                        "\n\n• "
                                      );

                                      const date = new Date(item.date);
                                      const options = {
                                        day: "numeric", // muestra el día del mes en números (p.ej. 1-31)
                                        month: "short", // muestra el mes en formato abreviado (p.ej. Jan, Feb, etc.)
                                        hour: "numeric", // muestra la hora en formato de 12 horas sin los minutos
                                        minute: "numeric", // muestra los minutos
                                        hour12: true, // usa el formato de 12 horas con AM/PM
                                        hourCycle: "h12", // se asegura que se use el ciclo de 12 horas
                                      };

                                      const formatter = new Intl.DateTimeFormat(
                                        "es-ES",
                                        options
                                      ); // crea un formateador de fecha y hora
                                      const formattedDate =
                                        formatter.format(date); // aplica el formateo
                                      const className =
                                        role === "user" ? "repaly" : "sender";

                                      return (
                                        <li id={item.id} className={className}>
                                          <p>
                                            <ReactMarkdown
                                              remarkPlugins={[
                                                remarkCodeFrontmatter,
                                              ]}
                                            >
                                              {content}
                                            </ReactMarkdown>
                                          </p>
                                          <span className="time">
                                            {formattedDate}
                                          </span>
                                        </li>
                                      );
                                    } catch (error) {
                                      console.log(`Error: ${error.message}`);
                                      return null;
                                    }
                                  })}
                                <li></li>
                              </ul>
                            </div>
                          </div>
                          <div className="send-box">
                            <form>
                              <textarea
                                id="send_message"
                                type="text"
                                className="form-control"
                                aria-label="message…"
                                placeholder="Type your message here..."
                                onKeyDown={(event) => {
                                  if (event.key === "Enter" && event.shiftKey) {
                                    event.preventDefault();
                                    // Añadir "\n" en la posición actual de la persona que escribe
                                    const textarea =
                                      document.getElementById("send_message");
                                    const start = textarea.selectionStart;
                                    const end = textarea.selectionEnd;
                                    const value = textarea.value;
                                    const before = value.substring(0, start);
                                    const after = value.substring(end);
                                    textarea.value = before + "\n" + after;
                                    textarea.selectionStart =
                                      textarea.selectionEnd = start + 1;
                                  } else if (event.key === "Enter") {
                                    event.preventDefault();
                                    // Si está vacío, no envíe nada
                                    if (event.target.value === "") {
                                      return;
                                    }
                                    handleClick(event);
                                  }
                                }}
                              />
                              <button
                                id="send_button"
                                type="button"
                                onClick={handleClick}
                              >
                                <span className="fa fa-paper-plane"></span>
                              </button>
                            </form>
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="chatbox">
                      <div className="modal-dialog-scrollable">
                        <div className="modal-content">
                          <div className="msg-head">
                            <div className="row">
                              <div className="col-8">
                                <div className="d-flex align-items-center">
                                  <span className="chat-icon">
                                    <img
                                      className="img-fluid"
                                      src="https://mehedihtml.com/chatbox/assets/img/arroleftt.svg"
                                      alt="image title"
                                    ></img>
                                  </span>
                                  <div className="flex-shrink-0"></div>
                                  <div className="flex-grow-1 ms-3">
                                    <h3>
                                      &nbsp; &nbsp; &nbsp; Abre o crea una
                                      conversación
                                    </h3>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="modal-body">
                            <div className="msg-body"></div>
                          </div>
                          <div className="send-box"></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      ) : (
        // Si loggedIn es falso, el usuario será redirigido a la página de inicio de sesión
        <div className="loading">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
