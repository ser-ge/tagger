import React, { useState, useEffect, useReducer } from 'react';





const Nav = (user) => {



    return (

        <nav>
            <div class="nav-wrapper black">
                <div className="col s1"></div>
                <a href="#!" className="brand-logo white-text centre-align"> tagger</a>
                <ul id="nav-mobile" class="right hide-on-med-and-down">
                    {user.auth ?
                        <li><a className="btn white black-text" href="/login">Login</a></li> :
                        <li><a className="btn white black-text" href="/logout">Logout</a></li>
                    }
                </ul>
            </div>
        </nav>



    );

}



export default Nav

