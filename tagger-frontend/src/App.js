import React from 'react';
import logo from './logo.svg';
import { makeStyles } from '@material-ui/core/styles'

import './App.css';
import Container from '@material-ui/core/Container'
import Box from '@material-ui/core/Box'

const useStyles  = makeStyles({
    inner: {
        minHeight: '70vh',
        backgroundColor: 'black',
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
    return (
        <Container className={classes.outer} maxWidth="sm">
            <Box className={classes.inner}>
            </Box>
        </Container>
 );
}

export default App;
