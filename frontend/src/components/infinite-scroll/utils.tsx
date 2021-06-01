import { useEffect, useState } from "react";
import h from "@macrostrat/hyper";
import { NonIdealState } from "@blueprintjs/core";

export function Expired(props) {
  const { child, secondChild = h(NoSearchResults), delay } = props;
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setVisible(false);
    }, delay);
  }, [delay]);

  return visible ? child : secondChild;
}

export function NoSearchResults() {
  const description = h("div", [
    "Your search didn't match any files",
    h("br"),
    "Try searching for something else"
  ]);
  return h(NonIdealState, {
    icon: "search",
    title: "No Search Results",
    description
  });
}

/**
 *
 * @param options: [rootMargin, Threshold] @param rootMargin : Margin around the root. Can have values similar to the CSS margin property, e.g. "10px 20px 30px 40px" (top, right, bottom, left). The values can be percentages. This set of values serves to grow or shrink each side of the root element's bounding box before computing intersections. Defaults to all zeros.
 * @example const [ref, visible] = useOnScreen({rootMargin: '300px'})
 *
 * @param  threshold: Either a single number or an array of numbers which indicate at what percentage of the target's visibility the observer's callback should be executed. If you only want to detect when visibility passes the 50% mark, you can use a value of 0.5. If you want the callback to run every time visibility passes another 25%, you would specify the array [0, 0.25, 0.5, 0.75, 1]. The default is 0 (meaning as soon as even one pixel is visible, the callback will be run). A value of 1.0 means that the threshold isn't considered passed until every pixel is visible.
 * @example const [ref, visible] = useOnScreen({threshold: 1})
 *
 */
export function useOnScreen() {
  const [ref, setRef] = useState(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setVisible(entry.isIntersecting);
      },
      { rootMargin: "700px 0px 0px 0px" }
    );

    if (ref) {
      observer.observe(ref);
    }
    return () => {
      if (ref) {
        observer.unobserve(ref);
      }
    };
  }, [ref]);
  return [setRef, visible];
}
