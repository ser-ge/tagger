import React, {useState, useEffect} from 'react';
import logo from './logo.svg';
import { makeStyles } from '@material-ui/core/styles'

import './App.css';
import Container from '@material-ui/core/Container'
import {Box, Link} from '@material-ui/core/'

const useStyles  = makeStyles({
    inner: {
        minHeight: '70vh',
        minWidth: '85%',
        alignSelf: 'centre'
    },

    outer: {
        minHeight: '90vh',
        paddingTop:'5vh',
        minWidth: '90vw'
    }
})
function App() {
    const classes = useStyles()
    const [user, setUser] = useState('No User')

    useEffect(()=> {
        loadData();
    });

    const loadData = async () => {
        const response = await fetch('/user');
        const data = await response.json()
        setUser(data.name)
    }
    return (
        <Container className={classes.outer} maxWidth="sm">
            <Box className={classes.inner}>
                <Link href='/login'> Login </Link>
                <Link href='/logout'> Logout </Link>
                <div>{user}</div>
                <Link href="/get_evernote_tags"> All tags</Link>
            </Box>
        </Container>
 );
}

export default App;
