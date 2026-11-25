import h from "@macrostrat/hyper";
import { Component } from "react";
import { InputGroup, Menu, Popover, Button, Position } from "@blueprintjs/core";
import { PagedAPIView } from "@macrostrat/ui-components";
import update from "immutability-helper";
import T from "prop-types";
import { useAuth } from "~/auth/context";

class FilterListComponent extends Component<any, any> {
  static propTypes = {
    route: T.string.isRequired,
    filterFields: T.objectOf(T.string).isRequired,
    itemComponent: T.elementType.isRequired,
  };
  constructor(props) {
    super(props);
    this.updateFilter = this.updateFilter.bind(this);
    this.state = {
      filter: "",
      field: Object.keys(this.props.filterFields)[0],
      isSelecting: false,
    };
  }

  updateFilter(event) {
    const { value } = event.target;
    return this.setState(update(this.state, { filter: { $set: value } }));
  }

  render() {
    const {
      route,
      filterFields,
      itemComponent,
      params: baseParams = {},
      ...rest
    } = this.props;
    const { filter, field } = this.state;
    let params = baseParams;
    if (filter != null && filter !== "") {
      const val = `ilike.*${filter}*`;
      params = { ...baseParams, [field]: val };
    }

    const menuItems = [];
    const onClick = (k) => () =>
      this.setState(
        update(this.state, {
          field: { $set: k },
          filter: { $set: "" },
        })
      );

    for (let k in filterFields) {
      const v = filterFields[k];
      menuItems.push(h(Button, { minimal: true, onClick: onClick(k) }, v));
    }

    const content = h(Menu, menuItems);
    const position = Position.BOTTOM_RIGHT;

    const rightElement = h(Popover, { content, position }, [
      h(
        Button,
        { minimal: true, rightIcon: "caret-down" },
        filterFields[field]
      ),
    ]);

    const filterBox = h(InputGroup, {
      leftIcon: "search",
      placeholder: "Filter values",
      value: this.state.filter,
      onChange: this.updateFilter,
      rightElement,
    });

    return h(
      PagedAPIView,
      {
        className: "data-frame",
        extraPagination: filterBox,
        params,
        route,
        topPagination: true,
        bottomPagination: true,
        perPage: 10,
        ...rest,
      },
      (data) =>
        h(
          "div",
          null,
          data.map((d) => h(itemComponent, d))
        )
    );
  }
}

function PostgRESTFilterList(props) {
  const { token } = useAuth();
  return h(FilterListComponent, {
    // Reload when the user signs in or out, which changes what is visible
    key: token ?? "public",
    getTotalCount: (response) => {
      const range = response.headers["content-range"] ?? "";
      return parseInt(range.split("/")[1]);
    },
    opts: {
      headers: {
        Prefer: "count=exact",
      },
    },
    ...props,
  });
}

export { FilterListComponent, PostgRESTFilterList };
