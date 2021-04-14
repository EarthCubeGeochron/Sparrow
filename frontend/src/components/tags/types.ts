interface tagBody {
  name: string;
  description: string;
  color: string;
  id?: number;
}

enum tag_reducer {
  NAME,
  DESCRIPTION,
  HEX_COLOR,
}

export { tagBody, tag_reducer };
