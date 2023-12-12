// App.js
import React, { useState } from 'react';
import GetTodo from './GetTodo';
import AddTodo from './AddTodo';
import './App.scss';
const App = () => {
  const [showForm, setShowForm] = useState('');

  const showAddForm = () => {
    setShowForm('addForm');
  };

  const showTodos = () => {
    setShowForm('showTodos');
  }

  return (
    <body>
      <div className="mainBox">
        <div className="sidebar">
          <nav className="nav">
            <ul>
              <li><button onClick={showAddForm}> Dodaj zadanie </button></li>
              <li><button onClick={showTodos}> Wyświetl zadania </button></li>
            </ul>
          </nav>
        </div>
        <div className={`content ${showForm}`}>
          {
            {
              'addForm': <AddTodo />,
              'showTodos': <GetTodo />
            }[showForm] || <GetTodo />
          }
        </div>
      </div>
    </body>
  );
};

export default App;
