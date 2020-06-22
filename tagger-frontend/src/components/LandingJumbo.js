import React, { useState, useEffect, useReducer } from "react";

const LandingJumbo = () => {
  return (
    <div className="jumbotron">
      <h1 className="display-4">Tagger</h1>
      <p className="lead">
          A smart assitant to organise your handwritten notes
      </p>
      <hr className="my-4"></hr>
      <p>
  Tagger allows you to organise and sync your notes based on user defined tags 
      </p>
          <p className="lead">
        <div className="row">
        <GoogleButton/>
        <a className="btn btn-primary btn-lg col-sm-4 m-2" href="#" role="button">
          Learn more
        </a>

        </div>
      </p>
    </div>
  );
};


const GoogleButton  = () => {
    return (
<a id="google-button" class="btn btn-lg btn-social btn-google text-white col-sm-5 m-2" href="/login">
  <i class="fa fa-google text-white"></i> Sign in with Google
</a>
    );
  };

export default LandingJumbo;
