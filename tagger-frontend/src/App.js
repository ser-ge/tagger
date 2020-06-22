import React, { useState, useEffect, Fragment } from 'react';
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link
} from "react-router-dom";

import './App.css';
import LandingJumbo from './components/LandingJumbo'
import Nav from './components/Nav'

import Dashboard from './components/Dashboard'

function App() {

    const [user, setUser] = useState(false)
    const [mUser, setmUser] = useState({
        name: 'serge',
        auth: true,
        gdriveauth: false,
        evernoteauth: false,
        appconfig: null,
    })

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        const response = await fetch('/user');
        const data = await response.json()
        setUser(data.name)
    }
    return (
        <Fragment>
            <Router>
                <div className="container vh-100">               
                 <Nav user={mUser} />
                    <Switch>
                        <Route path="/home">
                            <LandingJumbo />
                        </Route>
                        <Route path="/dashboard">
                            <Dashboard user={user} />
                        </Route>
                    </Switch>
                </div>

            </Router>
        </Fragment>
    );
}

export default App;
