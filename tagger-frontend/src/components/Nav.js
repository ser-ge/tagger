import React, { useState, useEffect, useReducer } from "react";
import {Link} from "react-router-dom"

const Nav = ({user}) => {
  return (
    <nav class="vw-100 navbar navbar-expand-lg navbar-light bg-white justify-content-between">
      <a class="navbar-brand " href="#">
        Tagger
      </a>
      <button
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarNavAltMarkup"
        aria-controls="navbarNavAltMarkup"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse justify-content-end" id="navbarNavAltMarkup">
        <div class="navbar-nav ">
          <Link className="nav-item nav-link active" to="/dashboard">Dashboard</Link>
          <a class="nav-item nav-link active" href="/sync">
            Sync <span class="sr-only">(current)</span>
          </a>
          <a class="nav-item nav-link" href="/logout">
            Logout
          </a>
          <a class="nav-item nav-link" href="/login">
            Login
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Nav;
