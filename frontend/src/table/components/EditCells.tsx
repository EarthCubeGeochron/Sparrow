import React from "react";
import Button from "@material-ui/core/Button";

const EditableCell = ({
  value: initialValue,
  row: { index },
  column: { id },
  updateMyData,
  ref: buttonRef,
}) => {
  const [value, setValue] = React.useState(initialValue);

  const onChange = (e) => {
    setValue(e.target.value);
  };

  const onBlur = () => {
    updateMyData(index, id, value);
  };

  React.useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  return (
    <div>
      <input value={value} onChange={onChange} type="text" />
      <button ref={buttonRef} onClick={onBlur}>
        Save
      </button>
    </div>
  );
};

const EditableNumCell = ({
  value: initialValue,
  row: { index },
  column: { id },
  ref: buttonRef,
  updateMyData,
}) => {
  const [value, setValue] = React.useState(initialValue);

  const onChange = (e) => {
    setValue(parseFloat(e.target.value));
  };

  const onBlur = () => {
    updateMyData(index, id, value);
  };

  React.useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  return (
    <div>
      <input value={value} onChange={onChange} type="number" />
      <button ref={buttonRef} onClick={onBlur}>
        Save
      </button>
    </div>
  );
};

export { EditableCell, EditableNumCell };
