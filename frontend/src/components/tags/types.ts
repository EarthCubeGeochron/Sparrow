interface tagBody {
  name: string;
  description: string;
  color: string;
  onClickDelete?: (e) => void;
  id?: number;
  disabled?: boolean;
  isEditing?: boolean;
}

enum tag_reducer {
  NAME,
  DESCRIPTION,
  HEX_COLOR,
}

export { tagBody, tag_reducer };
