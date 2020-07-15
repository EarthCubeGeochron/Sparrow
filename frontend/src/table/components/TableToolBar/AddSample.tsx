import React, { useState } from "react";
import AddIcon from "@material-ui/icons/Add";
import Button from "@material-ui/core/Button";
import Dialog from "@material-ui/core/Dialog";
import DialogActions from "@material-ui/core/DialogActions";
import DialogContent from "@material-ui/core/DialogContent";
import DialogContentText from "@material-ui/core/DialogContentText";
import DialogTitle from "@material-ui/core/DialogTitle";
import IconButton from "@material-ui/core/IconButton";
import TextField from "@material-ui/core/TextField";
import Tooltip from "@material-ui/core/Tooltip";

const intialSample = {
  name: "",
  id: 0,
  longitude: 0,
  latitude: 0,
  material: "",
  project_name: "",
};

const AddSample = (props) => {
  const { addSampleHandler } = props;
  const [newSample, setNewSample] = useState(intialSample);
  const [open, setOpen] = useState(false);

  const handleOpen = () => {
    setOpen(true);
  };
  const handleClose = () => {
    setOpen(false);
  };

  const handleAdd = (event) => {
    addSampleHandler(newSample);
    setNewSample(intialSample);
    setOpen(false);
  };

  const handleChange = (name) => ({ target: { value } }) => {
    setNewSample({ ...newSample, [name]: value });
  };

  return (
    <div>
      <Tooltip title="Add">
        <IconButton onClick={handleOpen}>
          <AddIcon />
        </IconButton>
      </Tooltip>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add New Sample</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Add samples from your own projects
          </DialogContentText>
          <TextField
            autoFocus
            margin="dense"
            label="Sample Name"
            type="text"
            fullWidth
            value={newSample.name}
            onChange={handleChange("name")}
          />
          <TextField
            autoFocus
            margin="dense"
            label="ID"
            type="text"
            fullWidth
            value={newSample.id}
            onChange={handleChange("id")}
          />
          <TextField
            autoFocus
            margin="dense"
            label="Longitude"
            type="number"
            fullWidth
            value={newSample.longitude}
            onChange={handleChange("longitude")}
          />
          <TextField
            autoFocus
            margin="dense"
            label="Latitude"
            type="number"
            fullWidth
            value={newSample.latitude}
            onChange={handleChange("latitude")}
          />
          <TextField
            autoFocus
            margin="dense"
            label="Material"
            type="text"
            fullWidth
            value={newSample.material}
            onChange={handleChange("material")}
          />
          <TextField
            autoFocus
            margin="dense"
            label="Project Title"
            type="text"
            fullWidth
            value={newSample.project_name}
            onChange={handleChange("project_name")}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Cancel
          </Button>
          <Button onClick={handleAdd} color="primary">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default AddSample;
