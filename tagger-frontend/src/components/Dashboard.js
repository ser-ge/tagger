import React, { useState, useEffect, Fragment } from 'react';

const Dashboard = ({ user }) => {

    const [folders, setFolders] = useState([
        {'id': '1234', 'name': 'NeoNotesPDF', 'timeSynced': 'today'},
    ])

    const setIsWatched = (folderId) => {
        return
    }
    return (
        <Fragment>
        <div class="container">
            <Folders title={"Google Drive"} folders={folders} />
                            <Folders title={"Evernote"} folders={folders} />
        </div >


        </Fragment>
    )
}



const Folders = ({title, folders, setIsWatched}) => {
    return (

            <div class="my-3 p-3 bg-white rounded shadow-sm">
                <h6 class="border-bottom border-gray pb-2 mb-0">{title}</h6>
                    {folders.map((folder)=> (<Folder setIsWatched={setIsWatched} folder={folder}/>))}
                        <small class="d-block text-right mt-3">
                </small>
            </div>
    )
}


// isWatched, destinations


const Folder = ({folder}) =>{

    const {name, timeSynced, isWatched, setIsWatched} = folder
    return (
                <div class="media text-muted pt-3">
                    <h2 className="d-flex mr-3">
                <i class="far fa-folder  "></i></h2>
                    <p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
                        <strong class="d-block text-gray-dark">{name}</strong>
                            <em>last synced: {timeSynced}</em>

                            <div class="btn-group float-right" role="group" aria-label="Basic example">
  <button type="button" class="btn btn-secondary">Unlink Folder</button>
  <button type="button" class="btn btn-secondary">Link New </button>
  <button type="button" class="btn btn-secondary">Sync</button>
</div>
            </p>

          </div>
)
}

// https://gitbrent.github.io/bootstrap4-toggle/
export default Dashboard
