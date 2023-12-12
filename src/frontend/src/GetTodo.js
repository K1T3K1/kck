// TodoList.js
import React, { useState, useEffect } from 'react';
import './GetTodo.scss'
import 'react-toastify/dist/ReactToastify.css';
import { ToastContainer, toast } from 'react-toastify';

const GetTodo = () => {
  const [todos, setTodos] = useState([]);
  const [editTodoId, setEditTodoId] = useState(null);
  const [editTodoName, setEditTodoName] = useState('');
  const [editTodoDescription, setEditTodoDescription] = useState('');
  const [editTodoDeadline, setEditTodoDeadline] = useState('');
  const [editTodoStatus, setEditTodoStatus] = useState('');

  const transformApiDate = (apiDate) => {
    const apiDateObject = new Date(apiDate);
    const year = apiDateObject.getFullYear();
    const month = (`0${apiDateObject.getMonth() + 1}`).slice(-2);
    const day = (`0${apiDateObject.getDate()}`).slice(-2);
    const hours = (`0${apiDateObject.getHours()}`).slice(-2);
    const minutes = (`0${apiDateObject.getMinutes()}`).slice(-2);

    // Zwróć datę w formacie zgodnym z inputem "datetime-local"
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const getTodos = () => {
    fetch('http://localhost:8000/todo/')
      .then(response => {
        if (!response.ok) {
          throw new Error(response.status)
        }
        return response.json()
      })
      .then(data => setTodos(data))
      .catch(error => showError());
  }
  const statusOptions = ["To do", "Done"];
  const statuses = {
    0: "To do",
    1: "Done"
  }

  const changeStatus = (id, name, description, deadline, status) => {
    console.log("Changing status")
    console.log(`${id} | ${name} | ${description} | ${deadline} | ${status}`)

    if (status === "To do") {
      status = statuses[1];
    } else {
      status = statuses[0];
    }

    deadline = transformApiDate(deadline)
    const url = `http://localhost:8000/todo/${encodeURIComponent(id)}?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}&deadline=${deadline}&status=${status}`;
    fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(response.status);
        }
        return response.json()
      })
      .then(data => {
        console.log('Zaktualizowano zadanie:', data);
        showSuccess();
      })
      .catch(errorCode => editError());

    getTodos();
  }

  const showEditForm = (id, name, description, deadline, status) => {
    console.log(`${id} showing form`)
    setEditTodoId(id);
    setEditTodoName(name);
    setEditTodoDescription(description);
    setEditTodoDeadline(transformApiDate(deadline));
    setEditTodoStatus(status);
  };

  const closeEditForm = () => {
    setEditTodoId(null);
    // Wyczyść też stanów z informacjami o zadaniu
    setEditTodoName('');
    setEditTodoDescription('');
    setEditTodoDeadline('');
    setEditTodoStatus('');
  };

  const showError = () => {
    console.log('Błąd podczas pobierania zadań.');
    toast.error('Błąd podczas pobierania zadań.', {
      position: "top-right",
      autoClose: 5000,
      closeOnClick: true,
      theme: "dark",
    });
  };

  const editError = () => {
    console.log('Błąd podczas edytowania zadania.');
    toast.error('Błąd podczas edytowania zadania.', {
      position: "top-right",
      autoClose: 5000,
      closeOnClick: true,
      theme: "dark",
    });
  };

  const showSuccess = () => {
    toast.success('Zaktualizowano zadanie.', {
      position: "top-right",
      autoClose: 5000,
      closeOnClick: true,
      theme: "dark"
    })
  }

  useEffect(() => {
    fetch('http://localhost:8000/todo/')
      .then(response => {
        if (!response.ok) {
          throw new Error(response.status)
        }
        return response.json()
      })
      .then(data => setTodos(data))
      .catch(error => showError());
    // W tym miejscu wywołaj funkcję pobierającą zadania z endpointa GET
  }, []); // Pusta tablica jako drugi argument, aby efekt wykonał się tylko raz po zamontowaniu komponentu

  const editTodo = () => {
    const url = `http://localhost:8000/todo/${encodeURIComponent(editTodoId)}?name=${encodeURIComponent(editTodoName)}&description=${encodeURIComponent(editTodoDescription)}&deadline=${editTodoDeadline}&status=${editTodoStatus}`;
    fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(response.status);
        }
        return response.json()
      })
      .then(data => {
        console.log('Zaktualizowano zadanie:', data);
        showSuccess();
      })
      .catch(errorCode => editError());
    getTodos();
  }

  return (
    <div>
      <ToastContainer />
      <div className="mainGetBox">
        <div className="todoBox">
          <h1 className="title">Lista zadań</h1>
          <ul>
            {todos.map(todo => (
              <li className="card" key={todo.id}>
                <div>
                  <strong className='todoName'>{todo.name}</strong>
                </div>
                <div className='description'>
                  <h3>
                    Opis
                  </h3>
                  {todo.description}
                </div>
                <div className="deadline">
                  <strong>Termin: </strong>{todo.deadline}
                </div>
                <div className='todoStatus'>
                  <strong>Status: </strong>{todo.status}
                </div>
                <div className="buttonBox">
                  <button onClick={() => showEditForm(todo.id, todo.name, todo.description, todo.deadline, todo.status)}>
                    edytuj
                  </button>
                  <button onClick={() => changeStatus(todo.id, todo.name, todo.description, todo.deadline, todo.status)}>
                    status
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
        {editTodoId !== null && (
          <div className="editBox">
            <h1 className="editTitle">Edytuj zadanie</h1>
            <div className="editForm">
              <form>
                <label>
                  Nazwa zadania:
                  <input
                    type="text"
                    value={editTodoName}
                    onChange={(e) => setEditTodoName(e.target.value)}
                  />
                </label>
                <br />
                <label>
                  Opis zadania:
                  <textarea
                    value={editTodoDescription}
                    onChange={(e) => setEditTodoDescription(e.target.value)}
                  />
                </label>
                <br />
                <label>
                  Deadline:
                  <input
                    type="datetime-local"
                    id="deadline"
                    name="deadline"
                    value={editTodoDeadline}
                    onChange={(e) => setEditTodoDeadline(e.target.value)}
                    required
                  />
                </label>
                <br />
                <label>
                  Status:
                  <select
                    value={editTodoStatus}
                    onChange={(e) => setEditTodoStatus(e.target.value)}
                  >
                    {statusOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>
                <br />
                <button type="button" onClick={editTodo}>
                  Zapisz zmiany
                </button>
                <button type="button" onClick={closeEditForm}>
                  Anuluj
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default GetTodo;
