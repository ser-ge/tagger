import React, {useState, useEffect} from 'react';
import logo from './logo.svg';

import './App.css';

import Nav from './components/Nav'


function App() {

    const [user, setUser] = useState('No User')

    useEffect(()=> {
        loadData();
    },[]);

    const loadData = async () => {
        const response = await fetch('/user');
        const data = await response.json()
        setUser(data.name)
    }
    return (
        <div class="container">
            <Nav/>
            <div >
                <a href='/login'> Login </a>
                <a href='/logout'> Logout </a>
                <div>{user}</div>
                <a href="/get_evernote_tags"> All tags</a>
            </div>
        </div >
 );
}

export default App;
