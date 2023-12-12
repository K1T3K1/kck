import React, { useState, useEffect } from 'react';
import 'react-toastify/dist/ReactToastify.css';
import { ToastContainer, toast } from 'react-toastify';
import "./AddTodo.scss"


const AddTodo = () => {
  const [name, setName] = useState('');
  const [deadline, setDeadline] = useState('');
  const [description, setDescription] = useState('');

  const showError = () => {
    console.log('Błąd podczas dodawania zadania.');
    toast.error('Błąd podczas dodawania zadania.', {
      position: "top-right",
      autoClose: 5000,
      closeOnClick: true,
      theme: "dark",
    });
  };

  const showSuccess = () => {
    toast.success('Dodano zadanie.', {
      position: "top-right",
      autoClose: 5000,
      closeOnClick: true,
      theme: "dark"
    })
  }

  const addTodo = () => {
    // Utwórz URL z danymi
    const url = `http://localhost:8000/todo/?name=${encodeURIComponent(name)}&description=${encodeURIComponent(description)}&deadline=${deadline}&status=To%20do`;

    // Wyślij żądanie POST na endpoint
    fetch(url, {
      method: 'POST',
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
        console.log('Dodano nowe zadanie:', data);
        showSuccess();
      })
      .catch(errorCode => showError());
  };

  return (
    <div>
      <h1>Dodaj zadanie</h1>
      <ToastContainer />
      <div className="formContainer">
        <div className="addForm">
          <label htmlFor="name">Nazwa: </label>
          <input
            type="text"
            id="name"
            name="name"
            value={name}
            onChange={e => setName(e.target.value)}
            required
          />
          <br />

          <label htmlFor="deadline">Termin ostateczny: </label>
          <input
            type="datetime-local"
            id="deadline"
            name="deadline"
            value={deadline}
            onChange={e => setDeadline(e.target.value)}
            required
          />
          <br />

          <label htmlFor="description">Opis: </label>
          <br />
          <textarea
            id="description"
            name="description"
            value={description}
            onChange={e => setDescription(e.target.value)}
            rows="4"
            cols="50"
            required
          ></textarea>
          <br />

          <button className="addButton" onClick={addTodo}>
            Dodaj zadanie
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddTodo;
