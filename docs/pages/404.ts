import BasePage from "components/pages/base";
import h from "@macrostrat/hyper";

const ErrorPage = () => {
  return h(BasePage, [
    h("h1.centered.extra-space", "404 — Page not found"),
    // h("div.mountain-underlay", [
    //   h("div.images", [
    //     h("img", { src: "/img/rear-mountains.png" }),
    //     h("img", { src: "/img/front-mountains.png" }),
    //   ]),
    // ]),
  ]);
};

export default ErrorPage;
