// EditTodo.js
import React, { useState } from 'react';

const PutTodo = ({ todoId }) => {
  const [name, setName] = useState('');
  const [deadline, setDeadline] = useState('');
  const [description, setDescription] = useState('');

  // Pobierz istniejące zadanie o id `todoId` i ustaw dane początkowe w state

  const editTodo = () => {
    const url = `http://localhost:8000/todo/${todoId}`;
    const data = {
      name,
      description,
      deadline,
      // Możesz dodać więcej pól do edycji, w zależności od potrzeb
    };

    fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(response => response.json())
      .then(updatedTodo => {
        console.log('Zaktualizowano zadanie:', updatedTodo);
        // Dodaj logikę do zaktualizowania stanu lub przekierowania użytkownika
      })
      .catch(error => {
        console.error('Błąd podczas edycji zadania:', error);
      });
  };

  return (
    <div>
      <h1>Formularz Edycji Todo</h1>
      {/* ... (formularz edycji, podobny do poprzednich) */}
      <button type="button" onClick={editTodo}>
        Zapisz zmiany
      </button>
    </div>
  );
};

export default PutTodo;
