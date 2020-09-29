import * as React from "react";
import { useState } from "react";
import { Dialog, Classes, Button } from "@blueprintjs/core";
import {
  SaveButton,
  CancelButton,
  DeleteButton,
} from "@macrostrat/ui-components";

const SubmitDialog = ({ onClick, content, className = null, disabled }) => {
  const [open, setOpen] = useState(false);
  return (
    <div>
      <SaveButton disabled={disabled} onClick={() => setOpen(true)}>
        Save Changes
      </SaveButton>
      <Dialog isOpen={open}>
        <div className={Classes.DIALOG_HEADER}>
          <h3>WARNING</h3>
        </div>
        <div className={Classes.DIALOG_BODY}>
          <p>{content}</p>
        </div>
        <div className={Classes.DIALOG_FOOTER}>
          <SaveButton
            className="save-btn"
            onClick={() => {
              onClick();
              setOpen(false);
            }}
          >
            Save changes
          </SaveButton>
          <CancelButton onClick={() => setOpen(false)}>Cancel</CancelButton>
        </div>
      </Dialog>
    </div>
  );
};

export function SheetHeader(props) {
  const { onSubmit, onUndo, hasChanges } = props;
  var constant =
    "Are you sure you want to save your edits? All changes will be final. If you do not want to submit, click Cancel.";
  return (
    <div className="sheet-header">
      <h3 className="sheet-title">Sample metadata</h3>
      <div className="sheet-actions">
        <SubmitDialog
          className="save-btn"
          onClick={onSubmit}
          content={constant}
          disabled={!hasChanges}
        ></SubmitDialog>
        <Button onClick={onUndo} disabled={!hasChanges}>
          Reset changes
        </Button>
      </div>
    </div>
  );
}
